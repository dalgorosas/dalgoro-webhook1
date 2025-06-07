
# reinicio_flujo.py

import datetime
from datetime import timezone, timedelta
ZONA_HORARIA_EC = timezone(timedelta(hours=-5))
TIEMPO_MAX_SILENCIO = datetime.timedelta(days=3, minutes=30)

def debe_reiniciar_flujo(ultima_interaccion, ahora=None):
    if ahora is None:
        ahora = datetime.now(ZONA_HORARIA_EC)
    if ultima_interaccion.tzinfo is None:
        ultima_interaccion = ultima_interaccion.replace(tzinfo=ZONA_HORARIA_EC)
    return (ahora - ultima_interaccion) > TIEMPO_MAX_SILENCIO
