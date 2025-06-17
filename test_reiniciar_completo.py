import os
import json
import gspread
from google.oauth2.service_account import Credentials
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Autenticación
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
ARCHIVO_CREDENCIALES = "credenciales.json"
ID_DOCUMENTO = "1RggJz98tnR86fo_AspwLWUVOIABn6vVrvojAkfQAqHc"

def obtener_hoja(nombre_hoja):
    creds = Credentials.from_service_account_file(ARCHIVO_CREDENCIALES, scopes=SCOPES)
    cliente = gspread.authorize(creds)
    documento = cliente.open_by_key(ID_DOCUMENTO)
    return documento.worksheet(nombre_hoja)

# Archivos locales
ARCHIVOS_A_ELIMINAR = ["mensajes_recientes.json", "bloqueos.json", "estado_conversaciones.json", "estado_usuarios.json"]
# Ruta al archivo estado_usuarios.json dentro del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ARCHIVO_A_VACIAR = os.path.join(BASE_DIR, "estado_usuarios.json")

# Eliminar archivos innecesarios
for archivo in ARCHIVOS_A_ELIMINAR:
    if os.path.exists(archivo):
        os.remove(archivo)
        logger.info("🧹 Archivo eliminado: %s", archivo)
    else:
        logger.info("ℹ️ Archivo no encontrado (ya estaba limpio): %s", archivo)

# Vaciar contenido de estado_usuarios.json
if os.path.exists(ARCHIVO_A_VACIAR):
    with open(ARCHIVO_A_VACIAR, "w", encoding="utf-8") as f:
        json.dump({}, f)
    logger.info("🧽 Archivo limpiado: %s", ARCHIVO_A_VACIAR)
else:
    logger.warning("⚠️ %s no existe. Creando archivo vacío...", ARCHIVO_A_VACIAR)
    with open(ARCHIVO_A_VACIAR, "w", encoding="utf-8") as f:
        json.dump({}, f)

# Borrar contenido de hojas de cálculo
def borrar_hoja_completa(nombre_hoja):
    hoja = obtener_hoja(nombre_hoja)
    datos = hoja.get_all_values()
    if len(datos) > 1:
        hoja.delete_rows(2, len(datos))
        logger.info("🗑️ Borradas %s filas en hoja: %s", len(datos)-1, nombre_hoja)
    else:
        logger.info("✅ Hoja %s ya está vacía.", nombre_hoja)

logger.info("🧼 Limpiando Google Sheets...")
for nombre in ["Estado", "Mensajes", "Citas", "Contactos"]:
    borrar_hoja_completa(nombre)

logger.info("✅ Reinicio completo del sistema exitoso.")
