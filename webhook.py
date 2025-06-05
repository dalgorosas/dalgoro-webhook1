from estado_conversaciones import manejar_conversacion
from flask import Flask, request, jsonify
from google_sheets_utils import sheets_manager
from config import Config
from datetime import datetime
from bot import enviar_mensaje
import requests
import logging
import json

app = Flask(__name__)
logger = logging.getLogger(__name__)

# ----------------------
# Verificación de entorno
# ----------------------
if not Config.GREEN_API_INSTANCE or not Config.GREEN_API_TOKEN:
    raise EnvironmentError("❌ GREEN_API_INSTANCE o GREEN_API_TOKEN no están definidos en variables de entorno.")

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
# Webhook principal
# ----------------------
@app.route("/webhook", methods=["POST"])
def recibir():
    if not request.is_json:
        return jsonify({"error": "Formato inválido"}), 400

    data = request.json
    print("📥 JSON recibido:\n", json.dumps(data, indent=2))

    # Ignorar eventos que no son mensajes entrantes
    if data.get("typeWebhook") != "incomingMessageReceived":
        return jsonify({"status": "ignorado"}), 200

    try:
        tipo = data["messageData"].get("typeMessage", "")
        if tipo == "extendedTextMessage":
            mensaje = data["messageData"]["extendedTextMessageData"]["text"]
        elif tipo == "textMessage":
            mensaje = data["messageData"]["textMessageData"]["textMessage"]
        else:
            mensaje = ""
        telefono = data["senderData"]["chatId"].replace("@c.us", "")
    except KeyError as e:
        print("❌ Clave faltante en JSON:", e)
        return jsonify({"error": "Estructura de mensaje no esperada"}), 400

    if not telefono or not mensaje:
        print("❌ Datos incompletos:", telefono, mensaje)
        return jsonify({"error": "Datos incompletos"}), 400

    # Guardar contacto y registrar mensaje recibido
    sheets_manager.update_contact(telefono)
    sheets_manager.log_message(telefono, mensaje, "Recibido", "WhatsApp")

    # Obtener respuesta desde lógica personalizada
    respuesta = manejar_conversacion(f"{telefono}@c.us", mensaje, None, datetime.now())

    # Registrar y enviar la respuesta
    sheets_manager.log_message(telefono, respuesta, "Enviado", "Bot")
    enviar_mensaje(telefono, respuesta)


    return jsonify({"status": "ok"}), 200

# ----------------------
# Local (opcional)
# ----------------------

if __name__ == "__main__":
    def validar_token():
        import requests
        from config import Config

        url = f"https://api.green-api.com/waInstance{Config.GREEN_API_INSTANCE}/getSettings/{Config.GREEN_API_TOKEN}"
        r = requests.get(url)
        print("🔍 Resultado validación:", r.status_code, r.text)

    validar_token()
    app.run(debug=True, port=5000)
