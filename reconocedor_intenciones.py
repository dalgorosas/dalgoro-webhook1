import re
import difflib
from respuestas_por_actividad import NEGATIVOS_FUERTES

def detectar_similitud(texto, lista, umbral=0.85):
    texto = texto.strip().lower()
    for frase in lista:
        frase = frase.lower()
        if frase in texto:
            return True
        similitud = difflib.SequenceMatcher(None, texto, frase).ratio()
        if similitud >= umbral:
            return True
    return False

EXPRESIONES_REACTIVACION = [
    "disculpa", "perdón", "buenos días", "buenas tardes", "buenas noches",
    "me quedé sin responder", "estás ahí", "ahora sí", "podemos continuar",
    "quiero retomar", "sí, disculpa", "perdón la demora", "podemos seguir",
    "perdón que no respondí", "disculpa la demora", "me desconecté",
    "tuve un inconveniente", "ahora tengo tiempo", "ya estoy disponible",
    "ya puedo responder", "sigamos", "podemos hablar", "podemos hablar ahora",
    "no pude responder antes", "volví", "aquí estoy", "ya regresé", "seguimos",
    "me quedé ocupado", "tuve que salir", "tuve que atender algo",
    "retomemos", "quiero seguir", "seguimos con lo de antes"
]

EXPRESIONES_OFENSIVAS = [
    "idiota", "estúpido", "imbécil", "no jodas", "vete", "que te pasa", "maldito", "cállate",
    "están locos", "qué asco", "no me molestes", "lárgate", "estúpidos", "inútiles"
]

EXPRESIONES_AMBIGUAS = [
    "más adelante", "otro día", "en otro momento", "quizá después",
    "no estoy seguro", "no por ahora", "no todavía", "aún no",
    "no he decidido", "déjame pensarlo", "necesito tiempo",
    "ahorita no", "en otra ocasión", "luego vemos", "en otro momento lo veo",
    "tal vez más adelante", "quizá en otro momento", "tengo que pensarlo",
    "tengo que revisarlo", "luego hablamos", "ahorita estoy ocupado",
    "déjame ver", "déjame organizarme", "voy a analizarlo",
    "podría ser después", "ahora no puedo", "ahorita no puedo", "lo veo luego",
    "lo pensaré", "lo revisaré", "luego te confirmo", "después te aviso",
    "ahorita no tengo tiempo", "dame un momento", "dame tiempo", "dame unos días"
]

EXPRESIONES_AFIRMACION_SUAVE = [
    "sí me interesa", "si me interesa", "me interesa",
    "sí deseo", "si deseo", "deseo continuar", "deseo que me visiten",
    "sí quiero", "si quiero", "quiero seguir", "quiero avanzar",
    "sí me gustaría", "si me gustaría", "me gustaría saber", "me gustaría continuar",
    "me interesa saber", "me interesa conocer", "me interesa el proceso", "me interesa avanzar",
    "quiero saber más", "quiero conocer el proceso", "quiero entender", "quiero información",
    "sí por favor", "sí claro", "claro que sí", "por supuesto", "cuéntame más",
    "me gustaría que me cuenten", "sí quiero que me cuentes", "sí deseo información",
    "me encantaría", "quisiera", "sí quisiera", "si quisiera", "quisiera más detalles",
    "sí estoy interesado", "estoy interesado", "me parece bien", "ok vamos", "sí quiero ayuda",
    "sí quiero que vengan", "me gustaría avanzar", "sí acepto", "acepto la ayuda",
    "está bien", "sí gracias", "perfecto", "de acuerdo", "acepto",
    "me interesa mucho", "claro, por favor", "sí, deseo avanzar", "gracias, sí quiero continuar",
    "me gustaría una visita", "me gustaría recibir asesoría", "quiero recibir asesoría",
    "sí, deseo que me asesoren", "quiero agendar", "sí deseo agendar", "estoy de acuerdo", 
    "cuenten conmigo", "ok, adelante", "sí, sigamos", "pueden continuar", "por favor, sigamos",
    "vamos con eso", "sí, estoy convencido", "quiero su ayuda", "sí deseo acompañamiento"
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

    if detectar_similitud(texto, EXPRESIONES_AFIRMACION_SUAVE):
        return "afirmacion_suave"

    if detectar_similitud(texto, EXPRESIONES_CITA):
        return "cita_implicita"

    if detectar_similitud(texto, EXPRESIONES_AMBIGUAS):
        return "negativo_ambiguo"

    if detectar_similitud(texto, NEGATIVOS_FUERTES):
        return "negativo_fuerte"

    if detectar_similitud(texto, EXPRESIONES_OFENSIVAS):
        return "ofensivo"

    if detectar_similitud(texto, EXPRESIONES_REACTIVACION):
        return "reactivacion"

    if detectar_similitud(texto, ["permiso", "registro", "licencia", "documento", "papeles"]):
        return "mencion_permiso"

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
