from datetime import datetime
import os
import json
from tinydb import TinyDB, Query
from dateutil.parser import isoparse
from zona_horaria import ZONA_HORARIA_EC
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ruta del archivo de estado
db_path = 'estado_usuarios.json'

def limpiar_chat_id(chat_id):
    return chat_id.replace("@c.us", "").strip()

def cargar_db():
    if not os.path.exists(db_path):
        logger.info("📂 No existe estado_usuarios.json. Intentando reconstruir desde Sheets...")
        try:
            from google_sheets_utils import cargar_estados_desde_sheets
            estados = cargar_estados_desde_sheets()
            tmp_db = TinyDB(db_path)
            for estado in estados:
                tmp_db.insert(estado)
            tmp_db.close()
        except Exception as e:
            logger.warning("⚠️ Error al cargar desde Sheets: %s", e)
            with open(db_path, "w") as f:
                json.dump({}, f)
    else:
        with open(db_path, "r") as f:
            try:
                data = json.load(f)
                if isinstance(data, list):
                    logger.error("❌ Archivo corrupto (lista). Eliminando y regenerando...")
                    os.remove(db_path)
                    return cargar_db()
            except Exception:
                logger.error("❌ Archivo ilegible. Eliminando y regenerando...")
                os.remove(db_path)
                return cargar_db()

    return TinyDB(db_path)

# Inicializa la base de datos
db = cargar_db()
Conversacion = Query()

def obtener_estado(chat_id):
    logger.debug("🔎 Buscando estado para: %s", chat_id)
    chat_id = limpiar_chat_id(chat_id)
    raw_resultado = db.get(Conversacion.chat_id == chat_id)

    resultado = dict(raw_resultado) if raw_resultado else None

    if resultado:
        if "ultima_interaccion" in resultado:
            resultado["ultima_interaccion"] = isoparse(resultado["ultima_interaccion"])
        if "intentos_aclaracion" not in resultado:
            resultado["intentos_aclaracion"] = 0
        logger.info("✅ Estado encontrado: %s", resultado)
        return resultado
    else:
        nuevo = {
            "actividad": None,
            "etapa": None,
            "fase": "inicio",
            "ultima_interaccion": datetime.now(ZONA_HORARIA_EC).isoformat(),
            "intentos_aclaracion": 0
        }
        logger.info("🆕 Estado nuevo para %s: %s", chat_id, nuevo)
        return nuevo

def reiniciar_estado(chat_id):
    chat_id = limpiar_chat_id(chat_id)

    logger.info("🗑 Reiniciando estado para %s", chat_id)
    db.remove(Conversacion.chat_id == chat_id)
    guardar_estado(chat_id, {
        "actividad": None,
        "etapa": None,
        "fase": "inicio",
        "ultima_interaccion": datetime.now(ZONA_HORARIA_EC).isoformat(),
        "intentos_aclaracion": 0
    })

def obtener_estado_seguro(chat_id):
    chat_id = limpiar_chat_id(chat_id)

    try:
        return obtener_estado(chat_id)
    except Exception as e:
        logger.error("⚠️ Error al obtener estado para %s: %s", chat_id, e)
        return {
            "actividad": None,
            "etapa": None,
            "fase": "inicio",
            "ultima_interaccion": datetime.now(ZONA_HORARIA_EC).isoformat(),
            "intentos_aclaracion": 0
        }

       
def guardar_estado(chat_id, nuevo_estado):
    chat_id = limpiar_chat_id(chat_id)
    nuevo_estado["chat_id"] = chat_id
    nuevo_estado["ultima_interaccion"] = datetime.now(ZONA_HORARIA_EC).isoformat()
    logger.debug("📦 Estado a guardar en DB para %s: %s", chat_id, nuevo_estado)
    db.upsert(nuevo_estado, Conversacion.chat_id == chat_id)
    try:
        from google_sheets_utils import guardar_estado_en_sheets
        guardar_estado_en_sheets(chat_id, nuevo_estado)
    except Exception as e:
        logger.warning("⚠️ No se pudo guardar en Sheets: %s", e)

def mensaje_ya_procesado(chat_id, mensaje_id):
    chat_id = limpiar_chat_id(chat_id)

    estado = obtener_estado(chat_id)
    return estado.get("ultimo_mensaje_id") == mensaje_id

def registrar_mensaje_procesado(chat_id, mensaje_id):
    chat_id = limpiar_chat_id(chat_id) 

    estado = obtener_estado(chat_id)
    estado["ultimo_mensaje_id"] = mensaje_id
    guardar_estado(chat_id, estado)
