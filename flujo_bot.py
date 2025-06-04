
# flujo_bot.py

from respuestas_por_actividad import RESPUESTA_INICIAL, FLUJOS_POR_ACTIVIDAD

def obtener_respuesta_inicial():
    return RESPUESTA_INICIAL

def obtener_flujo_por_actividad(actividad, etapa):
    """
    Devuelve el mensaje correspondiente a una actividad y etapa.
    actividad: string como 'bananera', 'camaronera', etc.
    etapa: string como 'inicio', 'empezando', 'tiene_finca', 'no_sabe', 'agendar', 'agradecimiento'
    """
    flujo = FLUJOS_POR_ACTIVIDAD.get(actividad.lower())
    if not flujo:
        return "Qué interesante lo que nos comenta 😊 Cuéntenos un poco más sobre su actividad para ver cómo podemos ayudarle mejor."
    return flujo.get(etapa, "Estamos aquí para ayudarle. ¿Podría indicarnos un poco más sobre su situación?")
