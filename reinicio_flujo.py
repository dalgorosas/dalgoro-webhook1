
# reinicio_flujo.py

from datetime import datetime, timedelta
from zona_horaria import ZONA_HORARIA_EC
TIEMPO_MAX_SILENCIO = timedelta(days=3, minutes=30)

def debe_reiniciar_flujo(ultima_interaccion, ahora=None):
    if ahora is None:
        ahora = datetime.now(ZONA_HORARIA_EC)
    if ultima_interaccion.tzinfo is None:
        ultima_interaccion = ultima_interaccion.replace(tzinfo=ZONA_HORARIA_EC)
    if ahora.tzinfo is None:
        ahora = ahora.replace(tzinfo=ZONA_HORARIA_EC)
    return (ahora - ultima_interaccion) > TIEMPO_MAX_SILENCIO
