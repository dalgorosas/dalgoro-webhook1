from datetime import datetime
import os
from tinydb import TinyDB, Query
from pytz import timezone
from dateutil.parser import isoparse

# Verifica y crea el archivo si no existe
db_path = 'estado_conversaciones.json'
if not os.path.exists(db_path):
    open(db_path, 'w').close()

db = TinyDB(db_path)
Conversacion = Query()

def obtener_estado(chat_id):
    print(f"🔎 Buscando estado para: {chat_id}")
    resultado = db.get(Conversacion.chat_id == chat_id)

    if resultado:
        if "ultima_interaccion" in resultado:
            resultado["ultima_interaccion"] = isoparse(resultado["ultima_interaccion"])
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
    # Actualiza siempre la hora local de interacción
    zona_ecuador = timezone('America/Guayaquil')
    nuevo_estado["ultima_interaccion"] = datetime.now(zona_ecuador).isoformat()
    
    print(f"📦 Estado a guardar en DB para {chat_id}: {nuevo_estado}")  # 👈 LÍNEA NUEVA
    db.upsert(nuevo_estado, Conversacion.chat_id == chat_id)

def reiniciar_estado(chat_id):
    print(f"🗑 Reiniciando estado para {chat_id}")
    db.remove(Conversacion.chat_id == chat_id)
    guardar_estado(chat_id, {
        "actividad": None,
        "etapa": None,
        "fase": "inicio",
        "ultima_interaccion": datetime.now().isoformat()
    })
