from datetime import datetime, timedelta

# Diccionario para guardar el historial de mensajes por usuario
historial_mensajes = {}

# Diccionario para manejar los bloqueos activos
bloqueos_temporales = {}

# Tiempo mínimo entre mensajes iguales del mismo usuario
TIEMPO_BLOQUEO = timedelta(seconds=60)

def normalizar(texto):
    """Limpia y normaliza un mensaje para comparación."""
    return texto.strip().lower()

def mensaje_duplicado(chat_id, mensaje, historial=historial_mensajes):
    """Verifica si el mensaje ya fue enviado recientemente por este usuario."""
    ahora = datetime.now()
    mensaje_normalizado = normalizar(mensaje)

    if chat_id in historial:
        mensaje_anterior, timestamp = historial[chat_id]
        if mensaje_normalizado == mensaje_anterior and (ahora - timestamp) < TIEMPO_BLOQUEO:
            return True
    return False

def registrar_mensaje(chat_id, mensaje, historial=historial_mensajes):
    """Registra un nuevo mensaje para evitar duplicados posteriores."""
    historial[chat_id] = (normalizar(mensaje), datetime.now())

def activar_bloqueo(chat_id):
    """Activa un bloqueo temporal para un usuario."""
    bloqueos_temporales[chat_id] = datetime.now()

def bloqueo_activo(chat_id):
    """Verifica si hay un bloqueo activo para este usuario."""
    if chat_id in bloqueos_temporales:
        tiempo_desde_bloqueo = datetime.now() - bloqueos_temporales[chat_id]
        if tiempo_desde_bloqueo < TIEMPO_BLOQUEO:
            return True
        else:
            # El bloqueo ya expiró
            bloqueos_temporales.pop(chat_id)
    return False
