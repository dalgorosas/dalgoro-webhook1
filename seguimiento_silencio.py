# seguimiento_silencio.py

import datetime
from zona_horaria import ZONA_HORARIA_EC
from estado_storage import obtener_estado_seguro, guardar_estado
from google_sheets_utils import registrar_mensaje_seguimiento
from enviador import enviar_mensaje

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
        "espera": datetime.timedelta(minutes=30),
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

def manejar_seguimiento(chat_id):
    """
    Evalúa si se debe enviar un mensaje de seguimiento según el tiempo transcurrido desde la última interacción.
    Trabaja con almacenamiento local respaldado en Google Sheets.
    """
    estado = obtener_estado_seguro(chat_id)

    if not estado.get("ultima_interaccion"):
        print(f"⏳ No se encontró última_interaccion para {chat_id}")
        return

    ultima_interaccion = datetime.datetime.fromisoformat(estado["ultima_interaccion"])
    ahora = datetime.datetime.now(ZONA_HORARIA_EC)
    minutos_transcurridos = (ahora - ultima_interaccion).total_seconds() / 60

    mensaje = obtener_mensaje_seguimiento(minutos_transcurridos)
    if mensaje:
        enviar_mensaje(chat_id, mensaje)
        print(f"📨 Seguimiento enviado a {chat_id}: {mensaje}")

        # Actualizar estado
        estado["ultima_interaccion"] = ahora.isoformat()
        guardar_estado(chat_id, estado)

        # Registrar el seguimiento en Google Sheets
        registrar_mensaje_seguimiento(chat_id, mensaje, ahora.isoformat())
