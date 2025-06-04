
# respuestas_finales.py

from respuestas_por_actividad import FLUJOS_POR_ACTIVIDAD

def obtener_mensaje_agradecimiento(actividad):
    """
    Retorna el mensaje de agradecimiento personalizado para la actividad,
    o un mensaje por defecto si no se encuentra.
    """
    flujo = FLUJOS_POR_ACTIVIDAD.get(actividad.lower())
    if flujo and "agradecimiento" in flujo:
        return flujo["agradecimiento"]
    return "✅ Gracias por agendar su cita con nosotros. Estamos para servirle. Pronto nos pondremos en contacto para coordinar los detalles."
