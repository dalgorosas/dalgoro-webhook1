from tinydb import TinyDB, Query
from datetime import datetime

# Guardado en ruta persistente en Render
db = TinyDB("/mnt/data/estado_conversaciones.json")
Conversacion = Query()

def obtener_estado(chat_id):
    resultado = db.get(Conversacion.chat_id == chat_id)
    if resultado:
        return resultado
    else:
        return {
            "actividad": None,
            "etapa": None,
            "fase": "inicio",
            "ultima_interaccion": datetime.now().isoformat()
        }

def guardar_estado(chat_id, nuevo_estado):
    nuevo_estado["chat_id"] = chat_id
    db.upsert(nuevo_estado, Conversacion.chat_id == chat_id)

def reiniciar_estado(chat_id):
    db.remove(Conversacion.chat_id == chat_id)
