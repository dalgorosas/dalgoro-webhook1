import gspread
import os
import json
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# Ámbitos de acceso para Google Sheets y Drive
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# ID del Google Sheet (reemplaza con tu ID real)
SHEET_ID = "1RggJz98tnR86fo_AspwLWUVOIABn6vVrvojAkfQAqHc"

def obtener_credenciales():
    cred_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if not cred_json:
        raise ValueError("La variable de entorno GOOGLE_CREDENTIALS_JSON no está definida.")
    cred_dict = json.loads(cred_json)
    return ServiceAccountCredentials.from_json_keyfile_dict(cred_dict, SCOPE)

def conectar_hoja(nombre_hoja):
    creds = obtener_credenciales()
    cliente = gspread.authorize(creds)
    hoja = cliente.open_by_key(SHEET_ID).worksheet(nombre_hoja)
    return hoja

class SheetsManager:
    def __init__(self):
        self.contactos = conectar_hoja("Contactos")
        self.mensajes = conectar_hoja("Mensajes")

    def update_contact(self, telefono):
        contactos = self.contactos.get_all_records()
        if not any(c["Teléfono"] == telefono for c in contactos):
            self.contactos.append_row([telefono, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])

    def log_message(self, telefono, mensaje, tipo, canal):
        try:
            self.mensajes.append_row([
                telefono,
                mensaje,
                tipo,
                canal,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ])
            return True
        except Exception as e:
            print("Error al registrar mensaje:", e)
            return False

    def get_analytics_data(self):
        mensajes = self.mensajes.get_all_records()
        return {
            "total_mensajes": len(mensajes),
            "enviados": sum(1 for m in mensajes if m["Tipo"] == "Enviado"),
            "recibidos": sum(1 for m in mensajes if m["Tipo"] == "Recibido")
        }

# Instancia global
sheets_manager = SheetsManager()
