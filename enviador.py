# enviador.py
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def enviar_mensaje(chat_id, mensaje):
    logger.info("[MENSAJE A %s]: %s", chat_id, mensaje)
