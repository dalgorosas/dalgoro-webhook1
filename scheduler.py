# scheduler.py — prueba controlada del módulo de seguimiento
from follow_up_manager import gestionar_seguimiento
from google_sheets_utils import obtener_contactos_activos
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("🔁 Ejecutando verificación de seguimiento...")

contactos = obtener_contactos_activos()
logger.info("📋 Contactos activos encontrados: %s", len(contactos))

for contacto in contactos:
    chat_id = contacto["chat_id"]
    logger.info("🟡 Verificando seguimiento para: %s", chat_id)
    gestionar_seguimiento(chat_id)

logger.info("✅ Seguimiento ejecutado con éxito.")
