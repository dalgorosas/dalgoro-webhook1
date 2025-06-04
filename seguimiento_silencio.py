
# seguimiento_silencio.py

import datetime

SEGUIMIENTOS = [
    {
        "espera": datetime.timedelta(minutes=30),
        "mensaje": "👋 Solo queríamos saber si tuvo oportunidad de leer nuestro último mensaje. Estamos listos para ayudarle 😊"
    },
    {
        "espera": datetime.timedelta(hours=1),
        "mensaje": "📌 ¡Hola nuevamente! Quedamos atentos para coordinar una cita gratuita y personalizada. ¿Le gustaría que le llamemos para conversar mejor?"
    },
    {
        "espera": datetime.timedelta(days=3),
        "mensaje": "👀 Seguimos disponibles para apoyarle con su consulta ambiental. Si desea retomar la conversación, será un gusto ayudarle 🌿"
    },
    {
        "espera": datetime.timedelta(minutes=30),  # 30 min después del mensaje anterior
        "mensaje": None  # No insistir más. Reset automático si vuelve a escribir.
    }
]

def obtener_mensaje_seguimiento(minutos_desde_ultimo_mensaje):
    """
    Devuelve el mensaje de seguimiento correspondiente al tiempo transcurrido desde el último contacto.
    Si no se debe enviar más mensajes, devuelve None.
    """
    transcurrido = datetime.timedelta(minutes=minutos_desde_ultimo_mensaje)
    acumulado = datetime.timedelta(0)

    for paso in SEGUIMIENTOS:
        acumulado += paso["espera"]
        if transcurrido < acumulado:
            return paso["mensaje"]
    return None

def debe_reiniciar_conversacion(minutos_desde_ultimo_mensaje):
    """
    Devuelve True si el cliente respondió después de haber agotado los seguimientos.
    Esto reinicia el flujo desde el mensaje inicial.
    """
    max_tiempo = sum((paso["espera"] for paso in SEGUIMIENTOS), datetime.timedelta())
    return datetime.timedelta(minutes=minutos_desde_ultimo_mensaje) > max_tiempo
