from datetime import datetime
from interpretador_citas import extraer_fecha_y_hora
from reinicio_flujo import debe_reiniciar_flujo
from respuestas_por_actividad import obtener_respuesta_por_actividad
from respuestas_finales import obtener_mensaje_agradecimiento
from seguimiento_silencio import manejar_seguimiento
from respuestas_por_actividad import obtener_respuesta_por_actividad, RESPUESTA_INICIAL
from respuestas_por_actividad import FLUJOS_POR_ACTIVIDAD

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

def manejar_conversacion(chat_id, mensaje, actividad_detectada, ultima_interaccion):
    ahora = datetime.now()
    print(f"📌 Mensaje recibido: {mensaje}")
    print(f"📌 Actividad detectada: {actividad_detectada}")

    # Inicialización de conversación
    if chat_id not in estado_conversaciones or debe_reiniciar_flujo(ultima_interaccion, ahora):
        estado_conversaciones[chat_id] = {
            "actividad": None,
            "fase": "inicio",
            "etapa": None,
            "ultima_interaccion": ahora
        }
        return RESPUESTA_INICIAL

    estado = estado_conversaciones[chat_id]
    estado["ultima_interaccion"] = ahora

    # Si hay cita en el mensaje
    cita = extraer_fecha_y_hora(mensaje)
    if cita:
        registrar_cita(chat_id, cita)
        return f"🗕 Hemos registrado su solicitud de cita para el {cita['fecha']} a las {cita['hora']} 🕓\nNos comunicaremos para confirmar los detalles. Muchas gracias por confiar en nosotros."

    # Si aún no se ha detectado actividad
    if not estado["actividad"]:
        if actividad_detectada and actividad_detectada in FLUJOS_POR_ACTIVIDAD:
            estado["actividad"] = actividad_detectada
            estado["etapa"] = "introduccion"
            return formatear_respuesta(FLUJOS_POR_ACTIVIDAD[actividad_detectada]["introduccion"])
        else:
            return "Gracias por escribirnos. ¿Podría contarnos un poco más sobre su caso para poder entender mejor y ayudarle adecuadamente? 🌱"

    # Si ya se detectó la actividad y estamos en flujo de etapas
    if estado["actividad"]:
        etapa_actual = estado.get("etapa", "introduccion")
        nueva_etapa = determinar_siguiente_etapa(estado["actividad"], etapa_actual, mensaje)
        estado["etapa"] = nueva_etapa
        respuesta = FLUJOS_POR_ACTIVIDAD[estado["actividad"]].get(nueva_etapa, "¿Podría explicarnos un poco más para poder ayudarle mejor? 😊")
        return formatear_respuesta(respuesta)

    return "Gracias por escribirnos. En breve uno de nuestros asesores se pondrá en contacto con usted."

def reiniciar_conversacion(chat_id):
    """
    Reinicia manualmente la conversación de un número específico de WhatsApp.
    """
    if chat_id in estado_conversaciones:
        del estado_conversaciones[chat_id]
        return f"🔄 Conversación con {chat_id} reiniciada exitosamente."
    else:
        return f"⚠️ No hay conversación activa con {chat_id}."

def manejar_seguimiento(chat_id, estado):
    # Simulación para pruebas, no hace nada real
    return None

def reiniciar_conversacion(chat_id):
    """
    Elimina todo rastro del contacto en el estado de conversación.
    """
    if chat_id in estado_conversaciones:
        del estado_conversaciones[chat_id]
        return f"✅ Conversación con {chat_id} reiniciada correctamente."
    else:
        return f"ℹ️ No se encontró estado previo para {chat_id}. No había nada que reiniciar."
