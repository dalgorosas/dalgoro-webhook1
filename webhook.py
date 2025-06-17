from gestor_conversacion import manejar_conversacion
from flask import Flask, request, jsonify
from google_sheets_utils import sheets_manager
from config import Config
from datetime import datetime
from bot import enviar_mensaje
from estado_storage import mensaje_ya_procesado, registrar_mensaje_procesado
import requests
import logging
import json
from mensaje_ids import cargar_ids, guardar_ids
from zona_horaria import ZONA_HORARIA_EC

mensajes_recientes = cargar_ids()


app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ----------------------
# Verificación de entorno
# ----------------------
if not Config.GREENAPI_INSTANCE_ID or not Config.GREENAPI_API_TOKEN:
    raise EnvironmentError("❌ GREENAPI_INSTANCE_ID o GREENAPI_API_TOKEN no están definidos en variables de entorno.")

# ----------------------
# Control de límites
# ----------------------
class RateLimiter:
    def __init__(self):
        self.message_counts = {}
        self.response_counts = {}

    def can_process_message(self, telefono):
        minuto = datetime.now(ZONA_HORARIA_EC).replace(second=0, microsecond=0)
        clave = f"{telefono}_{minuto}"
        cuenta = self.message_counts.get(clave, 0)
        if cuenta >= Config.MAX_MESSAGES_PER_MINUTE:
            return False
        self.message_counts[clave] = cuenta + 1
        return True

    def can_send_response(self):
        hora = datetime.now(ZONA_HORARIA_EC).replace(minute=0, second=0, microsecond=0)
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
    
    # ❗️Ignorar todo lo que no sea mensaje entrante
    if data.get("typeWebhook") != "incomingMessageReceived":
        return jsonify({"status": "ignorado"}), 200
    
    logger.info("📥 JSON recibido:\n%s", json.dumps(data, indent=2))
    
    mensaje_id = data.get("idMessage") or data.get("messageData", {}).get("idMessage")
    if mensaje_id in mensajes_recientes:
        logger.warning("⚠️ Mensaje duplicado detectado: %s", mensaje_id)
        return jsonify({"status": "duplicado"}), 200
    else:
        mensajes_recientes.add(mensaje_id)

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
        logger.error("❌ Clave faltante en JSON: %s", e)
        return jsonify({"error": "Estructura de mensaje no esperada"}), 400

    if not telefono or not mensaje:
        sheets_manager.log_message(telefono or "desconocido", "Mensaje vacío o malformado", "Error", "Bot")
        return jsonify({"error": "Datos incompletos"}), 400

    # Guardar contacto y registrar mensaje recibido
    sheets_manager.update_contact(telefono)
    sheets_manager.log_message(telefono, mensaje, "Recibido", "WhatsApp")

    from estado_storage import obtener_estado
    from dateutil.parser import isoparse
    from datetime import datetime

    chat_id = f"{telefono}@c.us"
    estado = obtener_estado(chat_id)
    ultima_interaccion = estado.get("ultima_interaccion")

    if ultima_interaccion:
        try:
            ultima_interaccion = isoparse(ultima_interaccion)
        except Exception:
            ultima_interaccion = datetime.now(ZONA_HORARIA_EC)
    else:
        ultima_interaccion = datetime.now(ZONA_HORARIA_EC)

    # ❗ Evitar procesar dos veces el mismo mensaje
    if mensaje_ya_procesado(chat_id, mensaje_id):
        logger.info("⏹️ Mensaje ya procesado anteriormente: %s", mensaje_id)
        return jsonify({"status": "ya_procesado"}), 200

    try:
        respuesta = manejar_conversacion(chat_id, mensaje, None, ultima_interaccion)
        logger.info("📤 Respuesta generada para %s: %s", telefono, respuesta)
    except Exception as e:
        logger.error("❌ Error al manejar conversación con %s: %s", telefono, e)
        respuesta = None
        
    # ✅ Marcar como procesado aunque haya error para evitar reenvíos infinitos
    registrar_mensaje_procesado(chat_id, mensaje_id)

    if not respuesta:
        logger.warning(f"⚠️ No se generó respuesta para {telefono}.")
        sheets_manager.log_message(telefono, "Sin respuesta generada", "Advertencia", "Bot")
        return jsonify({"status": "sin_respuesta"}), 200

    if len(respuesta) > 1000:
        respuesta = respuesta[:997] + "..."

    # ✅ Enviar la respuesta
    resultado_envio = enviar_mensaje(telefono, respuesta)
    if resultado_envio is None:
        logger.warning(f"❌ Falló el envío a {telefono}. Respuesta: {respuesta}")
    else:
        sheets_manager.log_message(telefono, respuesta, "Enviado", "Bot")

    return jsonify({"status": "ok"}), 200

# ----------------------
# Local (opcional)
# ----------------------

if __name__ == "__main__":
    def validar_token():
        import requests
        from config import Config

        url = f"https://api.green-api.com/waInstance{Config.GREENAPI_INSTANCE_ID}/getSettings/{Config.GREENAPI_API_TOKEN}"
        r = requests.get(url)
        logger.info("🔍 Resultado validación: %s %s", r.status_code, r.text)

    validar_token()
    app.run(debug=True, port=5000)

@app.route("/reiniciar", methods=["POST"])
def reiniciar_remoto():
    data = request.json
    chat_id = data.get("chat_id")

    if not chat_id:
        return jsonify({"error": "Falta el chat_id"}), 400

    from gestor_conversacion import reiniciar_conversacion
    resultado = reiniciar_conversacion(chat_id)
    return jsonify({"resultado": resultado})
