import os
import json
import re
import logging
import gspread
from google.oauth2.service_account import Credentials

# === CONFIGURACIÓN ===
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
ARCHIVO_CREDENCIALES = "credenciales.json"
ID_DOCUMENTO = "1RggJz98tnR86fo_AspwLWUVOIABn6vVrvojAkfQAqHc"
ARCHIVO_ESTADO = "estado_usuarios.json"
HOJAS_A_LIMPIAR = ["Citas", "Estado", "Mensajes", "Contactos"]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def obtener_hoja(nombre_hoja):
    creds = Credentials.from_service_account_file(ARCHIVO_CREDENCIALES, scopes=SCOPES)
    cliente = gspread.authorize(creds)
    documento = cliente.open_by_key(ID_DOCUMENTO)
    return documento.worksheet(nombre_hoja)

def limpiar_estado_json(chat_id):
    if not os.path.exists(ARCHIVO_ESTADO):
        logger.warning("⚠️ Archivo %s no existe.", ARCHIVO_ESTADO)
        return

    with open(ARCHIVO_ESTADO, "r", encoding="utf-8") as f:
        datos = json.load(f)

    if chat_id in datos:
        del datos[chat_id]
        with open(ARCHIVO_ESTADO, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
        logger.info("🧹 Eliminado estado de %s en %s", chat_id, ARCHIVO_ESTADO)
    else:
        logger.info("ℹ️ No se encontró estado para %s en %s", chat_id, ARCHIVO_ESTADO)

def limpiar_contacto_en_hoja(nombre_hoja, chat_id):
    numero_limpio = re.sub(r"\D", "", chat_id.split("@")[0])
    hoja = obtener_hoja(nombre_hoja)
    datos = hoja.get_all_values()

    filas_a_borrar = []
    for i, fila in enumerate(datos[1:], start=2):  # desde fila 2
        if len(fila) > 0 and numero_limpio in fila[0]:
            filas_a_borrar.append(i)

    for i in reversed(filas_a_borrar):
        hoja.delete_rows(i)

    if filas_a_borrar:
        logger.info("🗑️ Borradas %s filas en hoja '%s' para número %s", len(filas_a_borrar), nombre_hoja, numero_limpio)
    else:
        logger.info("✅ Hoja '%s' ya estaba limpia para %s", nombre_hoja, numero_limpio)

def reiniciar_contacto(chat_id):
    logger.info("🔄 Iniciando limpieza completa para contacto: %s", chat_id)

    limpiar_estado_json(chat_id)

    for hoja in HOJAS_A_LIMPIAR:
        limpiar_contacto_en_hoja(hoja, chat_id)

    logger.info("✅ Contacto %s reiniciado completamente en todas las fuentes.", chat_id)

# 🧪 USO DIRECTO (descomenta para probar):
# reiniciar_contacto("593987654321@c.us")
