from datetime import datetime, timezone, timedelta
from threading import Lock
import time
from dateutil.parser import isoparse

from enviador import enviar_mensaje
from estado_storage import guardar_estado, obtener_estado_seguro
from interpretador_citas import extraer_fecha_y_hora
from reinicio_flujo import debe_reiniciar_flujo
from respuestas_finales import obtener_mensaje_agradecimiento
from seguimiento_silencio import manejar_seguimiento
from google_sheets_utils import guardar_estado_en_sheets
from control_antirrepeticion import mensaje_duplicado, registrar_mensaje, bloqueo_activo, activar_bloqueo
from google_sheets_utils import registrar_cita_en_hoja
from respuestas_por_actividad import (
    detectar_actividad,
    obtener_respuesta_por_actividad,
    RESPUESTA_INICIAL,
    FLUJOS_POR_ACTIVIDAD
)
from respuestas_por_actividad import NEGATIVOS_FUERTES
from respuestas_por_actividad import contiene_permiso_si, contiene_permiso_no
from bot import enviar_mensaje  # Asegúrate que esta importación está activa arriba
from dateutil.parser import parse as parse_fecha
from respuestas_por_actividad import clasificar_permiso  # asegúrate de importar

ZONA_HORARIA_EC = timezone(timedelta(hours=-5))

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

        print(f"📦 JSON a enviar:\n{numero_personal=}\n{texto=}")
        enviar_mensaje(numero_personal, texto)
        print("📨 Notificación interna enviada por cita no registrada.")

    except Exception as e:
        print(f"⚠️ No se pudo enviar alerta personalizada: {e}")

def registrar_cita(chat_id, fecha, hora, ubicacion=None):
    print(f"🗕️ Se registró una cita para {chat_id}: {{'fecha': '{fecha}', 'hora': '{hora}', 'ubicacion': '{ubicacion}'}}")

    ubicacion_segura = ubicacion or ""
    modalidad = "Finca" if "finca" in ubicacion_segura.lower() else "Oficina"

    try:
        registrar_cita_en_hoja(
            contacto=chat_id,
            fecha_cita=fecha,
            hora=hora,
            modalidad=modalidad,
            lugar=ubicacion_segura or "No especificado",
            observaciones=""
        )

        # ✅ Notificar al número personal del Ing. Darwin
        numero_personal = formatear_chat_id("593984770663")

        mensaje_interno = (
            f"📢 *Nueva cita registrada:*\n"
            f"📅 *Fecha:* {fecha}\n"
            f"🕒 *Hora:* {hora}\n"
            f"📍 *Lugar:* {ubicacion_segura or 'No especificado'}\n"
            f"📞 *Cliente:* {chat_id.replace('@c.us', '')}\n"
            f"✉️ Mensaje automático para coordinación inmediata."
        )

        print(f"📦 Enviando a {numero_personal}:\n{mensaje_interno}")
        enviar_mensaje(numero_personal, mensaje_interno)

    except Exception as e:
        print(f"❌ Error al registrar o notificar cita: {e}")
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

    elif etapa == "aclaracion_permiso_si":
        clasificacion = clasificar_permiso(mensaje)
        if clasificacion == "si":
            return "permiso_si", "confirmado"
        elif any(x in mensaje.lower() for x in ["agenda", "visita", "quiero", "cita", "coordinar"]):
            return "cierre", "esperando_cita"
        else:
            return "aclaracion_permiso_si", "esperando_cita"

    elif etapa == "aclaracion_permiso_no":
        clasificacion = clasificar_permiso(mensaje)
        if clasificacion == "no":
            return "permiso_no", "confirmado"
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
            print(f"🚫 Cliente respondió con frase negativa. Intentos: {estado['intentos_negativos']}")
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
            print(f"⚠️ Evitando duplicidad por bloqueo activo para {chat_id}")
            return None
        if mensaje_duplicado(chat_id, mensaje):
            activar_bloqueo(chat_id)
            print(f"❌ Mensaje duplicado detectado para {chat_id}. Activando bloqueo.")
            return None

        # 🎯 Determinar siguiente etapa de forma estricta
        nueva_etapa, nueva_fase = determinar_siguiente_etapa(estado, mensaje)
        actividad_actual = estado.get("actividad", "otros")
        etapa_actual = estado.get("etapa")
        flujo_definido = FLUJOS_POR_ACTIVIDAD.get(actividad_actual, {})

        # ⛔ Validación estricta: no avanzar si la nueva_etapa no está definida
        if nueva_etapa not in flujo_definido:
            print(f"❌ Etapa no válida: {nueva_etapa} no está definida para la actividad {actividad_actual}")
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
            print(f"❌ Flujo inválido: intento de salto de '{etapa_actual}' a '{nueva_etapa}' en {actividad_actual}")
            return "🙏 Gracias por su mensaje. En breve le responderemos personalmente para coordinar su cita. 🌱"

        # ✅ Si todo está correcto, actualizar estado
        if nueva_etapa != estado.get("etapa") or nueva_fase != estado.get("fase"):
            print(f"➡️ Cambio de etapa: {estado.get('etapa')} → {nueva_etapa}")
            estado["etapa"] = nueva_etapa
            estado["fase"] = nueva_fase
        
        # ✅ Generar respuesta inmediata para etapas intermedias sin cita
        if estado["etapa"] in ["permiso_si", "permiso_no"]:
            respuesta = obtener_respuesta_por_actividad(estado["actividad"], estado["etapa"])
            estado["ultima_interaccion"] = fecha_actual.isoformat()
            estado["chat_id"] = chat_id
            guardar_estado(chat_id, estado)
            registrar_mensaje(chat_id, mensaje)
            return respuesta

        # ⏱ Intentar extraer cita solo si estamos en etapa de cierre o aclaración
        if estado["etapa"] in ["cierre", "aclaracion_cierre"]:
            respuesta = None  # Evita error si nunca se asigna en siguientes bloques
            cita = extraer_fecha_y_hora(mensaje)
    
            if estado.get("fase") == "cita_registrada":
                print(f"🔁 Ya se registró una cita antes para {chat_id}, evitando duplicado.")
                registrar_mensaje(chat_id, mensaje)
                return obtener_respuesta_por_actividad(estado["actividad"], "agradecimiento")

            if not isinstance(cita, dict):
                print(f"⚠️ Error: 'cita' no es un dict. Tipo recibido: {type(cita)} - Valor: {cita}")
                estado["etapa"] = "aclaracion_cierre"
                respuesta = obtener_respuesta_por_actividad(estado["actividad"], "aclaracion_cierre")
                if not respuesta:
                    respuesta = "Gracias por compartir la información. Para coordinar correctamente su cita, ¿podría confirmarnos por favor el *día*, la *hora* aproximada y si desea que lo visitemos en *finca u oficina*? Esta evaluación es sin costo 🌱"
                try:
                    enviar_alerta_a_personal(
                        chat_id=chat_id,
                        nombre=estado.get("nombre", "(sin nombre)"),
                        actividad=estado.get("actividad", "(sin actividad)"),
                        etapa=estado.get("etapa", ""),
                        fase=estado.get("fase", ""),
                        mensaje=mensaje,
                        fecha=fecha_actual
                    )
                except Exception as e:
                    print(f"⚠️ No se pudo enviar alerta personalizada: {e}")
                guardar_estado(chat_id, estado)
                registrar_mensaje(chat_id, mensaje)
                return respuesta

            elif "fecha" not in cita or "hora" not in cita:
                print(f"⚠️ Error: falta 'fecha' u 'hora' en cita: {cita}")
                estado["etapa"] = "aclaracion_cierre"
                respuesta = obtener_respuesta_por_actividad(estado["actividad"], "aclaracion_cierre")
                if not respuesta:
                    respuesta = "Gracias por compartir la información. Para coordinar correctamente su cita, ¿podría confirmarnos por favor el *día*, la *hora* aproximada y si desea que lo visitemos en *finca u oficina*? Esta evaluación es sin costo 🌱"
                try:
                    enviar_alerta_a_personal(
                        chat_id=chat_id,
                        nombre=estado.get("nombre", "(sin nombre)"),
                        actividad=estado.get("actividad", "(sin actividad)"),
                        etapa=estado.get("etapa", ""),
                        fase=estado.get("fase", ""),
                        mensaje=mensaje,
                        fecha=fecha_actual
                    )
                except Exception as e:
                    print(f"⚠️ No se pudo enviar alerta personalizada: {e}")
                guardar_estado(chat_id, estado)
                registrar_mensaje(chat_id, mensaje)
                return respuesta

            elif isinstance(cita, dict) and "fecha" in cita and "hora" in cita:
                registrar_cita(chat_id, cita["fecha"], cita["hora"], cita.get("ubicacion"))

                estado["etapa"] = "agradecimiento"
                estado["fase"] = "cita_registrada"
                estado["ultima_interaccion"] = fecha_actual.isoformat()
                estado["chat_id"] = chat_id

                respuesta = obtener_respuesta_por_actividad(estado["actividad"], "agradecimiento")

                guardar_estado(chat_id, estado)
                registrar_mensaje(chat_id, mensaje)
                return respuesta

        # 💾 Guardar estado actualizado
        estado["ultima_interaccion"] = fecha_actual.isoformat()
        estado["chat_id"] = chat_id
        guardar_estado(chat_id, estado)
        registrar_mensaje(chat_id, mensaje)

        # Validación adicional de seguridad
        if not isinstance(respuesta, str):
            print(f"❌ [ERROR] Respuesta inesperada (tipo {type(respuesta)}): {respuesta}")
            respuesta = "Gracias por su mensaje. En breve coordinaremos su cita."

        return respuesta or "🙏 Gracias por su mensaje. En breve le responderemos personalmente para coordinar su cita. 🌱"

    except Exception as e:
        print(f"❌ Error crítico en manejar_conversacion con {chat_id}: {e}")
        return "Gracias por compartir la información. Para coordinar correctamente su cita, ¿podría confirmarnos por favor el *día*, la *hora* aproximada y si desea que lo visitemos en *finca u oficina*? Esta evaluación es sin costo 🌱"

def reiniciar_conversacion(chat_id):
    if chat_id in estado_conversaciones:
        del estado_conversaciones[chat_id]
    if chat_id in bloqueos_chat:
        del bloqueos_chat[chat_id]
    if chat_id in locks_chat:
        del locks_chat[chat_id]
    return f"🔄 Conversación con {chat_id} reiniciada exitosamente."

def manejar_seguimiento(chat_id, estado):
    # Simulación para pruebas, no hace nada real
    return None
