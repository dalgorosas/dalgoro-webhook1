import os

class Config:
    GREEN_API_INSTANCE = "7105252633"  # Puedes mantenerlo fijo
    GREEN_API_TOKEN = os.getenv("GREEN_API_TOKEN")  # ← Esto debe venir del entorno
    GREEN_API_BASE_URL = "https://api.green-api.com"

    DEFAULT_RESPONSES = {
        "hola": "¡Hola! ¿En qué podemos ayudarte?",
        "licencia": "Ofrecemos consultoría para licenciamiento ambiental. ¿Quieres más información?",
        "default": "Gracias por contactarnos. Pronto responderemos."
    }

    MAX_MESSAGES_PER_MINUTE = 5
    MAX_RESPONSES_PER_HOUR = 30
