from datetime import datetime
from interpretador_citas import extraer_fecha_y_hora
from reinicio_flujo import debe_reiniciar_flujo
from respuestas_por_actividad import FLUJOS_POR_ACTIVIDAD, RESPUESTA_INICIAL
from respuestas_finales import obtener_mensaje_agradecimiento
from seguimiento_silencio import obtener_mensaje_seguimiento, debe_reiniciar_conversacion

# Simulación de base de datos en memoria
estado_conversaciones = {}

def registrar_cita(chat_id, cita):
    print(f"📅 Se registró una cita para {chat_id}: {cita}")
    if chat_id in estado_conversaciones:
        estado_conversaciones[chat_id]['cita'] = cita

def formatear_respuesta(respuesta):
    if isinstance(respuesta, str):
        return respuesta
    if isinstance(respuesta, list):
        return "\n".join(respuesta)
    return str(respuesta)

def manejar_conversacion(chat_id, mensaje, actividad_detectada, ultima_interaccion):
    ahora = datetime.now()

    # Inicialización de conversación
    if chat_id not in estado_conversaciones or debe_reiniciar_flujo(ultima_interaccion, ahora):
        estado_conversaciones[chat_id] = {
            "actividad": None,
            "fase": "inicio",
            "ultima_interaccion": ahora
        }
        return RESPUESTA_INICIAL

    estado = estado_conversaciones[chat_id]
    estado["ultima_interaccion"] = ahora

    # 🔁 Seguimiento por silencio
    minutos_silencio = (ahora - ultima_interaccion).total_seconds() // 60
    mensaje_seguimiento = obtener_mensaje_seguimiento(minutos_silencio)
    if mensaje_seguimiento:
        return mensaje_seguimiento

    # Si hay cita en el mensaje
    cita = extraer_fecha_y_hora(mensaje)
    if cita:
        registrar_cita(chat_id, cita)
        return f"📅 Hemos registrado su solicitud de cita para el {cita['fecha']} a las {cita['hora']} 🕓\nNos comunicaremos para confirmar los detalles. Muchas gracias por confiar en nosotros."

    # Si aún no se ha detectado actividad
    if not estado["actividad"]:
        if actividad_detectada and actividad_detectada in FLUJOS_POR_ACTIVIDAD:
            estado["actividad"] = actividad_detectada
            return formatear_respuesta(FLUJOS_POR_ACTIVIDAD[actividad_detectada]["preguntas_frecuentes"])
        else:
            return "Gracias por escribirnos. ¿Podría contarnos un poco más sobre su caso para poder entender mejor y ayudarle adecuadamente? 🌱"

    # Si ya se dio el flujo de preguntas frecuentes y vuelve a responder
    if estado["actividad"]:
        return obtener_mensaje_agradecimiento(estado["actividad"])

    # Si cae en un caso no contemplado
    return "Gracias por escribirnos. En breve uno de nuestros asesores se pondrá en contacto con usted."
