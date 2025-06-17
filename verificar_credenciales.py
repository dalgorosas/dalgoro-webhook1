import os
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cred_path = os.environ.get("GOOGLE_CREDENTIALS_JSON")
logger.info("🟢 Archivo a cargar: %s", cred_path)

try:
    with open(cred_path, "r") as f:
        cred_data = json.load(f)
        logger.info("✅ JSON cargado correctamente")
        logger.debug(json.dumps(cred_data, indent=2))
except Exception as e:
    logger.error("❌ Error: %s", e)
