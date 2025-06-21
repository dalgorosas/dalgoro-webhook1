from datetime import datetime
import re
from dateparser.search import search_dates
from lexico import EXPRESIONES_TIEMPO, EXPRESIONES_UBICACION
from zona_horaria import ZONA_HORARIA_EC
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ ZONA HORARIA DE ECUADOR
# Importado desde modulo comun
# 🔄 Patrones extendidos
patrones_hora_ext = [
    r"\b(?:a\s+las\s+)?(\d{1,2})(?::(\d{2}))\s*(am|pm)?\b",
    r"\b(?:a\s+las\s+)?(\d{1,2})\s*(am|pm)\b",
    r"\b(?:a\s+las\s+)?(\d{1,2})\b",
    r"\b(\d{1,2})[:.](\d{2})\b",
    r"\b(\d{1,2})\s+horas\b",
    r"\ba\s+las\s+(\d{1,2})(?:\s*en\s+la\s+(mañana|tarde|noche))?\b"
]

patrones_fecha_ext = [
    r"\b(hoy|mañana|pasado\s+mañana|esta\s+semana|esta\s+noche|esta\s+mañana|esta\s+tarde)\b",
    r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})\b",
    r"\b(\d{1,2})[/-](\d{1,2})\b",
    r"\b(el\s+)?(\d{1,2})\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)\b",
    r"\b(lunes|martes|miércoles|miercoles|jueves|viernes|sábado|sabado|domingo)\b",
    r"\b(próximo|proximo)\s+(lunes|martes|miércoles|miercoles|jueves|viernes|sábado|sabado|domingo)\b",
    r"\b(dentro\s+de\s+\d+\s+(días|semanas))\b",
    r"\b(en\s+una\s+semana|en\s+dos\s+días)\b"
]

# 🧠 Normalización de expresiones informales
def normalizar_expresiones_comunes(texto):
    reemplazos = {
        "pasado mañana después del medio día": "pasado mañana a las 13:00",
        "pasado mañana al medio día": "pasado mañana a las 12:00",
        "mañana después del medio día": "mañana a las 13:00",
        "mañana al medio día": "mañana a las 12:00",
        "hoy después del medio día": "hoy a las 13:00",
        "hoy al medio día": "hoy a las 12:00",
        "al amanecer": "a las 06:00",
        "al anochecer": "a las 18:00",
        "temprano en la mañana": "a las 08:00",
        "esta noche": "hoy a las 20:00",
        "esta mañana": "hoy a las 08:00",
        "esta tarde": "hoy a las 15:00",
        "en la madrugada": "hoy a las 05:00",
        "en la noche": "hoy a las 20:00",
        "en la tarde": "hoy a las 15:00",
        "en la mañana": "hoy a las 09:00",
        "después del almuerzo": "hoy a las 14:00",
        "a primera hora": "hoy a las 07:00",
        "en dos días": "pasado mañana"
    }
    reemplazos.update({
    "podemos vernos a las 10": "a las 10",
    "quedamos para el jueves": "jueves",
    "nos reunimos el viernes": "viernes",
    "veámonos a las 3": "a las 3",
    })

    texto_normalizado = texto.lower()
    for frase, sustituto in reemplazos.items():
        texto_normalizado = texto_normalizado.replace(frase, sustituto)

    return texto_normalizado

# 🎯 Función principal
def extraer_fecha_y_hora(texto):
    texto = normalizar_expresiones_comunes(texto)
    ubicacion = None  # Inicializar para evitar errores

    # Detección anticipada de ubicación
    for expr in EXPRESIONES_UBICACION:
        if expr.lower() in texto:
            ubicacion = EXPRESIONES_UBICACION[expr]
            break

    # Reforzar detección agregando patrones conocidos
    for palabra_clave in EXPRESIONES_TIEMPO["relativo"]:
        if palabra_clave.lower() in texto:
            texto += f" {palabra_clave}"  # No es reemplazo, es refuerzo
            break

    for patron in EXPRESIONES_TIEMPO["fecha"]:
        if re.search(patron, texto, re.IGNORECASE):
            logger.debug("🔍 Patrón de fecha encontrado: %s", patron)
            break

    for patron in EXPRESIONES_TIEMPO["hora"]:
        if re.search(patron, texto, re.IGNORECASE):
            logger.debug("🔍 Patrón de hora encontrado: %s", patron)
            break

    # Primer intento con dateparser
    fecha_hora = search_dates(
        texto,
        languages=["es"],
        settings={
            'TIMEZONE': 'America/Guayaquil',
            'RETURN_AS_TIMEZONE_AWARE': True,
            'PREFER_DATES_FROM': 'future',
            'RELATIVE_BASE': datetime.now(ZONA_HORARIA_EC)
        }
    )

    if fecha_hora and isinstance(fecha_hora, list) and isinstance(fecha_hora[0], (tuple, list)) and len(fecha_hora[0]) > 1:
        fecha_detectada = fecha_hora[0][1].astimezone(ZONA_HORARIA_EC)
        return {
            "fecha": fecha_detectada.strftime("%Y-%m-%d"),
            "hora": fecha_detectada.strftime("%H:%M"),
            "ubicacion": ubicacion
        }

    # Fallback manual con expresiones regulares
    hora_detectada = None
    for patron in patrones_hora_ext:
        coincidencia = re.search(patron, texto, re.IGNORECASE)
        if coincidencia:
            grupos = coincidencia.groups()
            try:
                hora = int(grupos[0])
                minutos = int(grupos[1]) if len(grupos) > 1 and grupos[1] else 0
                meridiano = grupos[-1].lower() if grupos[-1] and grupos[-1].lower() in ["am", "pm"] else None
                if meridiano == "pm" and hora < 12:
                    hora += 12
                hora_detectada = f"{hora:02}:{minutos:02}"
                break
            except Exception:
                continue

    # Interpretación de frases comunes adicionales
    if "y media" in texto:
        hora_detectada = "12:30"
    elif "al mediodía" in texto or "medio día" in texto:
        hora_detectada = "12:00"
    elif "medianoche" in texto:
        hora_detectada = "00:00"
    elif "y cuarto" in texto:
        hora_detectada = "12:15"

    hoy = datetime.now(ZONA_HORARIA_EC)
    fecha_detectada = None
    for patron in patrones_fecha_ext:
        if re.search(patron, texto, re.IGNORECASE):
            fecha_detectada = hoy.strftime("%Y-%m-%d")
            break

    if fecha_detectada or hora_detectada:
        if fecha_detectada and not hora_detectada:
            logger.info("⏱ Se detectó fecha pero no hora: se asume 09:00 por defecto.")
        elif hora_detectada and not fecha_detectada:
            logger.info("📅 Se detectó hora pero no fecha: se asume fecha de hoy por defecto.")

        resultado = {
            "fecha": fecha_detectada or hoy.strftime("%Y-%m-%d"),
            "hora": hora_detectada or "09:00",
            "ubicacion": ubicacion
        }
        logger.debug("🔍 Patrón de hora encontrado: %s", patron)
        return resultado
