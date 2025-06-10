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

def determinar_siguiente_etapa(actividad, etapa_actual, mensaje, estado, chat_id):
    # ✅ ETAPA: agradecimiento (final)
    if etapa_actual == "agradecimiento":
        if estado.get("fase") != "cita_registrada":
            cita = extraer_fecha_y_hora(mensaje)
            if cita and cita.get("fecha") and cita.get("hora"):
                registrar_cita(chat_id, cita["fecha"], cita["hora"], cita.get("ubicacion"))
                estado["fase"] = "cita_registrada"
        respuesta = obtener_respuesta_por_actividad(estado["actividad"], "agradecimiento")

    # 🌐 Flujo especial para "otros"
    elif actividad == "otros":
        cita = extraer_fecha_y_hora(mensaje)
        if cita and cita.get("fecha") and cita.get("hora"):
            return "agradecimiento"
        
        if any(p in mensaje.lower() for p in [
            "agendar", "programar", "calendarizar", "coordinar visita", "ponme una cita", "hazme la cita", "quiero agendar", "deseo agendar",
            "necesito agendar", "quiero coordinar", "sí, agenda", "ya quiero agendar",
            "visita", "visítenme", "visíteme", "me pueden visitar", "quiero que me visiten", "necesito que me visiten", "pueden venir",
            "puede venir", "vengan", "venga por favor", "que vengan", "necesito visita", "me gustaría que vengan", "quiero reunión presencial",
            "evaluación", "evaluar", "evaluación técnica", "revisión técnica", "revisar documentos", "quiero una evaluación", "pueden evaluar",
            "revisar mis permisos", "quiero que revisen", "necesito revisión", "sí, revisar"
        ]):
            return "cierre"

        return "aclaracion_introduccion"

    # ✅ ETAPA: cierre
    elif etapa_actual in ["cierre", "aclaracion_cierre"]:
        cita = extraer_fecha_y_hora(mensaje)
        if cita and cita.get("fecha") and cita.get("hora"):
            return "agradecimiento"
        else:
            return "aclaracion_cierre"  # ❗ No avanza hasta que se entienda

    # ✅ ETAPA: introducción
    elif etapa_actual in ["introduccion", "aclaracion_introduccion"]:
        if any(p in mensaje for p in ["tengo", "sí tengo", "ya tengo", "cuenta con", "disponemos"]):
            return "permiso_si"
        elif any(p in mensaje for p in ["no tengo", "ninguno", "aún no", "todavía no", "sin permiso"]):
            return "permiso_no"
        else:
            return "aclaracion_introduccion"  # ❗ No cambia etapa, se mantiene

    # ✅ ETAPA: permiso otorgado o no
    elif etapa_actual in ["permiso_si", "permiso_no", "aclaracion_permiso_si", "aclaracion_permiso_no"]:
        if any(p in mensaje for p in ["sí", "si", "claro", "por supuesto", "afirmativo", "de acuerdo", "ok", "vale", "está bien", "listo", "seguro", "acepto", "confirmo",
            "quiero", "me interesa", "me gustaría", "deseo", "necesito", "prefiero", "sí deseo", "sí quiero", "sí necesito", "sí me interesa",
            "agendar", "coordinemos", "calendarizar", "programar", "ponme una cita", "hazme la cita", "coordinemos visita",
            "pueden venir", "puede venir", "vengan por favor", "quiero que vengan", "agenden visita", "sí, visítenme", "pueden ir",
            "sii", "siii", "quieroo", "quiero agendar", "quiero cita", "si quiero", "si deseo", "si vienen"]):
            return "cierre"
        elif any(p in mensaje for p in ["no", "nop", "negativo", "ni de broma", "jamás", "nunca", "para nada", "no quiero", "no deseo", "no necesito",
            "no me interesa", "no por ahora", "no todavía", "todavía", "aún", "aun no", "no he decidido", "más adelante",
            "quizá después", "no en este momento", "no por el momento", "otro día", "en otra ocasión", "después",
            "ahorita no", "déjame pensarlo", "necesito pensarlo", "no estoy seguro", "no estoy lista", "no tengo tiempo"]):
            return etapa_actual  # ❗ Cliente no está listo, mantenemos etapa
        else:
            # Devuelve aclaración específica de esta etapa
            if etapa_actual.startswith("aclaracion_"):
                return etapa_actual  # Ya está en aclaración, no repetir
            else:
                return f"aclaracion_{etapa_actual}"

    return None  # Si no se cumple ninguna condición, devuelve None

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
    es_primera_interaccion = not estado.get("actividad") and not estado.get("etapa") and not estado.get("ultima_interaccion")
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
    
            # Solo para el PRIMER MENSAJE de la conversación, incluimos el saludo inicial
            if es_primera_interaccion:
                return RESPUESTA_INICIAL + "\n\n" + obtener_respuesta_por_actividad(actividad_detectada, "introduccion")

            else:
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

    # ⛔ Evitar que se reemplace la etapa si ya estamos en agradecimiento
    if estado.get("etapa") != "agradecimiento":
        try:
            nueva_etapa = determinar_siguiente_etapa(estado["actividad"], estado.get("etapa"), mensaje, estado, chat_id)
            if nueva_etapa:
                estado["etapa"] = nueva_etapa
        except Exception as e:
            print(f"❌ Error al determinar siguiente etapa para {chat_id}: {e}")

    # 🔐 Protección: si la etapa está vacía, forzar etapa segura
    if not etapa_actual:
        etapa_actual = "introduccion"
        estado["etapa"] = "introduccion"

    # ✅ Control seguro de registro de cita: solo si ya estamos en etapa de cierre
    if etapa_actual == "cierre":
        cita = extraer_fecha_y_hora(mensaje)

        if estado.get("fase") == "cita_registrada":
            print(f"🔁 Ya se registró una cita antes para {chat_id}, evitando duplicado.")
            return None

        if cita and cita.get("fecha") and cita.get("hora"):
            registrar_cita(chat_id, cita["fecha"], cita["hora"], cita.get("ubicacion"))
            estado["etapa"] = "agradecimiento"
            estado["fase"] = "cita_registrada"  # 🧠 Esto protege de nuevas sugerencias
            respuesta = obtener_respuesta_por_actividad(estado["actividad"], "agradecimiento")
        else:
            # Si falta algún dato, pedirlo de nuevo
            respuesta = obtener_respuesta_por_actividad(estado["actividad"], "aclaracion_cierre")
            estado["etapa"] = "aclaracion_cierre"  # Mantener en aclaración hasta que se proporcione correctamente    
    
    elif etapa_actual == "agradecimiento":
        respuesta = obtener_respuesta_por_actividad(estado["actividad"], "agradecimiento")

    else:
        respuesta = obtener_respuesta_por_actividad(estado["actividad"], etapa_actual)
    
    # 🧠 Guardar estado y registrar mensaje
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
