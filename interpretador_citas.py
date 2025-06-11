from datetime import datetime
from dateutil import parser
import re
import pytz
from dateparser.search import search_dates
from lexico import EXPRESIONES_TIEMPO, EXPRESIONES_UBICACION
from lexico import EXPRESIONES_UBICACION


# ✅ ZONA HORARIA DE ECUADOR
ZONA_HORARIA_EC = pytz.timezone("America/Guayaquil")

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
        "en la mañana": "a las 09:00",
        "en la tarde": "a las 15:00",
        "en la noche": "a las 19:00",
        "al amanecer": "a las 06:00",
        "al anochecer": "a las 18:00",
        "después del almuerzo": "a las 14:00",
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

    texto_normalizado = texto.lower()
    for frase, sustituto in reemplazos.items():
        texto_normalizado = texto_normalizado.replace(frase, sustituto)

    return texto_normalizado

# 🎯 Función principal
def extraer_fecha_y_hora(texto):
    texto = normalizar_expresiones_comunes(texto)
        # Segundo intento: buscar ubicaciones y expresiones de tiempo manuales
    for expr in EXPRESIONES_TIEMPO:
        if expr.lower() in texto:
            texto += f" {EXPRESIONES_TIEMPO[expr]}"
            break

    for expr in EXPRESIONES_UBICACION:
        if expr.lower() in texto:
            ubicacion = EXPRESIONES_UBICACION[expr]
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

    if fecha_hora:
        fecha_detectada = fecha_hora[0][1].astimezone(ZONA_HORARIA_EC)
    
        ubicacion = None
        for expresion in EXPRESIONES_UBICACION:
            if expresion in texto:
                if "finca" in expresion:
                    ubicacion = "Finca"
                elif "oficina" in expresion:
                    ubicacion = "Oficina"
                else:
                    ubicacion = "Sitio"
                break
            print(f"🧭 Ubicación detectada: {ubicacion}")

        return {
            "fecha": fecha_detectada.strftime("%Y-%m-%d"),
            "hora": fecha_detectada.strftime("%H:%M"),
            "ubicacion": ubicacion
        }
    
    # Fallback manual con regex
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

    hoy = datetime.now(ZONA_HORARIA_EC)
    fecha_detectada = None
    for patron in patrones_fecha_ext:
        if re.search(patron, texto, re.IGNORECASE):
            fecha_detectada = hoy.strftime("%Y-%m-%d")
            break

    if fecha_detectada or hora_detectada:
        ubicacion = None
        if "finca" in texto:
            ubicacion = "Finca"
        elif "oficina" in texto:
            ubicacion = "Oficina"

        return {
            "fecha": fecha_detectada or hoy.strftime("%Y-%m-%d"),
            "hora": hora_detectada or "09:00",
            "ubicacion": ubicacion
        }

    return None