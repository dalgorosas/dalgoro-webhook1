
import os
import json
import gspread
from google.oauth2.service_account import Credentials
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === CONFIGURACIÓN ===
CONTACTO_PRUEBA = "593984770663@c.us"  # Cambiar si usas otro número
CONTACTO_PURO = CONTACTO_PRUEBA.replace("@c.us", "")
# Directorio base del proyecto
RUTA_BASE = os.path.dirname(os.path.abspath(__file__))
ARCHIVOS_JSON = [
    "mensajes_recientes.json",
    "bloqueos.json",
    "estado_conversaciones.json",
    "estado_usuarios.json"
]
ARCHIVO_CREDENCIALES = "credenciales.json"
ID_DOCUMENTO = "1RggJz98tnR86fo_AspwLWUVOIABn6vVrvojAkfQAqHc"
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

# === FUNCIONES ===

def limpiar_json_local():
    for nombre_archivo in ARCHIVOS_JSON:
        ruta = os.path.join(RUTA_BASE, nombre_archivo)
        if os.path.exists(ruta):
            with open(ruta, "r", encoding="utf-8") as f:
                data = json.load(f)
            if CONTACTO_PRUEBA in data:
                del data[CONTACTO_PRUEBA]
                with open(ruta, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                logger.info("✅ Eliminado %s de %s", CONTACTO_PRUEBA, nombre_archivo)
            else:
                logger.info("ℹ️ %s no está en %s", CONTACTO_PRUEBA, nombre_archivo)
        else:
            logger.warning("⚠️ No existe el archivo: %s", ruta)

def obtener_hoja(nombre_hoja):
    creds = Credentials.from_service_account_file(ARCHIVO_CREDENCIALES, scopes=SCOPES)
    cliente = gspread.authorize(creds)
    documento = cliente.open_by_key(ID_DOCUMENTO)
    return documento.worksheet(nombre_hoja)

def borrar_fila_por_campo(nombre_hoja, campo):
    hoja = obtener_hoja(nombre_hoja)
    datos = hoja.get_all_values()
    if not datos:
        logger.warning("⚠️ Hoja vacía: %s", nombre_hoja)
        return

    headers = datos[0]
    if campo not in headers:
        logger.warning("⚠️ Campo '%s' no encontrado en hoja '%s'", campo, nombre_hoja)
        return

    index = headers.index(campo)
    filas_a_borrar = []

    for i, fila in enumerate(datos[1:], start=2):  # desde fila 2 en adelante
        if len(fila) <= index:
            continue
        valor = fila[index].strip()
        if CONTACTO_PURO in valor or CONTACTO_PRUEBA in valor:
            filas_a_borrar.append(i)

    for i in reversed(filas_a_borrar):
        hoja.delete_rows(i)
    logger.info("🗑️ %s filas eliminadas en hoja '%s' usando columna '%s'", len(filas_a_borrar), nombre_hoja, campo)

# === EJECUCIÓN ===
logger.info("🔍 Iniciando limpieza local de JSONs...")
limpiar_json_local()

logger.info("🔍 Iniciando limpieza local de JSONs...")
borrar_fila_por_campo("Contactos", "Teléfono")
borrar_fila_por_campo("Mensajes", "ID_Contacto")
borrar_fila_por_campo("Estado", "chat_id")
borrar_fila_por_campo("Citas", "ID_Contacto")

logger.info("✅ Limpieza de contacto de prueba completada.")
