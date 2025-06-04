from gestor_conversacion import manejar_conversacion
from datetime import datetime, timedelta

casos = [
    {
        "descripcion": "Solo actividad, sin decirla claramente",
        "chat_id": "cliente_001",
        "mensaje": "Tengo una finca y necesito una evaluación ambiental",
        "actividad_detectada": None,
        "ultima_interaccion": datetime.now() - timedelta(minutes=5),
    },
    {
        "descripcion": "Menciona cita con lenguaje informal",
        "chat_id": "cliente_002",
        "mensaje": "Nos podríamos ver el lunes a eso de las 10",
        "actividad_detectada": None,
        "ultima_interaccion": datetime.now() - timedelta(minutes=10),
    },
    {
        "descripcion": "Mezcla actividad y cita",
        "chat_id": "cliente_003",
        "mensaje": "Mi actividad es minería y podríamos hablar el miércoles a las 2",
        "actividad_detectada": "minería",
        "ultima_interaccion": datetime.now() - timedelta(minutes=12),
    },
    {
        "descripcion": "Usa términos vagos",
        "chat_id": "cliente_004",
        "mensaje": "Quiero cumplir con lo del ministerio",
        "actividad_detectada": None,
        "ultima_interaccion": datetime.now() - timedelta(minutes=7),
    },
    {
        "descripcion": "Reaparece luego de varios días",
        "chat_id": "cliente_005",
        "mensaje": "Disculpe que no respondí antes, ¿aún puedo agendar?",
        "actividad_detectada": None,
        "ultima_interaccion": datetime.now() - timedelta(days=4),
    },
]

def ejecutar_pruebas():
    for caso in casos:
        print(f"🔍 {caso['descripcion']}")
        respuesta = manejar_conversacion(
            caso["chat_id"],
            caso["mensaje"],
            caso["actividad_detectada"],
            caso["ultima_interaccion"]
        )
        print("📨 Respuesta del bot:", respuesta)
        print("-" * 50)

if __name__ == "__main__":
    ejecutar_pruebas()
