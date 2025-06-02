class Config:
    GREEN_API_INSTANCE = "tu_instancia_id"
    GREEN_API_TOKEN = "tu_token_api"
    GREEN_API_BASE_URL = "https://api.green-api.com"
    DEFAULT_RESPONSES = {
        "hola": "¡Hola! ¿En qué podemos ayudarte?",
        "licencia": "Ofrecemos consultoría para licenciamiento ambiental. ¿Quieres más información?",
        "default": "Gracias por contactarnos. Pronto responderemos."
    }
    MAX_MESSAGES_PER_MINUTE = 5
    MAX_RESPONSES_PER_HOUR = 30
