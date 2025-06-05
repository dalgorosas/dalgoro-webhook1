from tinydb import TinyDB, Query
from datetime import datetime
import os

# Ruta segura para Render (persistente)
db_path = "/mnt/data/estado_conversaciones.json"
print(f"📂 Verificando archivo de estado: {db_path} → Existe: {os.path.exists(db_path)}")
db = TinyDB(db_path)
Conversacion = Query()

def obtener_estado(chat_id):
    print(f"🔎 Buscando estado para: {chat_id}")
    resultado = db.get(Conversacion.chat_id == chat_id)
    if resultado:
        print(f"✅ Estado encontrado: {resultado}")
        return resultado
    else:
        nuevo = {
            "actividad": None,
            "etapa": None,
            "fase": "inicio",
            "ultima_interaccion": datetime.now().isoformat()
        }
        print(f"🆕 Estado nuevo para {chat_id}: {nuevo}")
        return nuevo

def guardar_estado(chat_id, nuevo_estado):
    nuevo_estado["chat_id"] = chat_id
    print(f"💾 Guardando estado para {chat_id}: {nuevo_estado}")
    db.upsert(nuevo_estado, Conversacion.chat_id == chat_id)

def reiniciar_estado(chat_id):
    print(f"🗑 Reiniciando estado para {chat_id}")
    db.remove(Conversacion.chat_id == chat_id)
