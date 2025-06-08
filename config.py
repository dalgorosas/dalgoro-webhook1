import os

class Config:
    GREEN_API_INSTANCE = "7105252633"  # Puedes mantenerlo fijo
    GREEN_API_TOKEN = os.getenv("GREEN_API_TOKEN")  # ← Esto debe venir del entorno
    GREEN_API_BASE_URL = "https://api.green-api.com"

    DEFAULT_RESPONSES = {
        "default": "👋 Hola, gracias por escribirnos. ¿Podría indicarnos a qué tipo de actividad se dedica? Bananera, camaronera, minería, cacaotera, ciclo corto, granja avícola, granja porcina, hotel, industria u otros."
    }

    MAX_MESSAGES_PER_MINUTE = 5
    MAX_RESPONSES_PER_HOUR = 30
