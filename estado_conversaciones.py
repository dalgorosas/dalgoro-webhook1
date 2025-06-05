from datetime import datetime
from interpretador_citas import extraer_fecha_y_hora
from reinicio_flujo import debe_reiniciar_flujo
from respuestas_por_actividad import obtener_respuesta_por_actividad
from respuestas_finales import obtener_mensaje_agradecimiento
from seguimiento_silencio import obtener_mensaje_seguimiento, manejar_seguimiento
from respuestas_por_actividad import obtener_respuesta_por_actividad, RESPUESTA_INICIAL
from respuestas_por_actividad import FLUJOS_POR_ACTIVIDAD
from estado_storage import obtener_estado, guardar_estado, reiniciar_estado

def registrar_cita(chat_id, cita):
    print(f"🗕️ Se registró una cita para {chat_id}: {cita}")
    estado = obtener_estado(chat_id)
    estado['cita'] = cita
    guardar_estado(chat_id, estado)

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

    estado = obtener_estado(chat_id)

    if debe_reiniciar_flujo(ultima_interaccion, ahora):
        estado.update({
            "actividad": None,
            "etapa": None,
            "fase": "inicio",
            "ultima_interaccion": ahora.isoformat()
        })
        guardar_estado(chat_id, estado)
        return RESPUESTA_INICIAL
    
    # 🧠 Proteger el sistema en caso de estado incompleto
    if not estado.get("actividad") or not estado.get("etapa"):
        estado.update({
            "actividad": actividad_detectada if actividad_detectada in FLUJOS_POR_ACTIVIDAD else None,
            "etapa": "introduccion",
            "fase": "inicio",
            "ultima_interaccion": ahora.isoformat()
        })
        guardar_estado(chat_id, estado)
        return RESPUESTA_INICIAL

    # Verificar si corresponde enviar mensaje de seguimiento
    if not ultima_interaccion or (ahora - ultima_interaccion).total_seconds() < 15:
        print("⏳ Ignorando seguimiento porque es una nueva conversación reciente.")
    else:
        minutos_pasados = (ahora - ultima_interaccion).total_seconds() / 60
        seguimiento = obtener_mensaje_seguimiento(minutos_pasados)
        if seguimiento:
            return seguimiento

    estado["ultima_interaccion"] = ahora.isoformat()

    cita = extraer_fecha_y_hora(mensaje)
    if cita:
        registrar_cita(chat_id, cita)
        return (
            f"🗓 Hemos registrado su solicitud de cita para el {cita['fecha']} a las {cita['hora']} ⏰.\n"
            "Nos comunicaremos para confirmar los detalles. Muchas gracias por confiar en nosotros."
        )
        
    if not estado["actividad"]:
        if actividad_detectada and actividad_detectada in FLUJOS_POR_ACTIVIDAD:
            estado["actividad"] = actividad_detectada
            estado["etapa"] = "introduccion"
            guardar_estado(chat_id, estado)
            return formatear_respuesta(FLUJOS_POR_ACTIVIDAD[actividad_detectada]["introduccion"])
        else:
            return "Gracias por escribirnos. ¿Podría contarnos un poco más sobre su caso para poder entender mejor y ayudarle adecuadamente? 🌱"

    etapa_actual = estado.get("etapa", "introduccion")
    nueva_etapa = determinar_siguiente_etapa(estado["actividad"], etapa_actual, mensaje)
    estado["etapa"] = nueva_etapa
    guardar_estado(chat_id, estado)
    respuesta = FLUJOS_POR_ACTIVIDAD[estado["actividad"]].get(nueva_etapa, "¿Podría explicarnos un poco más para poder ayudarle mejor? 😊")
    return formatear_respuesta(respuesta)

def reiniciar_conversacion(chat_id):
    reiniciar_estado(chat_id)
    estado = obtener_estado(chat_id)
    estado["ultima_interaccion"] = datetime.now().isoformat()
    guardar_estado(chat_id, estado)
    return f"🔄 Conversación con {chat_id} reiniciada exitosamente."

def manejar_seguimiento(chat_id, estado):
    return None
