import gspread
import os
import json
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
SHEET_ID = "1RggJz98tnR86fo_AspwLWUVOIABn6vVrvojAkfQAqHc"  # Tu ID real

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
        registros = self.contactos.get_all_records()
        if not any(c["ID"] == telefono for c in registros):
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.contactos.append_row([telefono, now])

    def log_message(self, telefono, mensaje, tipo, canal):
        try:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.mensajes.append_row([
                telefono,       # ID_Contacto
                now,            # Fecha
                tipo,           # Tipo: "Recibido" o "Enviado"
                canal,          # Canal: "WhatsApp"
                mensaje,        # Mensaje
                "Pendiente",    # Estado_Respuesta
                "Sí",           # Automatizado
                "Bot",          # Responsable
                ""              # Observaciones
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
