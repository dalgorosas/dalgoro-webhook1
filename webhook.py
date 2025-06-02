from flask import Blueprint, request, jsonify
from google_sheets_utils import sheets_manager, conectar_hoja
from config import Config
from datetime import datetime
import requests
import logging

webhook_blueprint = Blueprint("webhook", __name__)
logger = logging.getLogger(__name__)

# Rate limiting
class RateLimiter:
    def __init__(self):
        self.message_counts = {}
        self.response_counts = {}

    def can_process_message(self, telefono):
        minuto = datetime.now().replace(second=0, microsecond=0)
        clave = f"{telefono}_{minuto}"
        cuenta = self.message_counts.get(clave, 0)
        if cuenta >= Config.MAX_MESSAGES_PER_MINUTE:
            return False
        self.message_counts[clave] = cuenta + 1
        return True

    def can_send_response(self):
        hora = datetime.now().replace(minute=0, second=0, microsecond=0)
        cuenta = self.response_counts.get(hora, 0)
        if cuenta >= Config.MAX_RESPONSES_PER_HOUR:
            return False
        self.response_counts[hora] = cuenta + 1
        return True

rate_limiter = RateLimiter()

# Bot de WhatsApp
class WhatsAppBot:
    def __init__(self):
        self.responses = Config.DEFAULT_RESPONSES

    def get_response(self, mensaje):
        mensaje = mensaje.lower()
        if "precio" in mensaje:
            return "Nuestros servicios empiezan desde $200. ¿Deseas agendar una llamada?"
        elif "cita" in mensaje or "agendar" in mensaje:
            return "Podemos reunirnos el lunes a las 10am o miércoles a las 2pm. ¿Cuál prefieres?"
        for clave, respuesta in self.responses.items():
            if clave != "default" and clave in mensaje:
                return respuesta
        return self.responses["default"]

    def send_message(self, telefono, mensaje):
        if not rate_limiter.can_send_response():
            return False
        url = f"{Config.GREEN_API_BASE_URL}/waInstance{Config.GREEN_API_INSTANCE}/sendMessage/{Config.GREEN_API_TOKEN}"
        data = {
            "chatId": f"{telefono}@c.us",
            "message": mensaje
        }
        headers = {"Content-Type": "application/json"}
        r = requests.post(url, json=data, headers=headers)
        if r.status_code == 200:
            sheets_manager.log_message(telefono, mensaje, "Enviado", "WhatsApp")
            return True
        return False

bot = WhatsAppBot()

@webhook_blueprint.route("/webhook", methods=["POST"])
def recibir_mensaje():
    if not request.is_json:
        return jsonify({"error": "Formato inválido"}), 400

    data = request.get_json()
    mensaje = data.get("messageData", {}).get("textMessageData", {}).get("textMessage", "")
    telefono = data.get("senderData", {}).get("chatId", "").replace("@c.us", "")

    if not telefono or not mensaje:
        return jsonify({"error": "Datos incompletos"}), 400

    if not rate_limiter.can_process_message(telefono):
        return jsonify({"error": "Límite alcanzado"}), 429

    sheets_manager.update_contact(telefono)
    sheets_manager.log_message(telefono, mensaje, "Recibido", "WhatsApp")

    # registrar también en hoja 'Mensajes'
    hoja_mensajes = conectar_hoja("Mensajes")
    hoja_mensajes.append_row([
        telefono,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Recibido",
        "WhatsApp",
        mensaje,
        "Pendiente",
        "Sí",
        "Bot",
        ""
    ])

    respuesta = bot.get_response(mensaje)
    bot.send_message(telefono, respuesta)

    return jsonify({"status": "ok"}), 200
