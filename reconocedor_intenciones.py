import re

# Frases ya definidas en tu sistema
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

def detectar_intencion(texto):
    texto = texto.lower().strip()

    # Detención inmediata si es ofensivo
    if any(palabra in texto for palabra in EXPRESIONES_OFENSIVAS):
        return "ofensivo"

    # Rechazo fuerte directo
    if any(frase in texto for frase in NEGATIVOS_FUERTES):
        return "negativo_fuerte"

    # Ambiguo o evasivo
    if any(frase in texto for frase in EXPRESIONES_AMBIGUAS):
        return "negativo_ambiguo"

    # Reactivación luego de haber salido del flujo
    if any(frase in texto for frase in EXPRESIONES_REACTIVACION):
        return "reactivacion"

    # Si menciona permisos sin indicar claramente sí o no
    if any(p in texto for p in ["permiso", "registro", "licencia", "documento", "papeles"]):
        return "mencion_permiso"

    # Si contiene pregunta genérica
    if re.search(r"(cómo|qué|cuándo|dónde|para qué|puedo|necesito)", texto):
        return "pregunta_abierta"

    return "indefinido"
