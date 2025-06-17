from datetime import datetime
from threading import Lock
import time

from estado_storage import guardar_estado, obtener_estado_seguro
from interpretador_citas import extraer_fecha_y_hora
from control_antirrepeticion import mensaje_duplicado, registrar_mensaje, bloqueo_activo, activar_bloqueo
from google_sheets_utils import registrar_cita_en_hoja
from respuestas_por_actividad import (
    detectar_actividad,
    obtener_respuesta_por_actividad,
    RESPUESTA_INICIAL,
    FLUJOS_POR_ACTIVIDAD
)
from respuestas_por_actividad import NEGATIVOS_FUERTES
from bot import enviar_mensaje  # Asegúrate que esta importación está activa arriba
from respuestas_por_actividad import clasificar_permiso  # asegúrate de importar
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def formatear_chat_id(numero_base):
    if numero_base.endswith('@c.us'):
        return numero_base
    return f"{numero_base}@c.us"

bloqueos_chat = {}
locks_chat = {}

# Simulación de base de datos en memoria
estado_conversaciones = {}

def enviar_alerta_a_personal(chat_id, mensaje, actividad, etapa, fase, fecha, nombre="(sin nombre)"):
    try:
        # ✅ Asegura que no se duplique el sufijo @c.us
        numero_personal = formatear_chat_id("593984770663")

        from dateutil.parser import parse as parse_fecha
        fecha_obj = fecha if isinstance(fecha, datetime) else parse_fecha(str(fecha))

        texto = (
            f"⚠️ *Cita NO registrada automáticamente*\n"
            f"📞 Cliente: {chat_id.replace('@c.us', '')}\n"
            f"🏷 Actividad: {actividad or '(sin definir)'}\n"
            f"🔄 Etapa/Fase: {etapa} / {fase}\n"
            f"📬 *Mensaje recibido:* _{mensaje}_\n"
            f"🕒 {fecha_obj.strftime('%Y-%m-%d %H:%M')} - Requiere revisión manual."
        )

        logger.debug("📦 JSON a enviar:\nnumero_personal=%s\ntexto=%s", numero_personal, texto)
        enviar_mensaje(numero_personal, texto)
        logger.info("📨 Notificación interna enviada por cita no registrada.")

    except Exception as e:
        logger.warning("⚠️ No se pudo enviar alerta personalizada: %s", e)

def registrar_cita(chat_id, fecha, hora, ubicacion=None):
    logger.info("🗕️ Se registró una cita para %s: {'fecha': '%s', 'hora': '%s', 'ubicacion': '%s'}", chat_id, fecha, hora, ubicacion)

    ubicacion_segura = ubicacion or ""
    modalidad = "Finca" if "finca" in ubicacion_segura.lower() else "Oficina"

    # ✅ Notificar al número personal del Ing. Darwin
    numero_personal = formatear_chat_id("593984770663")
    try:
        registrar_cita_en_hoja(
            contacto=chat_id,
            fecha_cita=fecha,
            hora=hora,
            modalidad=modalidad,
            lugar=ubicacion_segura or "No especificado",
            observaciones=""
        )

        mensaje_interno = (
            f"📢 *Nueva cita registrada:*\n"
            f"📅 *Fecha:* {fecha}\n"
            f"🕒 *Hora:* {hora}\n"
            f"📍 *Lugar:* {ubicacion_segura or 'No especificado'}\n"
            f"📞 *Cliente:* {chat_id.replace('@c.us', '')}\n"
            f"✉️ Mensaje automático para coordinación inmediata."
        )

        logger.debug("📦 Enviando a %s:\n%s", numero_personal, mensaje_interno)
        enviar_mensaje(numero_personal, mensaje_interno)

    except Exception as e:
        logger.error("❌ Error al registrar o notificar cita: %s", e)
        mensaje_falla = (
            f"🚨 *ERROR al guardar o notificar cita*\n"
            f"📞 Cliente: {chat_id.replace('@c.us', '')}\n"
            f"📅 Fecha: {fecha}\n"
            f"🕒 Hora: {hora}\n"
            f"📍 Ubicación: {ubicacion_segura or 'No especificado'}\n"
            f"⚠️ Detalle técnico: {str(e)}"
        )
        enviar_mensaje(numero_personal, mensaje_falla)

def formatear_respuesta(respuesta):
    if isinstance(respuesta, str):
        return respuesta
    if isinstance(respuesta, list):
        return "\n".join(respuesta)
    return str(respuesta)

def determinar_siguiente_etapa(estado_actual, mensaje):
    etapa = estado_actual.get("etapa", "")
    fase = estado_actual.get("fase", "")

    if etapa == "" and fase == "inicio":
        if detectar_actividad(mensaje):
            return "introduccion", "actividad_detectada"
        else:
            return "", "inicio"

    elif etapa == "introduccion":
        clasificacion = clasificar_permiso(mensaje)
        if clasificacion == "si":
            return "permiso_si", "confirmado"
        elif clasificacion == "no":
            return "permiso_no", "confirmado"
        elif clasificacion == "mencion":
            return "aclaracion_introduccion", fase
        else:
            return "introduccion", fase

    elif etapa == "aclaracion_introduccion":
        clasificacion = clasificar_permiso(mensaje)
        if clasificacion == "si":
            return "permiso_si", "confirmado"
        elif clasificacion == "no":
            return "permiso_no", "confirmado"
        elif clasificacion == "mencion":
            return "aclaracion_introduccion", fase
        else:
            return "aclaracion_introduccion", fase
    
    elif etapa == "permiso_si":
        clasificacion = clasificar_permiso(mensaje)
        if clasificacion == "si":
            return "cierre", "esperando_cita"
        elif clasificacion == "no":
            return "permiso_no", "confirmado"
        elif clasificacion == "mencion":
            return "aclaracion_permiso_si", "esperando_cita"
        else:
            return "aclaracion_permiso_si", "esperando_cita"
    
    elif etapa == "permiso_no":
        clasificacion = clasificar_permiso(mensaje)
        if clasificacion == "no":
            return "cierre", "esperando_cita"
        elif clasificacion == "si":
            return "permiso_si", "confirmado"
        elif clasificacion == "mencion":
            return "aclaracion_permiso_no", "esperando_cita"
        else:
            return "aclaracion_permiso_no", "esperando_cita"
 
    elif etapa == "aclaracion_permiso_no":
        clasificacion = clasificar_permiso(mensaje)
        if clasificacion == "no":
            return "permiso_no", "confirmado"
        elif clasificacion == "si":
            return "cierre", "esperando_cita"
        elif any(x in mensaje.lower() for x in ["agenda", "visita", "quiero", "cita", "coordinar"]):
            return "cierre", "esperando_cita"
        else:
            return "aclaracion_permiso_no", "esperando_cita"

    elif etapa == "cierre":
        if extraer_fecha_y_hora(mensaje):
            return "agradecimiento", "cita_registrada"
        else:
            return "aclaracion_cierre", "esperando_cita"

    elif etapa == "aclaracion_cierre":
        if extraer_fecha_y_hora(mensaje):
            return "agradecimiento", "cita_registrada"
        else:
            return "aclaracion_cierre", "esperando_cita"

    elif etapa == "agradecimiento":
        return "agradecimiento", "cita_registrada"

    return etapa, fase

def esta_bloqueado(chat_id):
    ahora = time.time()
    expiracion = bloqueos_chat.get(chat_id, 0)
    return ahora < expiracion

def bloquear_chat(chat_id, segundos=1.5):
    bloqueos_chat[chat_id] = time.time() + segundos
    if chat_id not in locks_chat:
        locks_chat[chat_id] = Lock()

def manejar_conversacion(chat_id, mensaje, actividad, fecha_actual):
    try:
        estado = obtener_estado_seguro(chat_id)

        # 🚫 Detección anticipada de desinterés o negativa persistente
        if any(p in mensaje.lower() for p in NEGATIVOS_FUERTES):
            estado["intentos_negativos"] = estado.get("intentos_negativos", 0) + 1
            logger.info("🚫 Cliente respondió con frase negativa. Intentos: %s", estado['intentos_negativos'])
            if estado["intentos_negativos"] >= 2:
                estado["fase"] = "cerrado_amablemente"
                estado["ultima_interaccion"] = fecha_actual.isoformat()
                guardar_estado(chat_id, estado)
                registrar_mensaje(chat_id, mensaje)
                return obtener_respuesta_por_actividad(estado.get("actividad", "otros"), "salida_amable")
        else:
            estado["intentos_negativos"] = 0

        etapa = estado.get("etapa", "")
        fase = estado.get("fase", "inicio")
        actividad_detectada = detectar_actividad(mensaje)

        # 👋 Primera vez: mostrar mensaje inicial
        if not etapa and fase == "inicio":
            estado["fase"] = "esperando_actividad"
            estado["ultima_interaccion"] = fecha_actual.isoformat()
            guardar_estado(chat_id, estado)
            registrar_mensaje(chat_id, mensaje)
            return RESPUESTA_INICIAL

        # ⛔ No permitir avanzar si no hay actividad aún
        if not etapa and fase == "esperando_actividad":
            if actividad_detectada:
                estado["actividad"] = actividad_detectada
                estado["etapa"] = "introduccion"
                estado["fase"] = "actividad_detectada"
                guardar_estado(chat_id, estado)
                registrar_mensaje(chat_id, mensaje)
                return obtener_respuesta_por_actividad(actividad_detectada, "introduccion")
            else:
                estado["ultima_interaccion"] = fecha_actual.isoformat()
                guardar_estado(chat_id, estado)
                registrar_mensaje(chat_id, mensaje)
                return "🙏 Para poder orientarle mejor, ¿podría indicarnos a qué actividad se dedica? Ej: *bananera, camaronera, minería...* 🌱"

        # 🛡️ Control de duplicados
        if bloqueo_activo(chat_id):
            logger.warning("⚠️ Evitando duplicidad por bloqueo activo para %s", chat_id)
            return None
        if mensaje_duplicado(chat_id, mensaje):
            activar_bloqueo(chat_id)
            logger.warning("❌ Mensaje duplicado detectado para %s. Activando bloqueo.", chat_id)
            return None

        # 🎯 Determinar siguiente etapa de forma estricta
        nueva_etapa, nueva_fase = determinar_siguiente_etapa(estado, mensaje)
        actividad_actual = estado.get("actividad", "otros")
        etapa_actual = estado.get("etapa")
        flujo_definido = FLUJOS_POR_ACTIVIDAD.get(actividad_actual, {})

        # ⛔ Validación estricta: no avanzar si la nueva_etapa no está definida
        if nueva_etapa not in flujo_definido:
            logger.error("❌ Etapa no válida: %s no está definida para la actividad %s", nueva_etapa, actividad_actual)
            return "🙏 Gracias por su mensaje. En breve le responderemos personalmente para coordinar su cita. 🌱"

        # ⛔ No saltarse etapas: permitir solo transiciones válidas
        etapas_definidas = list(flujo_definido.keys())
        indice_actual = etapas_definidas.index(etapa_actual) if etapa_actual in etapas_definidas else -1
        indice_nueva = etapas_definidas.index(nueva_etapa) if nueva_etapa in etapas_definidas else -1

        transicion_valida = (
            indice_nueva == indice_actual + 1 or
            (etapa_actual == "introduccion" and nueva_etapa in ["permiso_si", "permiso_no", "aclaracion_introduccion"]) or
            (etapa_actual == "aclaracion_introduccion" and nueva_etapa in ["permiso_si", "permiso_no"]) or
            (etapa_actual == "permiso_si" and nueva_etapa in ["cierre", "aclaracion_permiso_si"]) or
            (etapa_actual == "permiso_no" and nueva_etapa in ["cierre", "aclaracion_permiso_no"]) or
            (etapa_actual == "aclaracion_permiso_si" and nueva_etapa == "cierre") or
            (etapa_actual == "aclaracion_permiso_no" and nueva_etapa == "cierre") or
            (etapa_actual == "cierre" and nueva_etapa == "agradecimiento") or
            (etapa_actual == "aclaracion_cierre" and nueva_etapa == "agradecimiento")
        )

        if not transicion_valida:
            logger.error("❌ Flujo inválido: intento de salto de '%s' a '%s' en %s", etapa_actual, nueva_etapa, actividad_actual)
            return "🙏 Gracias por su mensaje. En breve le responderemos personalmente para coordinar su cita. 🌱"

        # ✅ Si todo está correcto, actualizar estado (permitiendo reentrar en cierre o aclaración)
        if (nueva_etapa != estado.get("etapa")) or (nueva_fase != estado.get("fase")) or (nueva_etapa in ["cierre", "aclaracion_cierre"]):
            logger.debug("➡️ Cambio de etapa: %s → %s", estado.get('etapa'), nueva_etapa)
            estado["etapa"] = nueva_etapa
            estado["fase"] = nueva_fase      
        
        # 📌 Detectar y registrar cita SOLO si YA estamos en etapa 'cierre' o 'aclaracion_cierre'
        if estado["etapa"] in ["cierre", "aclaracion_cierre"]:
            cita = extraer_fecha_y_hora(mensaje)

            if isinstance(cita, dict) and "fecha" in cita and "hora" in cita:
                modalidad = "oficina" if "oficina" in mensaje.lower() else "finca" if "finca" in mensaje.lower() else ""
                lugar = cita.get("ubicacion", "")
                observaciones = f"Mensaje original: {mensaje}"

                registrar_cita_en_hoja(
                    contacto=chat_id,
                    fecha_cita=cita["fecha"],
                    hora=cita["hora"],
                    modalidad=modalidad,
                    lugar=lugar,
                    observaciones=observaciones
                )

                estado["etapa"] = "agradecimiento"
                estado["fase"] = "cita_registrada"
                estado["ultimo_mensaje_procesado"] = mensaje
                guardar_estado(chat_id, estado)
                registrar_mensaje(chat_id, mensaje)
                return obtener_respuesta_por_actividad(actividad_actual, "agradecimiento")

            else:
                estado["etapa"] = "aclaracion_cierre"
                estado["fase"] = "esperando_cita"
                guardar_estado(chat_id, estado)
                registrar_mensaje(chat_id, mensaje)
                return obtener_respuesta_por_actividad(actividad_actual, "aclaracion_cierre")

        # 💾 Guardar estado final
        estado["ultima_interaccion"] = fecha_actual.isoformat()
        estado["chat_id"] = chat_id
        guardar_estado(chat_id, estado)
        registrar_mensaje(chat_id, mensaje)

        return obtener_respuesta_por_actividad(actividad_actual, nueva_etapa)

    except Exception as e:
        logger.exception("❌ Error crítico en manejar_conversacion con %s: %s", chat_id, e)
        return "Gracias por compartir la información. Para coordinar correctamente su cita, ¿podría confirmarnos por favor el *día*, la *hora* aproximada y si desea que lo visitemos en *finca u oficina*? Esta evaluación es sin costo 🌱"

def reiniciar_conversacion(chat_id):
    if chat_id in estado_conversaciones:
        del estado_conversaciones[chat_id]
    if chat_id in bloqueos_chat:
        del bloqueos_chat[chat_id]
    if chat_id in locks_chat:
        del locks_chat[chat_id]
    return f"🔄 Conversación con {chat_id} reiniciada exitosamente."
