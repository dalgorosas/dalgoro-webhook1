import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = "dalgoro-api-e50c0157c814.json"
SHEET_ID = "tu_google_sheet_id"

def conectar_hoja(nombre_hoja):
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDS_FILE, SCOPE)
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

sheets_manager = SheetsManager()
