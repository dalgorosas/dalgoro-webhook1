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
    "sí me gustaría", "sí quiero", "me interesa", "quiero saber más", "claro que sí",
    "por supuesto", "sí por favor", "me gustaría conocer", "me gustaría que me cuenten",
    "sí deseo", "sí deseo saber", "sí deseo información"
]

EXPRESIONES_CITA = [
    "agenda", "visita", "cita", "coordinar", "nos vemos", "reunión", "vernos",
    "pueden venir", "pueden pasar", "me gustaría que vengan"
]

def detectar_intencion(texto):
    texto = texto.lower().strip()

    if any(p in texto for p in EXPRESIONES_OFENSIVAS):
        return "ofensivo"

    if any(p in texto for p in NEGATIVOS_FUERTES):
        return "negativo_fuerte"

    if any(p in texto for p in EXPRESIONES_AMBIGUAS):
        return "negativo_ambiguo"

    if any(p in texto for p in EXPRESIONES_REACTIVACION):
        return "reactivacion"

    if any(p in texto for p in ["permiso", "registro", "licencia", "documento", "papeles"]):
        return "mencion_permiso"

    if any(p in texto for p in EXPRESIONES_CITA):
        return "cita_implicita"

    if any(p in texto for p in EXPRESIONES_AFIRMACION_SUAVE):
        return "afirmacion_suave"

    if re.search(r"\b(cómo|qué|cuándo|dónde|para qué|puedo|necesito)\b", texto):
        return "pregunta_abierta"

    return "indefinido"
