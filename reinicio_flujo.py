
# reinicio_flujo.py

import datetime

TIEMPO_MAX_SILENCIO = datetime.timedelta(days=3, minutes=30)

def debe_reiniciar_flujo(ultima_interaccion: datetime.datetime, ahora: datetime.datetime) -> bool:
    """
    Determina si se debe reiniciar el flujo por nueva actividad del cliente
    después del período de silencio definido.
    """
    return (ahora - ultima_interaccion) > TIEMPO_MAX_SILENCIO
