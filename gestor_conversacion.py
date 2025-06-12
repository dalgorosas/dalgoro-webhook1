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
from respuestas_por_actividad import detectar_actividad, obtener_respuesta_por_actividad, RESPUESTA_INICIAL
from respuestas_por_actividad import NEGATIVOS_FUERTES

ZONA_HORARIA_EC = timezone(timedelta(hours=-5))

bloqueos_chat = {}
locks_chat = {}

# Simulación de base de datos en memoria
estado_conversaciones = {}

def registrar_cita(chat_id, fecha, hora, ubicacion=None):
    print(f"🗕️ Se registró una cita para {chat_id}: {{'fecha': '{fecha}', 'hora': '{hora}', 'ubicacion': '{ubicacion}'}}")
    
    ubicacion_segura = ubicacion or ""
    modalidad = "Finca" if "finca" in ubicacion_segura.lower() else "Oficina"
    registrar_cita_en_hoja(
        contacto=chat_id,
        fecha_cita=fecha,
        hora=hora,
        modalidad=modalidad,
        lugar=ubicacion_segura or "No especificado",
        observaciones=""
    )
    # ✅ Notificar al número personal del Ing. Darwin
    from bot import enviar_mensaje  # Asegúrate que esta importación está activa arriba

    numero_personal = "593984770663@c.us"  # Reemplaza con tu número real

    mensaje_interno = (
        f"📢 *Nueva cita registrada:*\n"
        f"📅 *Fecha:* {fecha}\n"
        f"🕒 *Hora:* {hora}\n"
        f"📍 *Lugar:* {ubicacion_segura or 'No especificado'}\n"
        f"📞 *Cliente:* {chat_id.replace('@c.us', '')}\n"
        f"✉️ Mensaje automático para coordinación inmediata."
    )

    enviar_mensaje(numero_personal, mensaje_interno)

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
        if detectar_actividad(mensaje):  # está bien como primer paso
            return "introduccion", "actividad_detectada"
        else:
            return "", "inicio"

    elif etapa == "introduccion":
        if contiene_permiso_si(mensaje):
            return "permiso_si", "confirmado"
        elif contiene_permiso_no(mensaje):
            return "permiso_no", "confirmado"
        else:
            return "aclaracion_introduccion", fase

    elif etapa == "aclaracion_introduccion":
        if contiene_permiso_si(mensaje):
            return "permiso_si", "confirmado"
        elif contiene_permiso_no(mensaje):
            return "permiso_no", "confirmado"
        else:
            return "aclaracion_introduccion", fase

    elif etapa == "permiso_si":
        return "cierre", "esperando_cita"
    elif etapa == "permiso_no":
        return "cierre", "esperando_cita"

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

    return etapa, fase  # por defecto, sin cambio

def esta_bloqueado(chat_id):
    ahora = time.time()
    expiracion = bloqueos_chat.get(chat_id, 0)
    return ahora < expiracion

def bloquear_chat(chat_id, segundos=1.5):
    bloqueos_chat[chat_id] = time.time() + segundos
    if chat_id not in locks_chat:
        locks_chat[chat_id] = Lock()

def manejar_conversacion(chat_id, mensaje, actividad, fecha_actual):
    estado = obtener_estado_seguro(chat_id)

    # 🚫 Detección anticipada de desinterés o negativa persistente
    if any(p in mensaje.lower() for p in NEGATIVOS_FUERTES):
        estado["intentos_negativos"] = estado.get("intentos_negativos", 0) + 1
        print(f"🚫 Cliente respondió con frase negativa. Intentos: {estado['intentos_negativos']}")
        if estado["intentos_negativos"] >= 2:
            estado["fase"] = "cerrado_amablemente"
            estado["ultima_interaccion"] = fecha_actual.isoformat() if fecha_actual else datetime.now(ZONA_HORARIA_EC).isoformat()
            guardar_estado(chat_id, estado)
            registrar_mensaje(chat_id, mensaje)
            return obtener_respuesta_por_actividad(estado.get("actividad", "otros"), "salida_amable")
    else:
        estado["intentos_negativos"] = 0

    es_primera_interaccion = not estado.get("actividad") and not estado.get("etapa") and not estado.get("ultima_interaccion")
    etapa = estado.get("etapa")
    fase_actual = estado.get("fase", "inicio")

    # ⚠️ Detectar actividad si no está definida
    if not estado.get("actividad"):
        actividad_detectada = detectar_actividad(mensaje)
        if actividad_detectada:
            estado["actividad"] = actividad_detectada
            estado["etapa"] = "introduccion"
            estado["fase"] = "actividad_detectada"
            guardar_estado(chat_id, estado)
            registrar_mensaje(chat_id, mensaje)
            print(f"🧠 Actividad detectada automáticamente: {actividad_detectada}")
            if es_primera_interaccion:
                return RESPUESTA_INICIAL + "\n\n" + obtener_respuesta_por_actividad(actividad_detectada, "introduccion")
            else:
                return obtener_respuesta_por_actividad(actividad_detectada, "introduccion")

        # Solicitar aclaración de actividad
        estado["fase"] = "esperando_actividad"
        estado["etapa"] = ""
        estado["ultima_interaccion"] = fecha_actual.isoformat() if fecha_actual else datetime.now(ZONA_HORARIA_EC).isoformat()
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

    # 🚧 Determinar siguiente etapa basada en flujo estricto
    nueva_etapa, nueva_fase = determinar_siguiente_etapa(estado, mensaje)
    if nueva_etapa != estado.get("etapa") or nueva_fase != estado.get("fase"):
        print(f"➡️ Cambio de etapa: {estado.get('etapa')} → {nueva_etapa}")
        estado["etapa"] = nueva_etapa
        estado["fase"] = nueva_fase

    # 🎯 Registro de cita solo si corresponde
    if estado["etapa"] in ["cierre", "aclaracion_cierre"]:
        cita = extraer_fecha_y_hora(mensaje)
        if estado.get("fase") == "cita_registrada":
            print(f"🔁 Ya se registró una cita antes para {chat_id}, evitando duplicado.")
            return None
        if not cita or not cita.get("fecha") or not cita.get("hora"):
            estado["etapa"] = "aclaracion_cierre"
            respuesta = obtener_respuesta_por_actividad(estado["actividad"], "aclaracion_cierre")
        else:
            ubicacion = cita.get("ubicacion", "") or "No especificado"
            registrar_cita(chat_id=chat_id, fecha=cita["fecha"], hora=cita["hora"], ubicacion=ubicacion)
            estado["etapa"] = "agradecimiento"
            estado["fase"] = "cita_registrada"
            respuesta = obtener_respuesta_por_actividad(estado["actividad"], "agradecimiento")
    else:
        respuesta = obtener_respuesta_por_actividad(estado["actividad"], estado["etapa"])

    # 💾 Guardar estado actualizado
    estado["ultima_interaccion"] = fecha_actual.isoformat() if fecha_actual else datetime.now(ZONA_HORARIA_EC).isoformat()
    estado["chat_id"] = chat_id
    guardar_estado(chat_id, estado)
    registrar_mensaje(chat_id, mensaje)
    return respuesta

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
