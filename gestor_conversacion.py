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

def determinar_siguiente_etapa(actividad, etapa, mensaje, estado, chat_id):
    # 🚧 Refuerzo de lógica: no saltar etapas sin pasar por las anteriores
    secuencia_etapas = ["introduccion", "permiso_si", "permiso_no", "cierre", "agradecimiento"]
    etapa_actual = etapa or "introduccion"

    # Si se detecta una etapa fuera de secuencia, forzar el retorno a la etapa actual
    if etapa_actual not in secuencia_etapas:
        return "introduccion"

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
    elif etapa in ["cierre", "aclaracion_cierre"]:
        cita = extraer_fecha_y_hora(mensaje)
        if cita and cita.get("fecha") and cita.get("hora"):
            return "agradecimiento"
        else:
            return "aclaracion_cierre"  # ❗ No avanza hasta que se entienda

    elif etapa in ["introduccion", "aclaracion_introduccion"]:
        mensaje_limpio = mensaje.lower()

        negativos_permiso = [
            "no tengo", "ninguno", "aún no", "todavía no", "sin permiso", 
            "no contamos", "no dispongo", "aún estamos esperando", "no nos han dado", 
            "no lo hemos tramitado", "falta tramitar"
        ]

        positivos_permiso = [
            "tengo", "sí tengo", "ya tengo", "cuenta con", "disponemos",
            "ya contamos", "ya nos otorgaron", "nos aprobaron", "lo tenemos", 
            "ya nos dieron", "está vigente"
        ]

        if any(p in mensaje_limpio for p in negativos_permiso):
            return "permiso_no"
        elif any(p in mensaje_limpio for p in positivos_permiso):
            return "permiso_si"
        else:
            return "aclaracion_introduccion"

    # ✅ ETAPA: permiso otorgado o no
    elif etapa in ["permiso_si", "permiso_no", "aclaracion_permiso_si", "aclaracion_permiso_no"]:
        positivos = [
            "sí", "si", "claro", "por supuesto", "afirmativo", "de acuerdo", "ok", "vale", "está bien", "listo",
            "seguro", "acepto", "confirmo", "quiero", "me interesa", "me gustaría", "deseo", "necesito", "prefiero",
            "sí deseo", "sí quiero", "sí necesito", "sí me interesa", "quiero agendar", "coordinemos", "calendarizar",
            "programar", "hazme la cita", "coordinemos visita", "pueden venir", "puede venir", "vengan por favor", 
            "quiero que vengan", "agenden visita", "sí, visítenme", "pueden ir", "sii", "siii", "quieroo", "quiero cita",
            "si quiero", "si deseo", "si vienen"
        ]
        negativos = [
            "no", "nop", "negativo", "ni de broma", "jamás", "nunca", "para nada", "no quiero", "no deseo", 
            "no necesito", "no me interesa", "no por ahora", "no todavía", "todavía", "aún", "aun no", 
            "no he decidido", "más adelante", "quizá después", "no en este momento", "otro día", 
            "déjame pensarlo", "necesito pensarlo", "no estoy seguro", "no tengo tiempo"
        ]

        if any(p in mensaje.lower() for p in positivos):
            return "cierre"
        elif any(p in mensaje.lower() for p in negativos):
            return etapa
        else:
            if etapa.startswith("aclaracion_"):
                return etapa
            else:
                return f"aclaracion_{etapa}"

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
        estado["intentos_negativos"] = 0  # Reinicia si hay otra intención
    es_primera_interaccion = not estado.get("actividad") and not estado.get("etapa") and not estado.get("ultima_interaccion")
    etapa = estado.get("etapa")
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

    actividad = actividad or estado.get("actividad")
    if actividad and not estado.get("etapa"):
        estado["etapa"] = "introduccion"
        etapa = "introduccion"

    if estado.get("fase") == "cerrado_amablemente":
        print(f"🚫 Cliente ya mostró desinterés. No se continuará conversación.")
        return obtener_respuesta_por_actividad(estado["actividad"], "salida_amable")

    # ⛔ Evitar que se reemplace la etapa si ya estamos en agradecimiento
    if estado.get("etapa") != "agradecimiento":
        try:
            nueva_etapa = determinar_siguiente_etapa(estado["actividad"], estado.get("etapa"), mensaje, estado, chat_id)
            if nueva_etapa:
                estado["etapa"] = nueva_etapa
                etapa = estado["etapa"]  # ACTUALIZA la variable local etapa

        except Exception as e:
            print(f"❌ Error al determinar siguiente etapa para {chat_id}: {e}")
    
    # ✅ Control seguro de registro de cita: aceptar si está en etapa de cierre o aclaración de cierre
        if etapa in ["cierre", "aclaracion_cierre"]:
            print(f"🎯 Entrando a etapa de registro de cita. Estado actual: {estado}")
            cita = extraer_fecha_y_hora(mensaje)

            if estado.get("fase") == "cita_registrada":
                print(f"🔁 Ya se registró una cita antes para {chat_id}, evitando duplicado.")
                return None

            if not cita or not cita.get("fecha") or not cita.get("hora"):
                print(f"⚠️ No se pudo detectar cita completa o faltan datos. Solicitar aclaración.")
                estado["etapa"] = "aclaracion_cierre"
                respuesta = obtener_respuesta_por_actividad(estado["actividad"], "aclaracion_cierre")
            else:
                ubicacion = cita.get("ubicacion", "") or "No especificado"
                modalidad = "Oficina" if "oficina" in ubicacion.lower() else "Finca"

                print(f"📝 Registrando cita para {chat_id}: {cita['fecha']} a las {cita['hora']} en {ubicacion} ({modalidad})")

                registrar_cita(
                    chat_id=chat_id,
                    fecha=cita["fecha"],
                    hora=cita["hora"],
                    ubicacion=ubicacion
                )

                estado["etapa"] = "agradecimiento"
                estado["fase"] = "cita_registrada"
                respuesta = obtener_respuesta_por_actividad(estado["actividad"], "agradecimiento")

            registrar_cita_en_hoja(
                contacto=chat_id,
                fecha_cita=cita["fecha"],
                hora=cita["hora"],
                modalidad=modalidad,
                lugar=ubicacion,
                observaciones=""
            )          
        
            estado["etapa"] = "agradecimiento"
            estado["fase"] = "cita_registrada"  # 🧠 Esto protege de nuevas sugerencias
            respuesta = obtener_respuesta_por_actividad(estado["actividad"], "agradecimiento")
        else:
            respuesta = obtener_respuesta_por_actividad(estado["actividad"], "aclaracion_cierre")
            estado["etapa"] = "aclaracion_cierre"
      
    elif etapa == "agradecimiento":
        respuesta = obtener_respuesta_por_actividad(estado["actividad"], "agradecimiento")

    else:
        respuesta = obtener_respuesta_por_actividad(estado["actividad"], etapa)
    
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
