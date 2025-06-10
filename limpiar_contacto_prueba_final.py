
import os
import json
import gspread
from google.oauth2.service_account import Credentials

# === CONFIGURACIÓN ===
CONTACTO_PRUEBA = "593984770663@c.us"  # Cambiar si usas otro número
CONTACTO_PURO = CONTACTO_PRUEBA.replace("@c.us", "")
RUTA_BASE = r"C:\Users\grdar\Desktop\bot_dalgoro\dalgoro-webhook1"
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
                print(f"✅ Eliminado {CONTACTO_PRUEBA} de {nombre_archivo}")
            else:
                print(f"ℹ️ {CONTACTO_PRUEBA} no está en {nombre_archivo}")
        else:
            print(f"⚠️ No existe el archivo: {ruta}")

def obtener_hoja(nombre_hoja):
    creds = Credentials.from_service_account_file(ARCHIVO_CREDENCIALES, scopes=SCOPES)
    cliente = gspread.authorize(creds)
    documento = cliente.open_by_key(ID_DOCUMENTO)
    return documento.worksheet(nombre_hoja)

def borrar_fila_por_campo(nombre_hoja, campo):
    hoja = obtener_hoja(nombre_hoja)
    datos = hoja.get_all_values()
    if not datos:
        print(f"⚠️ Hoja vacía: {nombre_hoja}")
        return

    headers = datos[0]
    if campo not in headers:
        print(f"⚠️ Campo '{campo}' no encontrado en hoja '{nombre_hoja}'")
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
    print(f"🗑️ {len(filas_a_borrar)} filas eliminadas en hoja '{nombre_hoja}' usando columna '{campo}'")

# === EJECUCIÓN ===
print("🔍 Iniciando limpieza local de JSONs...")
limpiar_json_local()

print("🧽 Iniciando limpieza de Google Sheets...")
borrar_fila_por_campo("Contactos", "Teléfono")
borrar_fila_por_campo("Mensajes", "ID_Contacto")
borrar_fila_por_campo("Estado", "chat_id")
borrar_fila_por_campo("Citas", "ID_Contacto")

print("✅ Limpieza de contacto de prueba completada.")
