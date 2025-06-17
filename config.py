import os

class Config:
    """Configuración de la aplicación."""

    # Credenciales para la API de Green API
    GREENAPI_INSTANCE_ID = os.getenv("GREENAPI_INSTANCE_ID")
    GREENAPI_API_TOKEN = os.getenv("GREENAPI_API_TOKEN")
    GREEN_API_BASE_URL = "https://api.green-api.com"

    DEFAULT_RESPONSES = {
        "default": "👋 Hola, gracias por escribirnos. ¿Podría indicarnos a qué tipo de actividad se dedica? Bananera, camaronera, minería, cacaotera, ciclo corto, granja avícola, granja porcina, hotel, industria u otros."
    }

    MAX_MESSAGES_PER_MINUTE = 5
    MAX_RESPONSES_PER_HOUR = 30
