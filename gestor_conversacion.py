from datetime import datetime
from threading import Lock
import time
import re
import logging
from estado_storage import guardar_estado, obtener_estado_seguro
from interpretador_citas import extraer_fecha_y_hora
from control_antirrepeticion import mensaje_duplicado, registrar_mensaje, bloqueo_activo, activar_bloqueo
from google_sheets_utils import registrar_cita_en_hoja
from google_sheets_utils import registrar_fallo_para_contacto
from reconocedor_intenciones import detectar_intencion
from respuestas_por_actividad import FLUJOS_POR_ACTIVIDAD
from respuestas_por_actividad import (
    detectar_actividad,
    obtener_respuesta_por_actividad,
    RESPUESTA_INICIAL,
    FLUJOS_POR_ACTIVIDAD
)
from respuestas_por_actividad import NEGATIVOS_FUERTES
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

def registrar_cita(chat_id, fecha, hora, ubicacion=None, mensaje="", estado=None):
    logger = logging.getLogger(__name__)

    logger.info("🗕️ Se solicitó registrar una cita para %s: {'fecha': '%s', 'hora': '%s', 'ubicacion': '%s'}", chat_id, fecha, hora, ubicacion)

    # 🛑 Validar etapa antes de registrar
    etapa_actual = estado.get("etapa") if estado else ""
    if etapa_actual not in ["cierre", "aclaracion_cierre"]:
        logger.warning("⛔ Registro de cita cancelado. Etapa no permitida: %s", etapa_actual)
        return

    ubicacion_segura = ubicacion or ""
    modalidad = "Finca" if "finca" in ubicacion_segura.lower() else "Oficina"

    # Solo en etapas válidas se usa el mensaje original
    mensaje_original = mensaje or estado.get("ultimo_mensaje_procesado", "(sin mensaje)")

    numero_limpio = re.sub(r"\D", "", chat_id.split("@")[0])

    try:
        registrar_cita_en_hoja(
            contacto=numero_limpio,
            fecha_cita=fecha,
            hora=hora,
            modalidad=modalidad,
            lugar=ubicacion_segura or "No especificado",
            observaciones=mensaje_original
        )
        logger.info("📄 Cita registrada correctamente en Google Sheets.")
    except Exception as e:
        logger.error("❌ Error al registrar cita en hoja de cálculo: %s", e)

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
            intencion = detectar_intencion(mensaje)

            if intencion in ["afirmacion_suave", "cita_implicita"]:
                return "cierre", "esperando_cita"

            elif intencion in ["mencion_permiso", "pregunta_abierta"]:
                return "aclaracion_introduccion", fase

            elif intencion == "negativo_ambiguo":
                return "aclaracion_permiso_no", fase  # o la etapa que uses para ambigüedad

            elif intencion in ["negativo_fuerte", "ofensivo"]:
                return "salida_amable", "cerrado_amablemente"

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
            intencion = detectar_intencion(mensaje)
            if intencion in ["mencion_permiso", "pregunta_abierta"]:
                return "aclaracion_introduccion", fase
            elif intencion == "negativo_fuerte":
                return "salida_amable", "cerrado_amablemente"
            elif intencion == "ofensivo":
                return "salida_amable", "cerrado_amablemente"
            return "aclaracion_introduccion", fase

    elif etapa == "permiso_si":
        clasificacion = clasificar_permiso(mensaje)
        intencion = detectar_intencion(mensaje)

        if clasificacion == "si":
            return "cierre", "esperando_cita"
        elif intencion in ["afirmacion_suave", "cita_implicita"]:
            return "cierre", "esperando_cita"
        elif clasificacion == "no":
            return "permiso_no", "confirmado"
        elif clasificacion == "mencion":
            return "aclaracion_permiso_si", "esperando_cita"
        elif intencion in ["pregunta_abierta", "mencion_permiso"]:
            return "aclaracion_permiso_si", "esperando_cita"
        elif intencion in ["negativo_fuerte", "ofensivo"]:
            return "salida_amable", "cerrado_amablemente"
        else:
            return "aclaracion_permiso_si", "esperando_cita"

    elif etapa == "aclaracion_permiso_si":
        clasificacion = clasificar_permiso(mensaje)
        intencion = detectar_intencion(mensaje)

        if clasificacion == "si":
            return "cierre", "esperando_cita"
        elif clasificacion == "no":
            return "permiso_no", "confirmado"
        elif intencion in ["afirmacion_suave", "cita_implicita"]:
            return "cierre", "esperando_cita"
        elif clasificacion == "mencion":
            return "aclaracion_permiso_si", "esperando_cita"
        elif intencion in ["pregunta_abierta", "mencion_permiso"]:
            return "aclaracion_permiso_si", "esperando_cita"
        elif intencion in ["negativo_fuerte", "ofensivo"]:
            return "salida_amable", "cerrado_amablemente"
        else:
            return "aclaracion_permiso_si", "esperando_cita"

    elif etapa == "permiso_no":
        clasificacion = clasificar_permiso(mensaje)
        intencion = detectar_intencion(mensaje)

        if clasificacion == "no":
            return "cierre", "esperando_cita"
        elif clasificacion == "si":
            return "permiso_si", "confirmado"
        elif intencion in ["afirmacion_suave", "cita_implicita"]:
            return "cierre", "esperando_cita"
        elif clasificacion == "mencion":
            return "aclaracion_permiso_no", "esperando_cita"
        elif intencion in ["pregunta_abierta", "mencion_permiso"]:
            return "aclaracion_permiso_no", "esperando_cita"
        elif intencion in ["negativo_fuerte", "ofensivo"]:
            return "salida_amable", "cerrado_amablemente"
        else:
            return "aclaracion_permiso_no", "esperando_cita"

    elif etapa == "aclaracion_permiso_no":
        clasificacion = clasificar_permiso(mensaje)
        intencion = detectar_intencion(mensaje)

        if clasificacion == "no":
            return "permiso_no", "confirmado"
        elif clasificacion == "si":
            return "cierre", "esperando_cita"
        elif intencion in ["afirmacion_suave", "cita_implicita"]:
            return "cierre", "esperando_cita"
        elif intencion in ["pregunta_abierta", "mencion_permiso"]:
            return "aclaracion_permiso_no", "esperando_cita"
        elif intencion in ["negativo_fuerte", "ofensivo"]:
            return "salida_amable", "cerrado_amablemente"
        else:
            return "aclaracion_permiso_no", "esperando_cita"

    elif etapa == "cierre":
        if extraer_fecha_y_hora(mensaje):
            return "agradecimiento", "cita_registrada"
        else:
            intencion = detectar_intencion(mensaje)
            if intencion in ["afirmacion_suave", "cita_implicita"]:
                return "cierre", "esperando_cita"
            elif intencion in ["pregunta_abierta", "mencion_permiso"]:
                return "aclaracion_cierre", "esperando_cita"
            elif intencion in ["negativo_fuerte", "ofensivo"]:
                return "salida_amable", "cerrado_amablemente"
            return "aclaracion_cierre", "esperando_cita"

    elif etapa == "aclaracion_cierre":
        if extraer_fecha_y_hora(mensaje):
            return "agradecimiento", "cita_registrada"
        else:
            intencion = detectar_intencion(mensaje)

            if intencion in ["afirmacion_suave", "cita_implicita"]:
                return "cierre", "esperando_cita"
            elif intencion in ["pregunta_abierta", "mencion_permiso"]:
                return "aclaracion_cierre", "esperando_cita"
            elif intencion in ["negativo_fuerte", "ofensivo"]:
                return "salida_amable", "cerrado_amablemente"
            else:
                return "aclaracion_cierre", "esperando_cita"

    elif etapa == "agradecimiento":
        return "agradecimiento", "cita_registrada"

    # ✅ Validación final de seguridad para evitar saltos no permitidos
    actividad = estado_actual.get("actividad_detectada", "")
    flujo = FLUJOS_POR_ACTIVIDAD.get(actividad, [])

    if etapa and etapa not in flujo:
        return "", "inicio"  # Reinicio forzado si etapa no es válida

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

        # 🛡️ Control de duplicados: se ejecuta ANTES de todo
        if bloqueo_activo(chat_id):
            logger.warning("⚠️ Evitando duplicidad por bloqueo activo para %s", chat_id)
            return None

        if mensaje_duplicado(chat_id, mensaje):
            activar_bloqueo(chat_id)
            logger.warning("❌ Mensaje duplicado detectado para %s. Activando bloqueo.", chat_id)

            if not any(x in mensaje.lower() for x in NEGATIVOS_FUERTES) and not mensaje.strip().startswith("AUDIO:"):
                registrar_fallo_para_contacto(chat_id, mensaje, estado, motivo="⚠️ Error: mensaje duplicado en etapa")

            return obtener_respuesta_por_actividad(estado.get("actividad", "otros"), estado.get("etapa", "introduccion"))

        # 🚫 Detección anticipada de desinterés o negativa persistente
        # ⚠️ Evitar aplicar en etapa introduccion o aclaracion_introduccion (ej: "no tengo")
        if estado.get("etapa") not in ["introduccion", "aclaracion_introduccion"] and any(p in mensaje.lower() for p in NEGATIVOS_FUERTES):
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
                return obtener_respuesta_por_actividad(
                    estado.get("actividad", "otros"),
                    estado.get("etapa", "introduccion")
                )

        # 🔁 Manejo especial: evitar bucle en aclaracion_permiso_si con IA básica
        if estado.get("etapa") == "aclaracion_permiso_si":
            from respuestas_por_actividad import PERMISOS_SI

            expresiones_validas = PERMISOS_SI + ["agenda", "visita", "quiero", "cita", "coordinar"]
            tipo_respuesta = detectar_intencion(mensaje)

            if tipo_respuesta in ["pregunta_abierta", "mencion_permiso"]:
                estado["intentos_aclaracion"] = 0
                estado["etapa"] = "cierre"
                estado["fase"] = "esperando_cita"
                guardar_estado(chat_id, estado)
                registrar_mensaje(chat_id, mensaje)
                return obtener_respuesta_por_actividad(estado.get("actividad", "otros"), "cierre")

            elif tipo_respuesta == "negativo_fuerte":
                estado["fase"] = "cerrado_amablemente"
                estado["etapa"] = "salida_amable"
                guardar_estado(chat_id, estado)
                registrar_mensaje(chat_id, mensaje)
                return obtener_respuesta_por_actividad(estado.get("actividad", "otros"), "salida_amable")

            elif tipo_respuesta == "ofensivo":
                estado["fase"] = "cerrado_amablemente"
                estado["etapa"] = "salida_amable"
                registrar_fallo_para_contacto(chat_id, mensaje, estado, motivo="❌ Mensaje ofensivo")
                guardar_estado(chat_id, estado)
                registrar_mensaje(chat_id, mensaje)
                return "😞 Hemos detectado un mensaje inapropiado. Finalizamos la conversación, pero puede escribirnos nuevamente si desea orientación."

            elif tipo_respuesta == "negativo_ambiguo":
                estado["intentos_aclaracion"] = estado.get("intentos_aclaracion", 0) + 1
                logger.info("🌀 Reintento #%s en aclaracion_permiso_si para %s", estado["intentos_aclaracion"], chat_id)

                if estado["intentos_aclaracion"] == 1:
                    guardar_estado(chat_id, estado)
                    registrar_mensaje(chat_id, mensaje)
                    return obtener_respuesta_por_actividad(estado.get("actividad", "otros"), "aclaracion_permiso_si")

                elif estado["intentos_aclaracion"] == 2:
                    guardar_estado(chat_id, estado)
                    registrar_mensaje(chat_id, mensaje)
                    return "🙏 Solo para confirmar, ¿usted cuenta actualmente con un permiso ambiental vigente como licencia o registro? Esto nos ayudará a guiarle mejor."

                elif estado["intentos_aclaracion"] >= 3:
                    estado["etapa"] = "salida_ambigua"
                    estado["fase"] = "salida"
                    guardar_estado(chat_id, estado)
                    registrar_mensaje(chat_id, mensaje)
                    return obtener_respuesta_por_actividad(estado.get("actividad", "otros"), "salida_ambigua")

            # Si no está en ninguna categoría IA, verificar manualmente si contiene expresiones válidas
            if not any(p in mensaje.lower() for p in expresiones_validas):
                estado["intentos_aclaracion"] = estado.get("intentos_aclaracion", 0) + 1
                logger.info("🌀 Reintento #%s en aclaracion_permiso_si para %s", estado["intentos_aclaracion"], chat_id)

                if estado["intentos_aclaracion"] == 1:
                    guardar_estado(chat_id, estado)
                    registrar_mensaje(chat_id, mensaje)
                    return obtener_respuesta_por_actividad(estado.get("actividad", "otros"), "aclaracion_permiso_si")

                elif estado["intentos_aclaracion"] == 2:
                    guardar_estado(chat_id, estado)
                    registrar_mensaje(chat_id, mensaje)
                    return "🙏 Solo para confirmar, ¿usted cuenta actualmente con un permiso ambiental vigente como licencia o registro? Esto nos ayudará a guiarle mejor."

                elif estado["intentos_aclaracion"] >= 3:
                    estado["etapa"] = "salida_ambigua"
                    estado["fase"] = "salida"
                    guardar_estado(chat_id, estado)
                    registrar_mensaje(chat_id, mensaje)
                    return obtener_respuesta_por_actividad(estado.get("actividad", "otros"), "salida_ambigua")

                elif tipo_respuesta in ["afirmacion_suave", "cita_implicita"]:
                    estado["etapa"] = "cierre"
                    estado["fase"] = "esperando_cita"
                    guardar_estado(chat_id, estado)
                    registrar_mensaje(chat_id, mensaje)

                    # 🚫 Prevenir ejecución de registro en este mismo ciclo
                    return obtener_respuesta_por_actividad(estado.get("actividad", "otros"), "cierre")

            else:
                estado["intentos_aclaracion"] = 0  # Reinicia si responde correctamente

        # 🔁 Manejo especial: evitar bucle en aclaracion_permiso_no
        if estado.get("etapa") == "aclaracion_permiso_no":

            intencion = detectar_intencion(mensaje)
            logger.info("🔍 Intención detectada en aclaracion_permiso_no: %s", intencion)

            if intencion in ["ofensivo", "negativo_fuerte"]:
                estado["fase"] = "cerrado_amablemente"
                estado["etapa"] = "salida_amable"
                estado["ultima_interaccion"] = fecha_actual.isoformat()
                guardar_estado(chat_id, estado)
                registrar_mensaje(chat_id, mensaje)
                return obtener_respuesta_por_actividad(estado.get("actividad", "otros"), "salida_amable")

            elif intencion == "negativo_ambiguo":
                estado["intentos_aclaracion"] = estado.get("intentos_aclaracion", 0) + 1
                logger.info("🌀 Reintento #%s en aclaracion_permiso_no para %s", estado["intentos_aclaracion"], chat_id)

                if estado["intentos_aclaracion"] == 1:
                    guardar_estado(chat_id, estado)
                    registrar_mensaje(chat_id, mensaje)
                    return obtener_respuesta_por_actividad(estado.get("actividad", "otros"), "aclaracion_permiso_no")

                elif estado["intentos_aclaracion"] >= 2:
                    estado["etapa"] = "salida_ambigua"
                    estado["fase"] = "salida"
                    guardar_estado(chat_id, estado)
                    registrar_mensaje(chat_id, mensaje)
                    return obtener_respuesta_por_actividad(estado.get("actividad", "otros"), "salida_ambigua")

            elif intencion == "afirmacion_suave":
                estado["intentos_aclaracion"] = 0
                estado["etapa"] = "cierre"
                estado["fase"] = "esperando_cita"
                guardar_estado(chat_id, estado)
                registrar_mensaje(chat_id, mensaje)
                return obtener_respuesta_por_actividad(...)

            elif intencion in ["pregunta_abierta", "mencion_permiso", "indefinido"]:
                guardar_estado(chat_id, estado)
                registrar_mensaje(chat_id, mensaje)
                return obtener_respuesta_por_actividad(
                    estado.get("actividad", "otros"),
                    "aclaracion_permiso_no"
                )

            elif intencion == "reactivacion":
                estado["etapa"] = "permiso_no"
                estado["fase"] = "confirmado"
                estado["ultima_interaccion"] = fecha_actual.isoformat()
                guardar_estado(chat_id, estado)
                registrar_mensaje(chat_id, mensaje)
                return obtener_respuesta_por_actividad(estado.get("actividad", "otros"), "permiso_no")

            elif intencion in ["afirmacion_suave", "cita_implicita"]:
                estado["intentos_aclaracion"] = 0  # ✅ Reinicia si responde bien
                estado["etapa"] = "cierre"
                estado["fase"] = "esperando_cita"
                guardar_estado(chat_id, estado)
                registrar_mensaje(chat_id, mensaje)
                return obtener_respuesta_por_actividad(
                    estado.get("actividad", "otros"),
                    "cierre"
                )

        # 🎯 Determinar siguiente etapa de forma estricta
        nueva_etapa, nueva_fase = determinar_siguiente_etapa(estado, mensaje)
        actividad_actual = estado.get("actividad", "otros")
        etapa_actual = estado.get("etapa")
        flujo_definido = FLUJOS_POR_ACTIVIDAD.get(actividad_actual, {})

        # ⛔ Validación estricta: no avanzar si la nueva_etapa no está definida
        if nueva_etapa not in flujo_definido:
            logger.warning("❌ Etapa no válida: %s no está definida para la actividad %s. Intentando recuperación con IA...", nueva_etapa, actividad_actual)
        
            intencion = detectar_intencion(mensaje)
            logger.info("🧠 Recuperación por IA activa. Intención detectada: %s", intencion)

            if intencion == "mencion_permiso":
                estado["etapa"] = "permiso_si"
                estado["fase"] = "confirmado"
            elif intencion == "negativo_fuerte":
                estado["etapa"] = "salida_amable"
                estado["fase"] = "cerrado_amablemente"
            elif intencion == "negativo_ambiguo":
                estado["etapa"] = "aclaracion_permiso_no"
                estado["fase"] = "confirmado"
            elif intencion == "pregunta_abierta":
                estado["etapa"] = "aclaracion_introduccion"
                estado["fase"] = "confirmado"
            elif intencion == "ofensivo":
                estado["etapa"] = "salida_amable"
                estado["fase"] = "cerrado_amablemente"
                registrar_fallo_para_contacto(chat_id, mensaje, estado, motivo="❌ Mensaje ofensivo")
                guardar_estado(chat_id, estado)
                registrar_mensaje(chat_id, mensaje)
                return "😞 Hemos detectado un mensaje inapropiado. Finalizamos la conversación, pero puede escribirnos nuevamente si desea orientación."
            else:
                # fallback final
                logger.warning("🤖 No se pudo recuperar con IA. Usando respuesta por defecto.")
                return obtener_respuesta_por_actividad("otros", "introduccion")

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

        # ✅ Si todo está correcto, actualizar estado (permitiendo reentrar en cierre o aclaración)
        if (nueva_etapa != estado.get("etapa")) or (nueva_fase != estado.get("fase")) or (nueva_etapa in ["cierre", "aclaracion_cierre"]):
            logger.debug("➡️ Cambio de etapa: %s → %s", estado.get('etapa'), nueva_etapa)
            estado["etapa"] = nueva_etapa
            estado["fase"] = nueva_fase      
        
        # 📌 Detectar y registrar cita, aunque esté incompleta, en etapa 'cierre' o 'aclaracion_cierre'
        if estado["etapa"] in ["cierre", "aclaracion_cierre"]:
            cita = extraer_fecha_y_hora(mensaje)
            logger.info("📅 Evaluando mensaje para registrar cita. Fecha=%s, Hora=%s, Ubicación=%s", cita.get("fecha"), cita.get("hora"), cita.get("ubicacion"))

            fecha = cita.get("fecha", "")
            hora = cita.get("hora", "")
            ubicacion = cita.get("ubicacion", "")
            observaciones = f"Mensaje original: {mensaje}"

            # Registrar siempre, aunque los campos estén vacíos
            etapa_actual = estado.get("etapa", "")
            mensaje_observacion = f"Mensaje original: {mensaje}" if etapa_actual in ["cierre", "aclaracion_cierre"] else ""

            registrar_cita(
                chat_id=chat_id,
                fecha=fecha,
                hora=hora,
                ubicacion=ubicacion,
                mensaje=mensaje_observacion,
                estado=estado
            )

            # Si fecha y hora están completas, avanzamos a 'agradecimiento'
            if fecha and hora:
                estado["etapa"] = "agradecimiento"
                estado["fase"] = "cita_registrada"
                estado["ultimo_mensaje_procesado"] = mensaje
                guardar_estado(chat_id, estado)
                registrar_mensaje(chat_id, mensaje)
                return obtener_respuesta_por_actividad(estado.get("actividad", "otros"), "agradecimiento")

            else:
                # Aún falta al menos un dato. Volver a pedirlos
                estado["etapa"] = "aclaracion_cierre"
                estado["fase"] = "esperando_cita"
                guardar_estado(chat_id, estado)
                registrar_mensaje(chat_id, mensaje)
                return obtener_respuesta_por_actividad(estado.get("actividad", "otros"), "aclaracion_cierre")

        if estado["etapa"] == "aclaracion_cierre":
            cita = extraer_fecha_y_hora(mensaje)
            if not (isinstance(cita, dict) and "fecha" in cita and "hora" in cita):
                estado["intentos_aclaracion"] = estado.get("intentos_aclaracion", 0) + 1
                logger.warning("⚠️ Reintento %s de cita incompleta en aclaracion_cierre", estado["intentos_aclaracion"])

                if estado["intentos_aclaracion"] >= 2:
                    registrar_fallo_para_contacto(chat_id, mensaje, estado, motivo="⚠️ Cita ambigua, requiere contacto directo")
                    return "Gracias por su interés. Vamos a coordinar directamente con usted para confirmar su cita. 🌱"

                guardar_estado(chat_id, estado)
                registrar_mensaje(chat_id, mensaje)
                return obtener_respuesta_por_actividad(estado.get("actividad", "otros"), "aclaracion_cierre")

        # 💾 Guardar estado final
        estado["ultima_interaccion"] = fecha_actual.isoformat()
        estado["chat_id"] = chat_id
        guardar_estado(chat_id, estado)
        registrar_mensaje(chat_id, mensaje)

        # 🔄 Si estamos en salida_ambigua y el cliente vuelve a escribir
        if estado.get("etapa") == "salida_ambigua":
            logger.info("🔄 Cliente reactivó conversación después de salida_ambigua: %s", mensaje)

            if not any(x in mensaje.lower() for x in NEGATIVOS_FUERTES) and not mensaje.strip().startswith("AUDIO:"):
                registrar_fallo_para_contacto(chat_id, mensaje, estado, motivo="📩 Reactivación posterior a salida_ambigua")

                # 📝 Se puede también registrar una fila explícita de reactivación en Google Sheets si lo deseas:
                registrar_cita(
                    chat_id=chat_id,
                    fecha="REACTIVADO",
                    hora="REACTIVADO",
                    ubicacion="",
                    mensaje=mensaje,
                    estado=estado
                )

            estado["etapa"] = ""
            estado["fase"] = "inicio"
            estado["actividad"] = ""
            estado["ultima_interaccion"] = fecha_actual.isoformat()
            guardar_estado(chat_id, estado)
            registrar_mensaje(chat_id, mensaje)
            return RESPUESTA_INICIAL
        
        guardar_estado(chat_id, estado)
        registrar_mensaje(chat_id, mensaje)
        return obtener_respuesta_por_actividad(estado.get("actividad", "otros"), estado.get("etapa", "introduccion"))

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
