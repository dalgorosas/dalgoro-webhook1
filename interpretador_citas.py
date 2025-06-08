from datetime import datetime
from dateutil import parser
import re
import pytz
from dateparser.search import search_dates

# ✅ ZONA HORARIA DE ECUADOR
ZONA_HORARIA_EC = pytz.timezone("America/Guayaquil")

# Patrones para extraer hora en formato simple (ej. "a las 10", "10am", "10:30")
patrones = [
    r"\b(?:a\s+las\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\b",
    r"\b(\d{1,2})\s*(am|pm)\b"
]

def extraer_fecha_y_hora(texto):
    fecha_hora = search_dates(
        texto,
        languages=["es"],
        settings={
            'TIMEZONE': 'America/Guayaquil',
            'RETURN_AS_TIMEZONE_AWARE': True,
            'PREFER_DATES_FROM': 'future',
            'RELATIVE_BASE': datetime.now(ZONA_HORARIA_EC)
        }
    )

    if not fecha_hora:
        return None

    fecha_detectada = fecha_hora[0][1]
    fecha_ecuador = fecha_detectada.astimezone(ZONA_HORARIA_EC)
    fecha_formateada = fecha_ecuador.strftime("%Y-%m-%d")
    hora_formateada = fecha_ecuador.strftime("%H:%M")

    return {
        "fecha": fecha_formateada,
        "hora": hora_formateada
    }
