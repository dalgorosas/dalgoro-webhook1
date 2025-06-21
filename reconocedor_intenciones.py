import re
from respuestas_por_actividad import NEGATIVOS_FUERTES

EXPRESIONES_REACTIVACION = [
    "disculpa", "perdón", "buenos días", "buenas tardes", "buenas noches",
    "me quedé sin responder", "estás ahí", "ahora sí", "podemos continuar", "quiero retomar",
    "sí, disculpa", "perdón la demora", "podemos seguir", "perdón que no respondí"
]

EXPRESIONES_OFENSIVAS = [
    "idiota", "estúpido", "imbécil", "no jodas", "vete", "que te pasa", "maldito", "cállate",
    "están locos", "qué asco", "no me molestes", "lárgate", "estúpidos", "inútiles"
]

EXPRESIONES_AMBIGUAS = [
    "más adelante", "otro día", "en otro momento", "quizá después", "no estoy seguro",
    "no por ahora", "no todavía", "aún no", "no he decidido", "déjame pensarlo", "necesito tiempo"
]

EXPRESIONES_AFIRMACION_SUAVE = [
    "sí me interesa", "si me interesa",
    "sí deseo", "si deseo",
    "sí quiero", "si quiero",
    "sí me gustaría", "si me gustaría",
    "me interesa", "me interesa saber", "me gustaría saber", "me gustaría conocer",
    "quiero saber más", "quiero conocer el proceso", "quiero entender",
    "claro que sí", "por supuesto", "sí por favor", "me gustaría que me cuenten",
    "si quiero que me cuentes", "sí deseo saber", "sí deseo información",
    "me encantaría", "quisiera", "sí quisiera", "si quisiera"
]

EXPRESIONES_CITA = [
    "agenda", "visita", "cita", "coordinar", "nos vemos", "reunión", "vernos",
    "pueden venir", "pueden pasar", "me gustaría que vengan"
]

"""
Detecta la intención de un mensaje de texto del usuario.

Parámetros:
    texto (str): El mensaje recibido del cliente.

Retorna:
    str: Una de las siguientes etiquetas según la intención detectada:
        - "ofensivo"
        - "negativo_fuerte"
        - "negativo_ambiguo"
        - "reactivacion"
        - "mencion_permiso"
        - "cita_implicita"
        - "afirmacion_suave"
        - "pregunta_abierta"
        - "indefinido"
"""

def detectar_intencion(texto):
    texto = texto.lower().strip()

    if any(re.search(rf"\b{re.escape(p)}\b", texto) for p in EXPRESIONES_OFENSIVAS):
        return "ofensivo"

    if any(re.search(rf"\b{re.escape(p)}\b", texto) for p in NEGATIVOS_FUERTES):
        return "negativo_fuerte"

    if any(re.search(rf"\b{re.escape(p)}\b", texto) for p in EXPRESIONES_AMBIGUAS):
        return "negativo_ambiguo"

    if any(re.search(rf"\b{re.escape(p)}\b", texto) for p in EXPRESIONES_REACTIVACION):
        return "reactivacion"

    if any(re.search(rf"\b{re.escape(p)}\b", texto) for p in ["permiso", "registro", "licencia", "documento", "papeles"]):
        return "mencion_permiso"

    if any(re.search(rf"\b{re.escape(p)}\b", texto) for p in EXPRESIONES_CITA):
        return "cita_implicita"

    if any(re.search(rf"\b{re.escape(p)}\b", texto) for p in EXPRESIONES_AFIRMACION_SUAVE):
        return "afirmacion_suave"

    if re.search(r"\b(cómo|qué|cuándo|dónde|para qué|puedo|necesito)\b", texto):
        return "pregunta_abierta"

    return "indefinido"

if __name__ == "__main__":
    pruebas = [
        "si me interesa", "nos vemos el jueves", "me gustaría que vengan",
        "disculpa no respondí", "maldito", "más adelante", "cuando pueden visitarme",
        "permiso ambiental", "quiero retomar", "no gracias", "lárgate"
    ]
    for texto in pruebas:
        print(f"{texto} → {detectar_intencion(texto)}")
