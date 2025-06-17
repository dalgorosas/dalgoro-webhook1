import os

class Config:
    GREENAPI_INSTANCE_ID = os.getenv("7105252633")
    GREENAPI_API_TOKEN = os.getenv("67c2dece454947aba9d8d44daca573ccfa41c248c0424464a8")
    GREEN_API_BASE_URL = "https://api.green-api.com"

    DEFAULT_RESPONSES = {
        "default": "👋 Hola, gracias por escribirnos. ¿Podría indicarnos a qué tipo de actividad se dedica? Bananera, camaronera, minería, cacaotera, ciclo corto, granja avícola, granja porcina, hotel, industria u otros."
    }

    MAX_MESSAGES_PER_MINUTE = 5
    MAX_RESPONSES_PER_HOUR = 30
