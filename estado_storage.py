from datetime import datetime
import os
import json
from tinydb import TinyDB, Query
from pytz import timezone
from dateutil.parser import isoparse

# Ruta del archivo de estado
db_path = 'estado_usuarios.json'

def cargar_db():
    if not os.path.exists(db_path):
        print("📂 No existe estado_usuarios.json. Intentando reconstruir desde Sheets...")
        try:
            from google_sheets_utils import cargar_estados_desde_sheets
            estados = cargar_estados_desde_sheets()
            with open(db_path, "w") as f:
                json.dump({"_default": {str(i + 1): e for i, e in enumerate(estados)}}, f)
        except Exception as e:
            print(f"⚠️ Error al cargar desde Sheets: {e}")
            with open(db_path, "w") as f:
                json.dump({}, f)

    else:
        with open(db_path, "r") as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    print("❌ Archivo corrupto (lista). Eliminando y regenerando...")
                    os.remove(db_path)
                    return cargar_db()
            except Exception as e:
                print("❌ Archivo ilegible. Eliminando y regenerando...")
                os.remove(db_path)
                return cargar_db()

    return TinyDB(db_path)

# Inicializa la base de datos
db = cargar_db()
Conversacion = Query()


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
    try:
        from google_sheets_utils import guardar_estado_en_sheets
        guardar_estado_en_sheets(chat_id, nuevo_estado)
    except Exception as e:
        print(f"⚠️ No se pudo guardar en Sheets: {e}")

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

def mensaje_ya_procesado(chat_id, mensaje_id):
    estado = obtener_estado(chat_id)
    return estado.get("ultimo_mensaje_id") == mensaje_id

def registrar_mensaje_procesado(chat_id, mensaje_id):
    estado = obtener_estado(chat_id)
    estado["ultimo_mensaje_id"] = mensaje_id
    guardar_estado(chat_id, estado)
