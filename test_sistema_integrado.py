# test_sistema_integrado.py

from datetime import datetime
from zona_horaria import ZONA_HORARIA_EC
from gestor_conversacion import manejar_conversacion, reiniciar_conversacion
from estado_storage import obtener_estado_seguro
from pprint import pformat
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def probar_flujo_completo(chat_id, mensajes_usuario):
    logger.info("\n📲 Iniciando simulación para: %s", chat_id)
    reiniciar_conversacion(chat_id)

    actividad = None  # Variable dinámica por si se detecta automáticamente

    for mensaje in mensajes_usuario:
        logger.info("\n👤 Usuario: %s", mensaje)
        respuesta = manejar_conversacion(
            chat_id,
            mensaje,
            actividad=actividad,
            fecha_actual=datetime.now(ZONA_HORARIA_EC)
        )
        if respuesta:
            logger.info("🤖 Bot: %s", respuesta)
        else:
            logger.warning("🤖 Bot no respondió (posible bloqueo o duplicado)")

        # Verificar si se detectó una actividad nueva desde estado
        estado = obtener_estado_seguro(chat_id)
        if estado.get("actividad"):
            actividad = estado["actividad"]

    logger.info("\n📦 Estado final almacenado:")
    estado = obtener_estado_seguro(chat_id)
    logger.info(pformat(estado))

# 🧪 Escenarios de prueba
pruebas = {
    "cliente_1": [
        "Hola",
        "Tengo una finca bananera",
        "Sí tengo permiso",
        "Puedo el jueves a las 10am en oficina",
    ],
    "cliente_2": [
        "Hola, necesito ayuda",
        "es una camaronera",
        "No tengo ningún permiso aún",
        "pueden venir el viernes a las 8am a la finca",
    ],
    "cliente_3": [
        "Hola",
        "Trabajo con cacao",
        "ya tengo todo en regla",
        "el lunes a las 14:00 está bien en oficina",
    ],
    "cliente_4": [
        "buenas tardes",
        "ninguna de las anteriores",
        "cultivo de ciclo corto",
        "sí, tengo permiso",
        "agendemos el martes a las 9am",
    ],
}

# 🔁 Ejecutar todas las pruebas
for chat_id, mensajes in pruebas.items():
    probar_flujo_completo(chat_id, mensajes)
