import os
import gspread
from google.oauth2.service_account import Credentials

# Autenticación directa (usa tus credenciales locales ya configuradas)
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
ARCHIVO_CREDENCIALES = "credenciales.json"
ID_DOCUMENTO = "1RggJz98tnR86fo_AspwLWUVOIABn6vVrvojAkfQAqHc"

def obtener_hoja(nombre_hoja):
    creds = Credentials.from_service_account_file(ARCHIVO_CREDENCIALES, scopes=SCOPES)
    cliente = gspread.authorize(creds)
    documento = cliente.open_by_key(ID_DOCUMENTO)
    return documento.worksheet(nombre_hoja)

# Eliminar archivos locales
ARCHIVOS = ["estado_usuarios.json", "mensajes_recientes.json", "bloqueos.json"]
for archivo in ARCHIVOS:
    if os.path.exists(archivo):
        os.remove(archivo)
        print(f"🧹 Archivo eliminado: {archivo}")
    else:
        print(f"ℹ️ Archivo no encontrado (ya estaba limpio): {archivo}")

# Borrar hojas remotas
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
