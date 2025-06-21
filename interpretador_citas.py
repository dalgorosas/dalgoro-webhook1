from datetime import datetime
import re
from dateparser.search import search_dates
from lexico import EXPRESIONES_TIEMPO, EXPRESIONES_UBICACION
from zona_horaria import ZONA_HORARIA_EC
import logging
from datetime import timedelta


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
        "tipo ": "a las ",
        "como a las ": "a las ",
        "como a ": "a las ",
        "a eso de las ": "a las ",
        "a eso de ": "a las ",
        "más o menos a las ": "a las ",
        "más o menos a ": "a las ",
        "por la tarde del ": "",  # se espera que ya haya una referencia de día
        "por la mañana del ": "",
        "cuando amanezca": "a las 06:00",
        "en la tarde noche": "a las 18:00",
        "cuando pase el almuerzo": "a las 15:00",
        "al terminar la jornada": "a las 17:00",
        "mañana tipo ": "mañana a las ",
        "hoy mismo a las ": "hoy a las ",
        "mañana después del desayuno": "mañana a las 10:00",
        "media mañana": "a las 10:30",
        "media tarde": "a las 16:00",
        "antes del medio día": "a las 11:00",
        "el lunes a primera hora": "lunes a las 07:00",
        "a las 7 u 8 de la noche": "a las 19:30",
    })

    texto_normalizado = texto.lower()
    for frase, sustituto in reemplazos.items():
        texto_normalizado = texto_normalizado.replace(frase, sustituto)

    return texto_normalizado

# 🎯 Función principal
def extraer_fecha_y_hora(texto):
    texto = normalizar_expresiones_comunes(texto)
    ubicacion = None
    fecha_detectada = None
    hora_detectada = None

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

    # Interpretación de frases informales si aún no se detecta hora
    if not hora_detectada:
        if "y media" in texto:
            hora_detectada = "12:30"
        elif "y cuarto" in texto:
            hora_detectada = "12:15"
        elif "al mediodía" in texto or "medio día" in texto:
            hora_detectada = "12:00"
        elif "medianoche" in texto:
            hora_detectada = "00:00"
        elif "media mañana" in texto:
            hora_detectada = "10:30"
        elif "media tarde" in texto:
            hora_detectada = "16:00"
        elif "temprano" in texto:
            hora_detectada = "08:00"
        elif "tarde noche" in texto:
            hora_detectada = "18:00"
        elif "noche" in texto:
            hora_detectada = "20:00"
        elif "mañana" in texto:
            hora_detectada = "09:00"

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
    
    # Si se menciona un día específico, intenta calcular la próxima fecha correspondiente
    dias_semana = {
        "lunes": 0, "martes": 1, "miércoles": 2, "miercoles": 2,
        "jueves": 3, "viernes": 4, "sábado": 5, "sabado": 5, "domingo": 6
    }
    for dia_texto, indice in dias_semana.items():
        if dia_texto in texto:
            hoy = datetime.now(ZONA_HORARIA_EC)
            dias_a_sumar = (indice - hoy.weekday() + 7) % 7 or 7
            fecha_detectada = (hoy + timedelta(days=dias_a_sumar)).strftime("%Y-%m-%d")
            break

    hoy = datetime.now(ZONA_HORARIA_EC)
    for patron in patrones_fecha_ext:
        if re.search(patron, texto, re.IGNORECASE):
            if not fecha_detectada:
                fecha_detectada = hoy.strftime("%Y-%m-%d")
            break

    if fecha_detectada or hora_detectada:
        if fecha_detectada and not hora_detectada:
            logger.info("⏱ Se detectó fecha pero no hora: se asume 09:00 por defecto.")
        elif hora_detectada and not fecha_detectada:
            logger.info("📅 Se detectó hora pero no fecha: se asume fecha de hoy por defecto.")

        return {
            "fecha": fecha_detectada or hoy.strftime("%Y-%m-%d"),
            "hora": hora_detectada or "09:00",
            "ubicacion": ubicacion,
            "observacion": texto  # texto ya normalizado
        }

    # 🚫 Si no se detectó nada, retornar diccionario vacío
    logger.warning("⚠️ No se detectaron fecha ni hora válidas en el texto: %s", texto)
    return {}

if __name__ == "__main__":
    from pprint import pprint

    pruebas_fecha_hora = [
        "mañana al mediodía",
        "pasado mañana a las 9",
        "nos vemos el viernes",
        "pueden venir a las 3 de la tarde",
        "quiero cita el martes a las 10",
        "me gustaría que vengan en la mañana",
        "esta noche está bien",
        "al amanecer del jueves",
        "después del almuerzo",
        "en dos días por la tarde",
        "nos vemos a primera hora",
        "quedamos para el lunes temprano",
        "jueves a las 14:00",
        "viernes",
        "mañana",
        "al mediodía",
        "a las 10",
        "el sábado por la mañana",
        "el domingo a eso de las 7",
        "el miércoles como a las 11",
        "por la tarde del lunes",
        "al terminar la jornada",
        "después de las 5",
        "a eso de las 3pm",
        "a la hora del almuerzo",
        "tipo 10 y media",
        "a primera hora del martes",
        "cuando amanezca",
        "en la tarde noche",
        "cuando pase el almuerzo",
        "en la noche del domingo",
        "mañana a las 8am",
        "pasado mañana por la noche",
        "el viernes en la tarde",
        "el lunes en la noche",
        "el jueves después del almuerzo",
        "sábado tipo 3 de la tarde",
        "en una semana a las 4",
        "el lunes a primera hora",
        "el martes antes del medio día",
        "mañana tipo 10",
        "hoy mismo a las 3",
        "mañana después del desayuno",
        "cuando tengan un espacio el viernes",
        "a las 7 u 8 de la noche",
        "a media mañana",
        "el domingo temprano",
        "el lunes a eso de las 10",
        "el jueves a media tarde"
    ]


    print("\n🔍 PRUEBAS EXTRAER FECHA Y HORA:")
    for texto in pruebas_fecha_hora:
        resultado = extraer_fecha_y_hora(texto)
        print(f"{texto} →")
        pprint(resultado)
        print("-" * 50)
