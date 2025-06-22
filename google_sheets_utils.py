import os
import json
import sys
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials
from zona_horaria import ZONA_HORARIA_EC
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Ámbitos de acceso para Google Sheets y Drive
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

def agregar_fila_a_hoja(nombre_hoja, fila):
    hoja = conectar_hoja(nombre_hoja)
    hoja.append_row(fila)

# ID del Google Sheet
# Puede definirse mediante la variable de entorno ``SHEET_ID``. Si se
# establece ``GOOGLE_SHEET_URL`` se usará directamente esa URL.
SHEET_ID = os.getenv("SHEET_ID", "1RggJz98tnR86fo_AspwLWUVOIABn6vVrvojAkfQAqHc")
GOOGLE_SHEET_URL = os.getenv("GOOGLE_SHEET_URL")

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
        logger.info("🔁 Estado actualizado en fila %s de Sheets.", idx)
    else:
        hoja.append_row(list(fila_nueva.values()))
        logger.info("➕ Estado nuevo registrado en Sheets para %s.", chat_id)

def obtener_credenciales():
    """Obtiene las credenciales de Google para acceder a Sheets.

    Primero intenta utilizar la variable de entorno ``GOOGLE_CREDENTIALS_JSON``.
    Esta variable puede contener la ruta a un archivo JSON o el JSON completo en
    formato de cadena. Si falla, se intenta cargar el archivo local
    ``dalgoro-api-ea1fa305d0ca.json``. En caso de no encontrar credenciales se
    lanza ``FileNotFoundError`` con un mensaje descriptivo.
    """

    cred_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if not cred_json:
        logger.error("❌ GOOGLE_CREDENTIALS_JSON no está definida.")
        raise FileNotFoundError("GOOGLE_CREDENTIALS_JSON no está definida.")

    if cred_json:
        try:
            if os.path.isfile(cred_json):
                with open(cred_json, "r", encoding="utf-8") as f:
                    cred_dict = json.load(f)
            else:
                cred_dict = json.loads(cred_json)
            return ServiceAccountCredentials.from_json_keyfile_dict(cred_dict, SCOPE)
        
        except Exception as e:
            logger.warning("⚠️ No se pudo usar GOOGLE_CREDENTIALS_JSON: %s", e)

    archivo_local = "dalgoro-api-ea1fa305d0ca.json"
    try:
        with open(archivo_local, "r", encoding="utf-8") as f:
            cred_dict = json.load(f)
        logger.info("🗂️ Credenciales cargadas desde %s", archivo_local)
        return ServiceAccountCredentials.from_json_keyfile_dict(cred_dict, SCOPE)
    except FileNotFoundError:
        logger.warning("⚠️ Archivo de credenciales '%s' no encontrado.", archivo_local) 
    
    except Exception as e:
        logger.error("❌ Error al cargar credenciales desde %s: %s", archivo_local, e)

    mensaje = (
        "Credenciales de Google no encontradas. Define la variable de entorno GOOGLE_CREDENTIALS_JSON o coloca el archivo '%s' en la raíz del proyecto." % archivo_local
    )
    logger.error(mensaje)
    sys.exit(mensaje)

def conectar_hoja(nombre_hoja):
    creds = obtener_credenciales()
    cliente = gspread.authorize(creds)

    # URL de la hoja de cálculo. Si se define ``GOOGLE_SHEET_URL`` se utiliza
    # directamente; de lo contrario se construye a partir de ``SHEET_ID``.
    url_hoja = GOOGLE_SHEET_URL or f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid=0"

    hoja_gspread = cliente.open_by_url(url_hoja).worksheet(nombre_hoja)
    return hoja_gspread

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
    logger.info("✅ Se cargaron %s estados desde Sheets.", len(estados))
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
            logger.error("Error al registrar mensaje: %s", e)
            return False

# Instancia global
sheets_manager = SheetsManager()

# ----------------------------
# FUNCIONES PARA FOLLOW-UP AUTOMÁTICO
# ----------------------------

ZONA_EC = ZONA_HORARIA_EC

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

def registrar_cita_en_hoja(contacto, fecha_cita, hora, modalidad, lugar, observaciones):
    print(f"➡️ Intentando registrar cita: {contacto}, {fecha_cita}, {hora}, {modalidad}, {lugar}")
    print("📦 Observaciones a registrar:", observaciones)  # Diagnóstico

    try:
        hoja = conectar_hoja("Citas")
        filas = hoja.get_all_records()

        # Verificar duplicados solo si la hoja tiene datos válidos
        for fila in filas:
            id_c = str(fila.get("contacto", "")).strip()
            fecha = str(fila.get("fecha_cita", "")).strip()
            hora_fila = str(fila.get("hora", "")).strip()

            if id_c == contacto and fecha == fecha_cita and hora_fila == hora:
                logger.info("➡️ Cita duplicada detectada. No se registrará de nuevo.")
                return

        nueva_fila = [contacto, fecha_cita, hora, modalidad, lugar, observaciones]
        logger.info("📝 Registrando nueva fila: %s", nueva_fila)
        hoja.append_row(nueva_fila)
        logger.info("✅ Cita registrada para %s en %s a las %s.", contacto, fecha_cita, hora)

    except Exception as e:
        logger.error("❌ Error al registrar cita en Google Sheets: %s", e)
        raise  # <--- para que el error no pase desapercibido

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
            logger.info("✅ Estado de la cita para %s actualizado a '%s'", contacto, nuevo_estado)
            return

    logger.warning("⚠️ No se encontró cita activa para %s.", contacto)

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

def registrar_fallo_para_contacto(chat_id, mensaje, estado, motivo="⚠️ Error detectado: flujo detenido"):
    try:
        import re
        numero_limpio = re.sub(r"\D", "", chat_id.split("@")[0])
        actividad = estado.get("actividad", "No detectada")
        etapa = estado.get("etapa", "Sin etapa")
        fase = estado.get("fase", "Sin fase")

        observaciones = f"{motivo}. Mensaje recibido: {mensaje}. Estado actual: etapa={etapa}, fase={fase}. Contactar manualmente."

        hoja = conectar_hoja("Citas")
        nueva_fila = [
            numero_limpio,   # contacto
            "",              # fecha_cita
            "",              # hora
            "Por confirmar", # modalidad
            "Sin datos - error en flujo",
            observaciones    # observaciones
        ]
        hoja.append_row(nueva_fila)
        logger.info("🚨 Fila de error registrada en hoja Citas para %s", chat_id)
    except Exception as e:
        logger.error("❌ Error al registrar falla en hoja Citas: %s", e)
