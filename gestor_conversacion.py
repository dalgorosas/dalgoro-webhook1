from estado_storage import guardar_estado
from datetime import datetime
from zoneinfo import ZoneInfo
from interpretador_citas import extraer_fecha_y_hora
from reinicio_flujo import debe_reiniciar_flujo
from respuestas_por_actividad import obtener_respuesta_por_actividad
from respuestas_finales import obtener_mensaje_agradecimiento
from seguimiento_silencio import manejar_seguimiento
from respuestas_por_actividad import obtener_respuesta_por_actividad, RESPUESTA_INICIAL
from respuestas_por_actividad import FLUJOS_POR_ACTIVIDAD
from estado_storage import obtener_estado_seguro  # asegúrate de importar esto al inicio
from dateutil.parser import isoparse  # asegúrate que esté importado arriba
import time
from threading import Lock
from datetime import timezone, timedelta
ZONA_HORARIA_EC = timezone(timedelta(hours=-5))

bloqueos_chat = {}
locks_chat = {}

# Simulación de base de datos en memoria
estado_conversaciones = {}

def registrar_cita(chat_id, cita):
    print(f"🗕️ Se registró una cita para {chat_id}: {cita}")
    if chat_id in estado_conversaciones:
        estado_conversaciones[chat_id]['cita'] = cita

def formatear_respuesta(respuesta):
    if isinstance(respuesta, str):
        return respuesta
    if isinstance(respuesta, list):
        return "\n".join(respuesta)
    return str(respuesta)

def determinar_siguiente_etapa(actividad, etapa_actual, mensaje_usuario):
    mensaje = mensaje_usuario.lower()

    if etapa_actual == "introduccion":
        if "tengo" in mensaje:
            return "permiso_si"
        elif "no tengo" in mensaje or "ninguno" in mensaje:
            return "permiso_no"
        else:
            return "aclaracion_introduccion"

    elif etapa_actual in ["permiso_si", "permiso_no"]:
        if "sí" in mensaje or "si" in mensaje or "quiero" in mensaje or "agendar" in mensaje:
            return "cierre"
        else:
            return f"aclaracion_{etapa_actual}"

    elif etapa_actual == "cierre":
        cita = extraer_fecha_y_hora(mensaje_usuario)
        if cita:
            return "agradecimiento"
        else:
            return "aclaracion_cierre"

    return etapa_actual


def esta_bloqueado(chat_id):
    ahora = time.time()
    expiracion = bloqueos_chat.get(chat_id, 0)
    return ahora < expiracion

def bloquear_chat(chat_id, segundos=1.5):
    bloqueos_chat[chat_id] = time.time() + segundos
    if chat_id not in locks_chat:
        locks_chat[chat_id] = Lock()

def manejar_conversacion(chat_id, mensaje, actividad, fecha_actual):
    if esta_bloqueado(chat_id):
        print(f"⚠️ Evitando duplicidad por bloqueo activo para {chat_id}")
        return None
    bloquear_chat(chat_id)
    
    ahora = fecha_actual or datetime.now(ZoneInfo("America/Guayaquil"))
    actividad_detectada = actividad  # Para mantener compatibilidad con el flujo
    try:      
        estado_prev = obtener_estado_seguro(chat_id)

    except Exception as e:
        print(f"⚠️ Error al obtener estado: {e}")
        estado_prev = {
            "actividad": None,
            "etapa": None,
            "fase": "inicio",
            "ultima_interaccion": datetime.now().isoformat()
        }
        guardar_estado(chat_id, estado_prev)  # ✅ Guardar si fue creado manualmente

   # Inicialización de conversación
    ultima_interaccion_str = estado_prev.get("ultima_interaccion")
    ultima_interaccion_dt = isoparse(ultima_interaccion_str) if isinstance(ultima_interaccion_str, str) else ultima_interaccion_str

    if ultima_interaccion_dt.tzinfo is None:
        ultima_interaccion_dt = ultima_interaccion_dt.replace(tzinfo=ZoneInfo("America/Guayaquil"))

    if chat_id not in estado_conversaciones or debe_reiniciar_flujo(ultima_interaccion_dt, ahora):

        from google_sheets_utils import cargar_estado_desde_sheets
        from estado_storage import obtener_estado_seguro as obtener_estado, guardar_estado
        estado_prev = obtener_estado(chat_id)  # Ahora devuelve un datetime válido

        if not estado_prev:
            estado_prev = cargar_estado_desde_sheets(chat_id)
            if estado_prev:
                guardar_estado(chat_id, estado_prev)

        if not estado_prev:
            estado_prev = {
        "actividad": actividad_detectada,
        "etapa": "introduccion",
        "fase": "inicio",
        "ultima_interaccion": ahora
    }
    guardar_estado(chat_id, estado_prev)  # ✅ Guardar si fue creado manualmente

    estado_conversaciones[chat_id] = estado_prev  # ✅ Necesario para no lanzar KeyError
    estado = estado_conversaciones[chat_id]
    estado["ultima_interaccion"] = fecha_actual or datetime.now(ZONA_HORARIA_EC)
    
    # Si ya se detectó la actividad y estamos en flujo de etapas
    if estado["actividad"]:
        etapa_actual = estado.get("etapa", "introduccion")
        nueva_etapa = determinar_siguiente_etapa(estado["actividad"], etapa_actual, mensaje)
        estado["etapa"] = nueva_etapa

        if nueva_etapa == "agradecimiento":
            cita = extraer_fecha_y_hora(mensaje)
            if cita:
                registrar_cita(chat_id, cita)
                fecha = cita.get("fecha") if isinstance(cita, dict) else cita[0]
                hora = cita.get("hora") if isinstance(cita, dict) else cita[1]
                return f"🗕 Hemos registrado su solicitud de cita para el {fecha} a las {hora} 🕓\nEl Ing. Darwin González Romero se comunicará con usted mediante el número 0984770663 para coordinar los detalles. Gracias por confiar en nosotros 🌱"

        respuesta = FLUJOS_POR_ACTIVIDAD[estado["actividad"]].get(nueva_etapa, "¿Podría explicarnos un poco más para poder ayudarle mejor? 😊")
        from google_sheets_utils import guardar_estado_en_sheets
        guardar_estado(chat_id, estado)
        guardar_estado_en_sheets(chat_id, estado)
        return formatear_respuesta(respuesta)

    # Si aún no se ha detectado actividad
    from respuestas_por_actividad import RESPUESTA_INICIAL

    if not estado["actividad"]:
        if actividad_detectada and actividad_detectada in FLUJOS_POR_ACTIVIDAD:
            estado["actividad"] = actividad_detectada
            estado["etapa"] = "introduccion"
            return formatear_respuesta(FLUJOS_POR_ACTIVIDAD[actividad_detectada]["introduccion"])
        else:
            return formatear_respuesta(RESPUESTA_INICIAL)

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
