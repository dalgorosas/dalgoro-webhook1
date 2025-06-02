import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Ámbitos de acceso autorizados para trabajar con Google Sheets y Drive
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Leer el ID de la hoja desde variable de entorno
SHEET_ID = os.getenv("GOOGLE_SHEET_ID")


def obtener_credenciales():
    """Carga las credenciales desde la variable de entorno GOOGLE_CREDENTIALS_JSON"""
    try:
        json_keyfile = os.getenv("GOOGLE_CREDENTIALS_JSON")
        if not json_keyfile:
            raise ValueError("La variable de entorno GOOGLE_CREDENTIALS_JSON no está definida.")
        creds_dict = json.loads(json_keyfile)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
        return creds
    except Exception as e:
        print("❌ Error cargando credenciales:", e)
        raise


def conectar_hoja(nombre_hoja):
    """Conecta con una hoja específica por nombre"""
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
            print("❌ Error al registrar mensaje:", e)
            return False

    def get_analytics_data(self):
        mensajes = self.mensajes.get_all_records()
        return {
            "total_mensajes": len(mensajes),
            "enviados": sum(1 for m in mensajes if m["Tipo"] == "Enviado"),
            "recibidos": sum(1 for m in mensajes if m["Tipo"] == "Recibido")
        }


# Instancia global para usar en otras partes del sistema
sheets_manager = SheetsManager()
