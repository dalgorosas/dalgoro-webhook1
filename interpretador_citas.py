
# interpretador_citas.py (ampliado con términos aproximados de hora)

import re
from datetime import datetime
import dateparser
from google_sheets_utils import registrar_cita_en_hoja

# Mapa de términos aproximados a horas estimadas
HORAS_ESTIMADAS = {
    "temprano": "08:00",
    "al mediodía": "12:00",
    "mediodía": "12:00",
    "en la tarde": "15:00",
    "por la tarde": "15:00",
    "en la mañana": "09:00",
    "por la mañana": "09:00",
    "en la noche": "19:00",
    "por la noche": "19:00"
}

def extraer_fecha_y_hora(texto):
    texto = texto.lower()
    texto = texto.replace("mañana a ", "mañana a las ")
    texto = texto.replace("este ", "")
    texto = texto.replace("próximo ", "")

    # Verificar si hay un término de hora estimada
    hora_aproximada = None
    for palabra, hora in HORAS_ESTIMADAS.items():
        if palabra in texto:
            hora_aproximada = hora
            break

    # Configuración de contexto
    settings = {
        'PREFER_DATES_FROM': 'future',
        'RELATIVE_BASE': datetime.now()
    }

    # Intento 1: parsear todo el texto
    parsed = dateparser.parse(texto, languages=['es'], settings=settings)
    if parsed:
        fecha_str = parsed.strftime("%Y-%m-%d")
        hora_str = parsed.strftime("%H:%M") if not hora_aproximada else hora_aproximada
        return fecha_str, hora_str

    # Intento 2: buscar subfrases como "martes a las 10", "8 de junio a las 9"
    patrones = [
        r"(lunes|martes|miércoles|jueves|viernes|sábado|domingo).*?(\d{1,2})(?::(\d{2}))?",
        r"(\d{1,2}) de (enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre).*?(\d{1,2})(?::(\d{2}))?",
    ]

    for patron in patrones:
        coincidencia = re.search(patron, texto)
        if coincidencia:
            frase_detectada = coincidencia.group(0)
            parsed_alt = dateparser.parse(frase_detectada, languages=['es'], settings=settings)
            if parsed_alt:
                fecha_str = parsed_alt.strftime("%Y-%m-%d")
                hora_str = parsed_alt.strftime("%H:%M") if not hora_aproximada else hora_aproximada
                return fecha_str, hora_str

    return None, None

def procesar_y_registrar_cita(chat_id, mensaje):
    fecha, hora = extraer_fecha_hora(mensaje)
    if fecha and hora:
        registrar_cita_en_hoja(
            contacto=chat_id,
            fecha_cita=fecha,
            hora=hora,
            modalidad="Definir en llamada",
            lugar="Definir en llamada",
            observaciones=mensaje
        )
        return True
    return False
