import gspread
import json
from google.oauth2.service_account import Credentials

# Leer archivo JSON de credenciales
with open("dalgoro-api-ea1fa305d0ca.json", "r") as f:
    cred_json = f.read()
cred_dict = json.loads(cred_json)

# Autenticación con Google Sheets API
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_info(cred_dict, scopes=scope)
client = gspread.authorize(credentials)

# 🟢 REEMPLAZA la URL con la real de tu hoja
url_hoja = "https://docs.google.com/spreadsheets/d/1RggJz98tnR86fo_AspwLWUVOIABn6vVrvojAkfQAqHc/edit?gid=0#gid=0"
spreadsheet = client.open_by_url(url_hoja)

# Seleccionar pestaña "Contactos"
worksheet = spreadsheet.worksheet("Contactos")

# Leer y mostrar primeras filas
filas = worksheet.get_all_values()
print("✅ Primeras 5 filas:")
for fila in filas[:5]:
    print(fila)
