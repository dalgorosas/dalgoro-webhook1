import os
import json
import logging
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cred_path = os.environ.get("GOOGLE_CREDENTIALS_JSON")
logger.info("🟢 Archivo a cargar: %s", cred_path)

if not cred_path or not os.path.isfile(cred_path):
    mensaje = (
        "Archivo de credenciales no encontrado. "
        "Define la variable de entorno GOOGLE_CREDENTIALS_JSON con la ruta al "
        "archivo JSON de la cuenta de servicio."
    )
    logger.error(mensaje)
    sys.exit(mensaje)

try:
    with open(cred_path, "r", encoding="utf-8") as f:
        cred_data = json.load(f)
        logger.info("✅ JSON cargado correctamente")
        logger.debug(json.dumps(cred_data, indent=2))
except Exception as e:
    logger.error("❌ Error: %s", e)
