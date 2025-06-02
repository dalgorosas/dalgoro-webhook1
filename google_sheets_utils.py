import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS_FILE = "dalgoro-api-ea1fa305d0ca.json"
SHEET_ID = "tu_google_sheet_id"

def conectar_hoja(nombre_hoja):
    import os
from google.oauth2 import service_account

creds_dict = {
    "type": os.environ["service_account"],
    "project_id": os.environ["dalgoro-api"],
    "private_key_id": os.environ["ea1fa305d0caa07c4529e5363ede23fbabbb9196"],
    "private_key": os.environ["-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCNgce2cNJ1AneZ\nQtuyH+bCLvyyjMuSMFgCIef/bm+xvu7GCx7odybjfnJfuWgOd7XO8i1S29eJB3Mh\n+WwO1i6x+H/jEAJWb59avhPBX+VOV5rA5EGVrSKQw7rIga3rc99xPmu16ta891NQ\nNarkydC5cZDf8H1bhcn5J0hZhgQoYJ6rMl+5p5MtQRjY11hpe+bgXmdNiGg6LfYR\n5Lej63BkyBsd/JU6JVuY65gvZ148ckvskss5/hZQR4aLUZxxaiL8IBkJ2XjOgSmZ\nszMj5UCQfsxYq2su7ZZ18Umojlzaf/Y+H/Ht7jJs78Q5EYT7CdX4V+9Vzw6MqWMR\nURbJJuO7AgMBAAECggEADz9bsKSJg4LSNkPGU8mCM4xH6ElUKhq8G5wMWTFM0b88\nD+o6Lgb2EW9E4wb3AmVobrXDp85OdCfHAnMoxJR+5ZMG3LA96uhjfa3w3QD4lATL\n2lr+AiMXZWKMaXcnsVuD87oryvyp9M9Fko/7K7nfRrbI9d2o9Ef/PQc8PCvnnh4E\nv1wa+s35lNSkwyZMrB3yFYRa+yjEjLZXcEdYHNsLy4gHA5bXvK8ofGaQB7cpOETq\nPlzVHZVBDHaFzXtbrS/RWRroEe8EEU7iQrql8hndQARN3C+N4b+J50/Sn9BiR2Zp\n0FdmX3qIWjG8ocOM5mTedZ4UcmEwzSG9r1mg/AwmwQKBgQDByZzxIZxKFEdpWH/C\nfWihUtQxlywzi3YF8CLwJI0ismbob2lo94ejXAwIT8ScldOaSLY0Ym59YhTKRqUt\nJ+InIHFVKut2LH7b15ZgWJDfBmr41cNPr+WgDNTv6Gs2M7MD8QdDSGsa/XWsqDZk\n3gBHSjk4FA5vC471ByekylRI2wKBgQC6739tQX/9uXeXdi1e2i48Zo2QLciZEjv/\nsqDJrXBhvD8mTDElxrLAdXYEQb0vwcem+M9BW0/LhkFAM5GgaccRM4lPdYq3QMhg\nYbWmVYqdC59K2PQ8wKgA/VGxGE1SI0DDmvVGOIea4h1jxhE/+AtgEQhGA02jFOIc\n5GZovRrWoQKBgQCWWPN4aVk2aDFXXCATJvUsZHTY3K6gdwzkYoDYy6LsTnlk0Dt6\nAsGrTljPggPKcLuxMcSbM9sBUD1NCi5QsGbXcGY9a4UvNCpgKg0zRsNvJS2NTVuw\n0YlX+VyjnTDA5q922WOHIgJm+Ep54DADZfHVXZKzHWxtXwxUsm5hfdCSjQKBgQCn\ngJsJ5zssuteyXC5jY9UyQiJvItcwcepZQFJa5JJiwS9Evdj8JINfeOD7B3ziIh0o\nPKJZydxCXlZxlMPUnXPGsgtDq+tUMTRbSLJgDR5bgmKFyslu9qKT4Gkm6sO96eDK\nZTuKZHT+D8aN9JjYXQa0Wg6zzZnvm3LQuMga6ff2gQKBgHJzW7BmbhB4/ZMwK9Il\n+ngCZ/MplHrdkaARLtMu0oXOsJwfISc2WHbKm+IVLFBPPaj+6WYdf15fWwiuYXxV\nziFHJgpFgS8hmBf9uk3x7xWxfIq6Q1dJK+hIzF5N/xDPHLp3huWn5Mv8x/6lZ8jI\nhlpZsavSrJff2DVBazDihXVE\n-----END PRIVATE KEY-----\n"].replace("\\n", "\n"),
    "client_email": os.environ["accesogooglesheetsdalgoro@dalgoro-api.iam.gserviceaccount.com"],
    "client_id": os.environ["105165166183054127894"],
    "auth_uri": os.environ["https://accounts.google.com/o/oauth2/auth"],
    "token_uri": os.environ["https://oauth2.googleapis.com/token"],
    "auth_provider_x509_cert_url": os.environ["https://www.googleapis.com/oauth2/v1/certs"],
    "client_x509_cert_url": os.environ["https://www.googleapis.com/robot/v1/metadata/x509/accesogooglesheetsdalgoro%40dalgoro-api.iam.gserviceaccount.com"]
}

creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPE)
 
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
