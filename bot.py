import json
import requests
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Usa variables de entorno
INSTANCE_ID = os.getenv("7105252633")
API_TOKEN = os.getenv("67c2dece454947aba9d8d44daca573ccfa41c248c0424464a8")

def enviar_mensaje(numero, mensaje):
    if not mensaje:
        logger.warning("⚠️ Intento de envío sin mensaje para %s", numero)
        return None

    url = f"https://api.green-api.com/waInstance{INSTANCE_ID}/sendMessage/{API_TOKEN}"
    datos = {
        "chatId": f"{numero}@c.us",
        "message": mensaje
    }

    logger.debug("📦 JSON a enviar: %s", json.dumps(datos, indent=2))

    try:
        respuesta = requests.post(url, json=datos)
        respuesta.raise_for_status()  # Lanza excepción si el código no es 2xx

        try:
            data = respuesta.json()
            logger.info("✅ Mensaje enviado a %s: %s", numero, data)
            return data
        except ValueError:
            logger.warning("⚠️ Respuesta no era JSON. Código: %s", respuesta.status_code)
            logger.warning("Texto recibido: %s", respuesta.text)
            return None

    except requests.RequestException as e:
        logger.error("❌ Error al enviar mensaje a %s: %s", numero, e)
        return None

# 🧪 PRUEBA: Enviar mensaje
if __name__ == "__main__":
    numero_destino = "593998829143"
    texto = "Hola 👋, te saluda DALGORO SAS. ¿Te gustaría conocer nuestros servicios de regulación ambiental?"
    enviar_mensaje(numero_destino, texto)
