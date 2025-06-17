
import os
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ruta al archivo local de estado
ESTADO_PATH = "estado_usuarios.json"

# Paso 1: Borrar el estado local (si existe)
if os.path.exists(ESTADO_PATH):
    os.remove(ESTADO_PATH)
    logger.info("🗑️ Archivo de estado local eliminado para simular pérdida de memoria.")
else:
    logger.warning("⚠️ El archivo estado_usuarios.json no existe. Continuando igual...")

# Paso 2: Simular recepción de mensaje desde WhatsApp
from gestor_conversacion import manejar_conversacion

# Datos simulados del contacto
chat_id = "593984770663@c.us"
mensaje = "Lunes a las 14:00 en mi finca"
actividad_detectada = "bananera"
ultima_interaccion = datetime.now()

# Ejecutar el flujo
respuesta = manejar_conversacion(chat_id, mensaje, actividad_detectada, ultima_interaccion)
logger.info("🤖 Respuesta del bot:")
logger.info(respuesta)
