from flask import Flask, request, jsonify
from google_sheets_utils import sheets_manager
from config import Config
from datetime import datetime
import requests
import logging
import json

app = Flask(__name__)
logger = logging.getLogger(__name__)

# ----------------------
# Control de límites
# ----------------------
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

# ----------------------
# Lógica del bot
# ----------------------
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

# ----------------------
# Webhook principal
# ----------------------
@app.route("/webhook", methods=["POST"])
def recibir():
    if not request.is_json:
        return jsonify({"error": "Formato inválido"}), 400

    data = request.json
    print("📥 JSON recibido:\n", json.dumps(data, indent=2))  # Para depuración

    try:
        mensaje = data["messageData"]["extendedTextMessageData"]["text"]
        telefono = data["senderData"]["chatId"].replace("@c.us", "")
    except KeyError as e:
        print("❌ Clave faltante en JSON:", e)
        return jsonify({"error": "Estructura de mensaje no esperada"}), 400

    if not telefono or not mensaje:
        print("❌ Datos incompletos:", telefono, mensaje)
        return jsonify({"error": "Datos incompletos"}), 400

    # Guardar en Sheets
    sheets_manager.update_contact(telefono)
    sheets_manager.log_message(telefono, mensaje, "Recibido", "WhatsApp")

    # Responder automáticamente
    respuesta = bot.get_response(mensaje)
    bot.send_message(telefono, respuesta)

    return jsonify({"status": "ok"}), 200

# ----------------------
# Ejecución local (opcional)
# ----------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
