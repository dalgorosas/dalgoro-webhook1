from flask import request, jsonify
from google_sheets_utils import sheets_manager
from config import Config
from app import app
from datetime import datetime
import requests
import logging

logger = logging.getLogger(__name__)

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

class WhatsAppBot:
    def __init__(self):
        self.responses = Config.DEFAULT_RESPONSES

    def get_response(self, mensaje):
        mensaje = mensaje.lower()
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

@app.route("/webhook", methods=["POST"])
def recibir():
    if not request.is_json:
        return jsonify({"error": "Formato inválido"}), 400
    data = request.json
    mensaje = data.get("messageData", {}).get("textMessageData", {}).get("textMessage", "")
    telefono = data.get("senderData", {}).get("chatId", "").replace("@c.us", "")
    if not telefono or not mensaje:
        return jsonify({"error": "Datos incompletos"}), 400
    if not rate_limiter.can_process_message(telefono):
        return jsonify({"error": "Límite alcanzado"}), 429
    sheets_manager.update_contact(telefono)
    sheets_manager.log_message(telefono, mensaje, "Recibido", "WhatsApp")
    respuesta = bot.get_response(mensaje)
    bot.send_message(telefono, respuesta)
    return jsonify({"status": "ok"}), 200

from flask import Flask, request
from google_sheets_utils import conectar_hoja
from datetime import datetime
import requests

app = Flask(__name__)

# 💬 Lógica del webhook
@app.route('/webhook', methods=['POST'])
def recibir_mensaje():
    data = request.json

    mensaje = data.get("messageData", {}).get("textMessageData", {}).get("textMessage", "").lower()
    telefono = data.get("senderData", {}).get("chatId", "").replace("@c.us", "")
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Registrar mensaje en hoja 'Mensajes'
    hoja_mensajes = conectar_hoja("Mensajes")
    hoja_mensajes.append_row([
        telefono,                 # ID_Contacto (usamos teléfono por ahora)
        fecha_hora,
        "Recibido",
        "WhatsApp",
        mensaje,
        "Pendiente",
        "Sí",
        "Bot",
        ""
    ])

    # Lógica de respuesta automática
    if "precio" in mensaje:
        respuesta = "Nuestros servicios empiezan desde $200. ¿Deseas agendar una llamada?"
    elif "cita" in mensaje or "agendar" in mensaje:
        respuesta = "Podemos reunirnos el lunes a las 10am o miércoles a las 2pm. ¿Cuál prefieres?"
    else:
        respuesta = "Gracias por escribirnos. ¿En qué te gustaría que te ayudemos?"

    enviar_respuesta(telefono, respuesta)

    return "ok", 200


# Función para responder vía Green API
def enviar_respuesta(numero, mensaje):
    url = "https://api.green-api.com/waInstance7105252633/sendMessage/67c2dece454947aba9d8d44daca573ccfa41c248c0424464a8"
    payload = {
        "chatId": f"{numero}@c.us",
        "message": mensaje
    }
    headers = {"Content-Type": "application/json"}
    requests.post(url, json=payload, headers=headers)


# Ejecutar servidor localmente
if __name__ == '__main__':
    app.run(port=5000)
