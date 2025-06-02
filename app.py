from flask import Flask

app = Flask(__name__)

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

