import os
import json
import gspread
from google.oauth2.service_account import Credentials

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
ARCHIVO_A_VACIAR = r"C:\Users\grdar\Desktop\bot_dalgoro\dalgoro-webhook1\estado_usuarios.json"

# Eliminar archivos innecesarios
for archivo in ARCHIVOS_A_ELIMINAR:
    if os.path.exists(archivo):
        os.remove(archivo)
        print(f"🧹 Archivo eliminado: {archivo}")
    else:
        print(f"ℹ️ Archivo no encontrado (ya estaba limpio): {archivo}")

# Vaciar contenido de estado_usuarios.json
if os.path.exists(ARCHIVO_A_VACIAR):
    with open(ARCHIVO_A_VACIAR, "w", encoding="utf-8") as f:
        json.dump({}, f)
    print(f"🧽 Archivo limpiado: {ARCHIVO_A_VACIAR}")
else:
    print(f"⚠️ {ARCHIVO_A_VACIAR} no existe. Creando archivo vacío...")
    with open(ARCHIVO_A_VACIAR, "w", encoding="utf-8") as f:
        json.dump({}, f)

# Borrar contenido de hojas de cálculo
def borrar_hoja_completa(nombre_hoja):
    hoja = obtener_hoja(nombre_hoja)
    datos = hoja.get_all_values()
    if len(datos) > 1:
        hoja.delete_rows(2, len(datos))
        print(f"🗑️ Borradas {len(datos)-1} filas en hoja: {nombre_hoja}")
    else:
        print(f"✅ Hoja {nombre_hoja} ya está vacía.")

print("🧼 Limpiando Google Sheets...")
for nombre in ["Estado", "Mensajes", "Citas", "Contactos"]:
    borrar_hoja_completa(nombre)

print("✅ Reinicio completo del sistema exitoso.")
