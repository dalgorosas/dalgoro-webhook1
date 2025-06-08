from datetime import datetime, timezone, timedelta
from threading import Lock
import time
from dateutil.parser import isoparse

from estado_storage import guardar_estado, obtener_estado_seguro
from interpretador_citas import extraer_fecha_y_hora
from reinicio_flujo import debe_reiniciar_flujo
from respuestas_por_actividad import obtener_respuesta_por_actividad, RESPUESTA_INICIAL
from respuestas_finales import obtener_mensaje_agradecimiento
from seguimiento_silencio import manejar_seguimiento
from google_sheets_utils import guardar_estado_en_sheets
from respuestas_por_actividad import detectar_actividad
from control_antirrepeticion import mensaje_duplicado, registrar_mensaje, bloqueo_activo, activar_bloqueo
from google_sheets_utils import registrar_cita_en_hoja


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

def formatear_respuesta(respuesta):
    if isinstance(respuesta, str):
        return respuesta
    if isinstance(respuesta, list):
        return "\n".join(respuesta)
    return str(respuesta)

def determinar_siguiente_etapa(actividad, etapa_actual, mensaje_usuario):
    mensaje = mensaje_usuario.lower()

    # 🔁 Flujo universal para actividad 'otros' u otros flujos simplificados
    if actividad == "otros":
        if any(palabra in mensaje for palabra in ["quiero", "agendar", "visita", "evaluación", "evaluar", "pueden venir", "puede venir"]):
            return "cierre"
        cita = extraer_fecha_y_hora(mensaje_usuario)
        if cita:
            return "agradecimiento"
        return "aclaracion_introduccion"

    # 🔁 Flujo tradicional para bananera, camaronera, etc.
    if etapa_actual == "introduccion":
        if "tengo" in mensaje:
            return "permiso_si"
        elif "no tengo" in mensaje or "ninguno" in mensaje:
            return "permiso_no"
        else:
            return "aclaracion_introduccion"

    elif etapa_actual in ["permiso_si", "permiso_no"]:
        if any(palabra in mensaje for palabra in ["sí", "si", "quiero", "agendar", "evaluación"]):
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
    estado = obtener_estado_seguro(chat_id)
    etapa_actual = estado.get("etapa")
    fase_actual = estado.get("fase", "inicio")

    print(f"💬 Nuevo mensaje de {chat_id}. Etapa actual: {etapa_actual}, Actividad: {estado.get('actividad')}")

    # 🛡️ Evita duplicados si hay bloqueo activo
    if bloqueo_activo(chat_id):
        print(f"⚠️ Evitando duplicidad por bloqueo activo para {chat_id}")
        return None

    # 🛡️ Si el mensaje es igual a uno reciente, activa bloqueo y no responde
    if mensaje_duplicado(chat_id, mensaje):
        activar_bloqueo(chat_id)
        print(f"❌ Mensaje duplicado detectado para {chat_id}. Activando bloqueo.")
        return None

    # Si no hay actividad definida aún, usar la pasada si existe
    if actividad is None and estado.get("actividad"):
        actividad = estado["actividad"]

    # Si hay actividad nueva, actualizar estado
    if actividad:
        estado["actividad"] = actividad

    # Determinar siguiente etapa según mensaje recibido
    nueva_etapa = determinar_siguiente_etapa(estado["actividad"], etapa_actual, mensaje)

    if nueva_etapa:
        estado["etapa"] = nueva_etapa

    # Si en etapa de cierre o agradecimiento se detecta cita, extraer fecha y hora
    respuesta = None
    if estado["etapa"] in ["cierre", "agradecimiento"]:
        cita = extraer_fecha_y_hora(mensaje)
        if cita:
            print(f"🗕️ Se registró una cita para {chat_id}: {cita}")
            registrar_cita(chat_id, cita["fecha"], cita["hora"], cita.get("ubicacion"))
            respuesta = f"🙌 Su cita ha sido registrada correctamente. El Ing. Darwin González Romero se comunicará con usted mediante el número 0984770663 para confirmar los detalles. ¡Gracias por confiar en nosotros! 🌿"
        else:
            respuesta = obtener_respuesta_por_actividad(estado["actividad"], estado["etapa"])
    else:
        respuesta = obtener_respuesta_por_actividad(estado["actividad"], estado["etapa"])

    # Si no se pasa fecha_actual, usar la actual en horario de Ecuador
    if not fecha_actual:
        fecha_actual = datetime.now(ZONA_HORARIA_EC)
    
    # Actualizar última interacción
    estado["ultima_interaccion"] = fecha_actual.isoformat()
    estado["chat_id"] = chat_id

    print(f"📦 Estado a guardar en DB para {chat_id}: {estado}")
    guardar_estado(chat_id, estado)

    # ✅ Registrar el mensaje procesado para control antirrepetición
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
