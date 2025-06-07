from datetime import datetime
import os
import json
from tinydb import TinyDB, Query
from pytz import timezone
from dateutil.parser import isoparse

# Ruta del archivo de estado
db_path = 'estado_usuarios.json'

# Verifica y crea el archivo si no existe, intentando respaldo desde Google Sheets
if not os.path.exists(db_path):
    print("⚠️ El archivo estado_usuarios.json no existe. Intentando cargar desde Google Sheets...")
    try:
        from google_sheets_utils import cargar_estados_desde_sheets
        estados_remotos = cargar_estados_desde_sheets()
        with open(db_path, 'w') as f:
            json.dump(estados_remotos, f)
        print("✅ Archivo creado desde backup de Sheets.")
    except Exception as e:
        print(f"❌ Error cargando desde Sheets: {e}")
        open(db_path, 'w').close()

# Inicializa la base de datos local
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
    zona_ecuador = timezone('America/Guayaquil')
    nuevo_estado["ultima_interaccion"] = datetime.now(zona_ecuador).isoformat()
    print(f"📦 Estado a guardar en DB para {chat_id}: {nuevo_estado}")
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

def obtener_estado_seguro(chat_id):
    try:
        return obtener_estado(chat_id)
    except Exception as e:
        print(f"⚠️ Error al obtener estado para {chat_id}: {e}")
        return {
            "actividad": None,
            "etapa": None,
            "fase": "inicio",
            "ultima_interaccion": datetime.now().isoformat()
        }
