# follow_up_manager.py
from datetime import datetime
from zona_horaria import ZONA_HORARIA_EC
from google_sheets_utils import (
    conectar_hoja,
    registrar_mensaje,
    actualizar_estado_chat
)

ZONA_EC = ZONA_HORARIA_EC

MENSAJES_SEGUIMIENTO = {
    "seguimiento_1": "¡Hola! Solo queríamos asegurarnos de que viste nuestro mensaje anterior. ¿Te interesa que te ayudemos con tus necesidades ambientales?",
    "seguimiento_2": "Seguimos a tu disposición. Si deseas avanzar con tu trámite ambiental, podemos guiarte paso a paso.",
    "recordatorio": "Solo como recordatorio: si necesitas consultoría o licenciamiento ambiental, estamos listos para ayudarte. ¡Contáctanos!"
}

def gestionar_seguimiento(chat_id):
    hoja_mensajes = conectar_hoja("Mensajes")
    registros = hoja_mensajes.get_all_records()

    contacto = next((fila for fila in registros if fila.get("Teléfono") == chat_id), None)
    if not contacto:
        return

    estado = contacto.get("Estado", "activo").lower()
    fecha_str = contacto.get("Fecha")

    try:
        fecha_interaccion = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M:%S")
    except:
        return

    fecha_interaccion = fecha_interaccion.replace(tzinfo=ZONA_HORARIA_EC)
    ahora = datetime.now(ZONA_HORARIA_EC)
    minutos = (ahora - fecha_interaccion).total_seconds() / 60

    if estado == "activo" and minutos >= 30:
        mensaje = MENSAJES_SEGUIMIENTO["seguimiento_1"]
        registrar_mensaje(chat_id, mensaje, "Enviado", "Bot")
        actualizar_estado_chat(chat_id, "seguimiento_1")

    elif estado == "seguimiento_1" and minutos >= 60:
        mensaje = MENSAJES_SEGUIMIENTO["seguimiento_2"]
        registrar_mensaje(chat_id, mensaje, "Enviado", "Bot")
        actualizar_estado_chat(chat_id, "seguimiento_2")

    elif estado == "seguimiento_2" and minutos >= 4320:  # 3 días
        mensaje = MENSAJES_SEGUIMIENTO["recordatorio"]
        registrar_mensaje(chat_id, mensaje, "Enviado", "Bot")
        actualizar_estado_chat(chat_id, "recordatorio")

    elif estado == "recordatorio" and minutos >= 60:
        actualizar_estado_chat(chat_id, "cerrado")
