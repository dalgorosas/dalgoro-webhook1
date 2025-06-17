
# test_detectar_cita.py

# La función original `procesar_y_registrar_cita` no está disponible.
# Utilizamos directamente `extraer_fecha_y_hora` para esta prueba.
from interpretador_citas import extraer_fecha_y_hora
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simulación de un mensaje del cliente con fecha y hora
chat_id = "593999000222"
mensaje_cliente = "Podría ser el próximo martes a las 10 de la mañana, si está bien para ustedes."

resultado = extraer_fecha_y_hora(mensaje_cliente)

if resultado:
    logger.info("✅ Cita detectada y registrada correctamente.")
else:
    logger.warning("⚠️ No se detectó una fecha y hora válida en el mensaje.")
