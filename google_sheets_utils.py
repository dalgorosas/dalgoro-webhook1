import os
import json
import gspread
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials
import pytz
from datetime import timezone, timedelta
ZONA_HORARIA_EC = timezone(timedelta(hours=-5))


# Ámbitos de acceso para Google Sheets y Drive
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

def agregar_fila_a_hoja(nombre_hoja, fila):
    hoja = conectar_hoja(nombre_hoja)
    hoja.append_row(fila)

# ID del Google Sheet (reemplaza con tu ID real)
SHEET_ID = "1RggJz98tnR86fo_AspwLWUVOIABn6vVrvojAkfQAqHc"

def guardar_estado_en_sheets(chat_id, estado):
    hoja = conectar_hoja("Estado")
    registros = hoja.get_all_records()
    encontrados = [i for i, fila in enumerate(registros) if str(fila.get("chat_id", "")).strip() == chat_id.strip()]

    fila_nueva = {
        "chat_id": chat_id,
        "actividad": estado.get("actividad", ""),
        "etapa": estado.get("etapa", ""),
        "fase": estado.get("fase", ""),
        "ultima_interaccion": str(estado.get("ultima_interaccion", "")),
        "ultimo_mensaje_id": estado.get("ultimo_mensaje_id", "")
    }

    if encontrados:
        idx = encontrados[0] + 2
        hoja.update(f"A{idx}:F{idx}", [[
            fila_nueva["chat_id"],
            fila_nueva["actividad"],
            fila_nueva["etapa"],
            fila_nueva["fase"],
            fila_nueva["ultima_interaccion"],
            fila_nueva["ultimo_mensaje_id"]
        ]])
        print(f"🔁 Estado actualizado en fila {idx} de Sheets.")
    else:
        hoja.append_row(list(fila_nueva.values()))
        print(f"➕ Estado nuevo registrado en Sheets para {chat_id}.")

def obtener_credenciales():
    try:
        # INTENTO 1: usar variable de entorno si está bien cargada
        cred_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
        if cred_json and cred_json.strip():
            cred_dict = json.loads(cred_json)
            return ServiceAccountCredentials.from_json_keyfile_dict(cred_dict, SCOPE)
    except Exception as e:
        print(f"⚠️ Variable de entorno no válida. Motivo: {e}")

    # INTENTO 2: modo local con archivo JSON
    print("🗂️ Usando archivo local de credenciales.")
    with open("dalgoro-api-ea1fa305d0ca.json", "r", encoding="utf-8") as f:
        cred_dict = json.load(f)
    return ServiceAccountCredentials.from_json_keyfile_dict(cred_dict, SCOPE)

def conectar_hoja(nombre_hoja):
    creds = obtener_credenciales()
    cliente = gspread.authorize(creds)

    # Reemplaza esta URL con la URL real de tu Google Sheet
    url_hoja = "https://docs.google.com/spreadsheets/d/1RggJz98tnR86fo_AspwLWUVOIABn6vVrvojAkfQAqHc/edit#gid=0"

    hoja = cliente.open_by_url(url_hoja).worksheet(nombre_hoja)
    return hoja

def cargar_estados_desde_sheets():
    hoja = conectar_hoja("Estado")
    registros = hoja.get_all_records()

    estados = []
    for fila in registros:
        estados.append({
            "chat_id": str(fila.get("chat_id", "")).strip(),
            "actividad": fila.get("actividad", ""),
            "etapa": fila.get("etapa", ""),
            "fase": fila.get("fase", ""),
            "ultima_interaccion": fila.get("ultima_interaccion", ""),
            "ultimo_mensaje_id": fila.get("ultimo_mensaje_id", "")
        })
    print(f"✅ Se cargaron {len(estados)} estados desde Sheets.")
    return estados

class SheetsManager:
    def __init__(self):
        self.contactos = conectar_hoja("Contactos")
        self.mensajes = conectar_hoja("Mensajes")

    def update_contact(self, telefono):
        contactos = self.contactos.get_all_records()
        if not any(c["Teléfono"] == telefono for c in contactos):
            self.contactos.append_row([telefono, datetime.now(ZONA_HORARIA_EC).strftime("%Y-%m-%d %H:%M:%S")])

    def log_message(self, telefono, mensaje, tipo, canal):
        try:
            hoja = conectar_hoja("Mensajes")
            ahora = datetime.now(ZONA_HORARIA_EC).strftime("%Y-%m-%d %H:%M:%S")
            hoja.append_row([
                telefono,      # A - Teléfono
                ahora,         # B - Fecha
                tipo,          # C - Tipo
                canal,         # D - Canal
                mensaje,       # E - Mensaje
            ])
            return True
        except Exception as e:
            print("Error al registrar mensaje:", e)
            return False

def registrar_mensaje(chat_id, mensaje, tipo, canal):
    from datetime import datetime
    hoja = conectar_hoja("Mensajes")
    ahora = datetime.now(ZONA_HORARIA_EC).strftime("%Y-%m-%d %H:%M:%S")  # ✅ Correcto
    hoja.append_row([
        chat_id,    # A - Teléfono
        ahora,      # B - Fecha
        tipo,       # C - Tipo
        canal,      # D - Canal
        mensaje,    # E - Mensaje
    ])

    def get_analytics_data(self):
        mensajes = self.mensajes.get_all_records()
        return {
            "total_mensajes": len(mensajes),
            "enviados": sum(1 for m in mensajes if m["Tipo"] == "Enviado"),
            "recibidos": sum(1 for m in mensajes if m["Tipo"] == "Recibido")
        }

# Instancia global
sheets_manager = SheetsManager()

# ----------------------------
# FUNCIONES PARA FOLLOW-UP AUTOMÁTICO
# ----------------------------

ZONA_EC = pytz.timezone("America/Guayaquil")

def obtener_contactos_activos():
    hoja = conectar_hoja("Mensajes")
    registros = hoja.get_all_records()

    activos = []
    for fila in registros:
        estado = fila.get("Estado", "").strip().lower()
        if estado in ["activo", "seguimiento_1", "seguimiento_2", "recordatorio"]:
            activos.append({
                "chat_id": fila.get("Teléfono", "").strip(),
                "estado": estado,
                "ultimo_mensaje": fila.get("Fecha", "")
            })
    return activos

def actualizar_estado_chat(chat_id, nuevo_estado):
    hoja = conectar_hoja("Mensajes")
    datos = hoja.get_all_values()

    for i, fila in enumerate(datos):
        if i == 0:
            continue  # Encabezados
        if fila[0].strip() == chat_id.strip():
            hoja.update_cell(i + 1, 3, nuevo_estado)  # Columna C = Estado
            break

def actualizar_ultima_interaccion(chat_id):
    hoja = conectar_hoja("Mensajes")
    datos = hoja.get_all_values()
    ahora = datetime.now(ZONA_EC).strftime("%Y-%m-%d %H:%M:%S")

    for i, fila in enumerate(datos):
        if i == 0:
            continue
        if fila[0].strip() == chat_id.strip():
            hoja.update_cell(i + 1, 4, ahora)  # Columna D = Fecha
            break

def registrar_mensaje(chat_id, mensaje, tipo, canal):
    hoja = conectar_hoja("Mensajes")
    ahora = datetime.now(ZONA_EC).strftime("%Y-%m-%d %H:%M:%S")
    hoja.append_row([
        chat_id,    # Número
        ahora,      # Fecha
        tipo,       # Tipo
        canal,      # Canal
        mensaje     # Mensaje
    ])

def registrar_cita_en_hoja(
    contacto: str,
    fecha_cita: str,
    hora: str,
    modalidad: str,
    lugar: str,
    observaciones: str = ""
):
    """
    Registra una nueva cita en la hoja 'Citas' del Google Sheets.
    contacto: número del cliente (593...)
    fecha_cita: fecha en formato texto (ej. '2025-06-10')
    hora: hora en formato texto (ej. '10:00')
    modalidad: 'Finca' o 'Oficina'
    lugar: ubicación del encuentro
    observaciones: cualquier nota adicional
    """
    hoja = conectar_hoja("Citas")
    fila = [
        contacto,
        fecha_cita,
        hora,
        modalidad,
        lugar,
        "Pendiente",       # Confirmada por defecto
        observaciones
    ]
    hoja.append_row(fila)

def actualizar_estado_cita(contacto, nuevo_estado, observaciones_adicionales=""):
    """
    Actualiza el estado de una cita existente en la hoja 'Citas' para un contacto específico.
    Se basa en el número de contacto (ID_Contacto) y modifica la columna 'Confirmada' y 'Observaciones'.
    """
    hoja = conectar_hoja("Citas")
    filas = hoja.get_all_values()

    for idx, fila in enumerate(filas):
        if idx == 0:
            continue  # Saltar cabecera

        if fila[0] == contacto:
            hoja.update_cell(idx + 1, 6, nuevo_estado)  # Columna F = Confirmada
            hoja.update_cell(idx + 1, 7, observaciones_adicionales)  # Columna G = Observaciones
            print(f"✅ Estado de la cita para {contacto} actualizado a '{nuevo_estado}'")
            return

    print(f"⚠️ No se encontró cita activa para {contacto}.")

def cargar_estado_desde_sheets(contacto_id):
    hoja = conectar_hoja("Contactos")
    registros = hoja.get_all_records()
    for idx, fila in enumerate(registros, start=2):  # empieza en 2 por encabezado
        if str(fila.get("ID_Contacto", "")).strip() == str(contacto_id).strip():
            return {
                "actividad": fila.get("Actividad", "").strip().lower(),
                "etapa": fila.get("Etapa_Actual", "inicio")
            }
    return None

def registrar_mensaje_seguimiento(chat_id, mensaje, fecha_hora):
    registrar_mensaje(chat_id, mensaje, tipo="Seguimiento", canal="Bot")
