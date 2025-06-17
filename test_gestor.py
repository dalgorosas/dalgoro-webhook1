
# test_gestor.py

from datetime import datetime, timedelta
from gestor_conversacion import manejar_conversacion
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Simular prueba completa del flujo con múltiples escenarios
def ejecutar_pruebas():
    ahora = datetime.now()

    casos = [
        {
            "descripcion": "🔁 Cliente reaparece luego de 4 días sin contacto",
            "chat_id": "123",
            "mensaje": "Hola, disculpe que no respondí antes",
            "actividad_actual": "bananera",
            "ultima_interaccion": ahora - timedelta(days=4)
        },
        {
            "descripcion": "📅 Cliente propone una cita en el mensaje",
            "chat_id": "456",
            "mensaje": "Me gustaría agendar para el próximo martes a las 10am",
            "actividad_actual": "camaronera",
            "ultima_interaccion": ahora - timedelta(minutes=15)
        },
        {
            "descripcion": "📚 Cliente dentro del flujo normal con actividad definida",
            "chat_id": "789",
            "mensaje": "¿Qué documentos necesito?",
            "actividad_actual": "minería",
            "ultima_interaccion": ahora - timedelta(minutes=20)
        },
        {
            "descripcion": "💬 Cliente inicia por primera vez sin actividad detectada",
            "chat_id": "001",
            "mensaje": "Hola, necesito ayuda para mi finca",
            "actividad_actual": None,
            "ultima_interaccion": None
        },
        {
            "descripcion": "🤖 Actividad no reconocida o aún sin respuestas",
            "chat_id": "002",
            "mensaje": "Trabajo en ganadería",
            "actividad_actual": "ganadería",
            "ultima_interaccion": ahora - timedelta(minutes=10)
        }
    ]

    for caso in casos:
        logger.info("\n%s", caso['descripcion'])
        respuesta = manejar_conversacion(
            caso['chat_id'],
            caso['mensaje'],
            caso['actividad_actual'],
            caso['ultima_interaccion']
        )
        logger.info("📨 Respuesta del bot: %s", respuesta.strip())

if __name__ == "__main__":
    ejecutar_pruebas()
