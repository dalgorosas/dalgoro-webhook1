# -*- coding: utf-8 -*-

# Expresiones para detección de tiempo en lenguaje natural
EXPRESIONES_TIEMPO = {
    "fecha": [
        r"\d{1,2}\s+de\s+(enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)"
    ],
    "hora": [
        r"a\s+las\s+\d{1,2}:\d{2}",
        r"\d{1,2}:\d{2}"
    ],
    "relativo": [
        "hoy", "mañana", "pasado mañana", "esta semana", "la próxima semana", "el próximo lunes",
        "el próximo martes", "el próximo miércoles", "el próximo jueves", "el próximo viernes",
        "el próximo sábado", "el próximo domingo", "este lunes", "este martes", "este miércoles",
        "este jueves", "este viernes", "este sábado", "este domingo", "fin de semana", "inicios de semana",
        "finales de semana", "dentro de una semana", "en una semana", "el lunes", "el martes", "el miércoles",
        "el jueves", "el viernes", "el sábado", "el domingo", "el día lunes", "el día martes",
        "en la tarde", "en la mañana", "al mediodía", "por la tarde", "por la mañana", "por la noche",
        "temprano", "tarde", "en la noche"
    ]
}

# Expresiones comunes para detección de ubicación
EXPRESIONES_UBICACION = {
    "en mi finca": "Finca",
    "en la finca": "Finca",
    "en la empresa": "Oficina",
    "en el sitio": "Campo",
    "en mi oficina": "Oficina",
    "en la oficina": "Oficina",
    "en el galpón": "Campo",
    "en la camaronera": "Finca",
    "en el plantel": "Campo",
    "en las instalaciones": "Oficina",
    "en mi planta": "Finca",
    "aquí mismo": "Campo",
    "en mi propiedad": "Finca",
    "en campo": "Campo",
    "en sitio": "Campo",
    "en el predio": "Finca",
    "en el terreno": "Finca",
    "donde están los cultivos": "Finca",
    "donde están las piscinas": "Finca",
    "en el criadero": "Finca",
    "en el proyecto": "Campo"
}
