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

    # 🔁 Flujo especial para "otros"
    if actividad == "otros":
        if any(p in mensaje for p in ["quiero", "agendar", "visita", "evaluación", "evaluar", "pueden venir", "puede venir"]):
            return "cierre"
        cita = extraer_fecha_y_hora(mensaje_usuario)
        if cita:
            return "agradecimiento"
        return "aclaracion_introduccion"

    # ✅ ETAPA: introducción
    if etapa_actual in ["introduccion", "aclaracion_introduccion"]:
        if any(p in mensaje for p in ["tengo", "sí tengo", "ya tengo", "cuenta con", "disponemos"]):
            return "permiso_si"
        elif any(p in mensaje for p in ["no tengo", "ninguno", "aún no", "todavía no", "sin permiso"]):
            return "permiso_no"
        else:
            return "aclaracion_introduccion"  # ❗ No cambia etapa, se mantiene

    # ✅ ETAPA: permiso otorgado o no
    elif etapa_actual in ["permiso_si", "permiso_no", "aclaracion_permiso_si", "aclaracion_permiso_no"]:
        if any(p in mensaje for p in ["sí", "si", "quiero", "agendar", "evaluación", "pueden venir", "puede venir", "sí deseo"]):
            return "cierre"
        elif any(p in mensaje for p in ["no", "todavía", "aún"]):
            return etapa_actual  # ❗ Cliente no está listo, mantenemos etapa
        else:
            # Devuelve aclaración específica de esta etapa
            return f"aclaracion_{etapa_actual}"

    # ✅ ETAPA: cierre
    elif etapa_actual in ["cierre", "aclaracion_cierre"]:
        cita = extraer_fecha_y_hora(mensaje_usuario)
        if cita and cita.get("fecha") and cita.get("hora"):
            return "agradecimiento"
        else:
            return "aclaracion_cierre"  # ❗ No avanza hasta que se entienda

    # ✅ ETAPA: agradecimiento (final)
    elif etapa_actual == "agradecimiento":
        return "agradecimiento"

    # Por defecto, mantener la etapa actual
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

    # ⚠️ Iniciar con mensaje inicial si el estado está vacío y no está esperando actividad
    if not estado.get("actividad") and not estado.get("etapa") and fase_actual != "esperando_actividad":
        actividad_detectada = detectar_actividad(mensaje)
        if actividad_detectada:
            estado["actividad"] = actividad_detectada
            estado["etapa"] = "introduccion"
            estado["fase"] = "actividad_detectada"
            guardar_estado(chat_id, estado)
            registrar_mensaje(chat_id, mensaje)
            print(f"🧠 Actividad detectada automáticamente desde mensaje inicial: {actividad_detectada}")
            return obtener_respuesta_por_actividad(actividad_detectada, "introduccion")

        estado["fase"] = "inicio"
        estado["etapa"] = ""
        estado["ultima_interaccion"] = fecha_actual.isoformat() if fecha_actual else datetime.now(ZONA_HORARIA_EC).isoformat()
        guardar_estado(chat_id, estado)
        registrar_mensaje(chat_id, mensaje)
        print(f"📤 Enviando RESPUESTA_INICIAL a {chat_id} (reinicio por estado vacío sin detección)")
        return RESPUESTA_INICIAL

    # ✅ Detectar actividad si aún no está definida
    if not actividad and not estado.get("actividad"):
        actividad_detectada = detectar_actividad(mensaje)
        if actividad_detectada:
            actividad = actividad_detectada
            estado["actividad"] = actividad
            estado["etapa"] = "introduccion"
            estado["fase"] = "actividad_detectada"
            guardar_estado(chat_id, estado)
            print(f"🧠 Actividad detectada automáticamente: {actividad}")
        else:
            mensaje_actividades = (
                "🙏 Para poder orientarle mejor, ¿podría indicarnos a qué actividad se dedica? "
                "Por ejemplo: *bananera, camaronera, minería, cacaotera, cultivo de ciclo corto, "
                "granja porcina, granja avícola, hotel, industria u otra* 🌱"
            )
            estado["fase"] = "esperando_actividad"
            estado["etapa"] = ""
            estado["ultima_interaccion"] = fecha_actual.isoformat() if fecha_actual else datetime.now(ZONA_HORARIA_EC).isoformat()
            guardar_estado(chat_id, estado)
            registrar_mensaje(chat_id, mensaje)
            print(f"❓ Solicitud de aclaración de actividad enviada a {chat_id}")
            return mensaje_actividades

    # 🛡️ Control de duplicados
    if bloqueo_activo(chat_id):
        print(f"⚠️ Evitando duplicidad por bloqueo activo para {chat_id}")
        return None

    if mensaje_duplicado(chat_id, mensaje):
        activar_bloqueo(chat_id)
        print(f"❌ Mensaje duplicado detectado para {chat_id}. Activando bloqueo.")
        return None

    if actividad is None and estado.get("actividad"):
        actividad = estado["actividad"]

    if actividad:
        if estado.get("actividad") != actividad:
            estado["actividad"] = actividad
            estado["etapa"] = "introduccion"
        elif not estado.get("etapa"):
            estado["etapa"] = "introduccion"

    nueva_etapa = determinar_siguiente_etapa(estado["actividad"], etapa_actual, mensaje)
    if nueva_etapa:
        estado["etapa"] = nueva_etapa

    etapa_actual = estado.get("etapa")
    respuesta = None

    # ✅ Control seguro de registro de cita: solo si ya estamos en etapa de cierre
    if etapa_actual == "cierre":
        cita = extraer_fecha_y_hora(mensaje)

        if cita and cita.get("fecha") and cita.get("hora"):
            registrar_cita(chat_id, cita["fecha"], cita["hora"], cita.get("ubicacion"))
            estado["etapa"] = "agradecimiento"
            respuesta = obtener_respuesta_por_actividad(estado["actividad"], "agradecimiento")
        else:
            respuesta = obtener_respuesta_por_actividad(estado["actividad"], etapa_actual)

    elif etapa_actual == "agradecimiento":
        respuesta = obtener_respuesta_por_actividad(estado["actividad"], "agradecimiento")

    else:
        # Etapas anteriores no deben registrar citas aunque mencionen fechas
        respuesta = obtener_respuesta_por_actividad(estado["actividad"], etapa_actual)

    estado["ultima_interaccion"] = fecha_actual.isoformat() if fecha_actual else datetime.now(ZONA_HORARIA_EC).isoformat()
    estado["chat_id"] = chat_id
    guardar_estado(chat_id, estado)
    registrar_mensaje(chat_id, mensaje)

    print(f"📦 Estado a guardar en DB para {chat_id}: {estado}")

    if not respuesta:
        respuesta = obtener_respuesta_por_actividad(estado["actividad"], estado["etapa"])

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
