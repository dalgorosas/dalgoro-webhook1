import json
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(__file__)
RUTA_JSON = os.path.join("dalgoro-webhook1", "estado_usuarios.json")

def cargar_estados():
    if not os.path.exists(RUTA_JSON):
        logger.error("❌ No existe el archivo estado_usuarios.json")
        return {}

    with open(RUTA_JSON, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            return data.get("_default", {})
        except Exception as e:
            logger.error("❌ Error al leer el archivo: %s", e)
            return {}

def guardar_estados(registros):
    with open(RUTA_JSON, "w", encoding="utf-8") as f:
        json.dump({"_default": registros}, f, indent=2)
        logger.info("✅ Archivo actualizado correctamente.")

def listar_estados(registros):
    if not registros:
        logger.info("✅ No hay registros actualmente.")
        return

    logger.info("📊 Hay %s registros:", len(registros))
    for k, estado in registros.items():
        logger.info(" - ID interno: %s | chat_id: %s | etapa: %s | actividad: %s", k, estado.get('chat_id'), estado.get('etapa'), estado.get('actividad'))

def eliminar_chat_id(registros, chat_id_objetivo):
    claves_a_eliminar = [k for k, e in registros.items() if e.get("chat_id") == chat_id_objetivo]
    if not claves_a_eliminar:
        logger.error("❌ No se encontró ese chat_id en los registros.")
        return registros

    for k in claves_a_eliminar:
        logger.info("🗑 Eliminando entrada: %s", registros[k])
        registros.pop(k)

    return registros

if __name__ == "__main__":
    estados = cargar_estados()
    listar_estados(estados)

    opcion = input("¿Deseas eliminar algún chat_id específico? (s/n): ").strip().lower()
    if opcion == "s":
        chat_id = input("🔢 Ingresa el chat_id completo (ej: 593xxxxxxxxx@c.us): ").strip()
        nuevos_estados = eliminar_chat_id(estados, chat_id)
        guardar_estados(nuevos_estados)
