RESPUESTA_INICIAL = """
👋 ¡Hola! Le saluda *DALGORO - Innovación y Sostenibilidad* 🌿
Ayudamos a empresas como la suya a cumplir con la normativa ambiental para operar tranquilamente ✅

Cuéntenos por favor, ¿su consulta está relacionada con alguna de estas actividades?
Bananera, camaronera, minería, cacaotera, cultivo de ciclo corto, granja porcina, granja avícola, hotel, industria u otra.
"""

# Lista centralizada de frases que indican desinterés fuerte o rechazo
NEGATIVOS_FUERTES = [
    "no", "no quiero", "no deseo", "no me interesa", "más adelante",
    "ahora no", "otro día", "quizá después", "no estoy seguro",
    "no por ahora", "no todavía", "todavía", "aún", "aun no", 
    "no he decidido", "otro momento", "déjame pensarlo", 
    "necesito pensarlo", "no tengo tiempo"
]

FLUJOS_POR_ACTIVIDAD = {
    "bananera": {
        "introduccion": "🍌 ¡Excelente actividad! Justamente nosotros nos especializamos en el sector bananero para facilitar el cumplimiento ambiental y evitar sanciones. ¿Podría indicarnos si ya cuenta con un permiso ambiental como registro o licencia?\n\n👉 Ya tengo permiso\n👉 Aún no tengo ninguno",
        "aclaracion_introduccion": "🙏 Gracias por su mensaje. ¿Nos podría confirmar si ya cuenta con un permiso ambiental (registro o licencia)? Eso nos ayudará a guiarle mejor 😊",
        "permiso_si": "✅ Muy bien. Podemos revisar si su documentación está al día y sin observaciones. Ofrecemos una evaluación gratuita en su finca o podemos visitarle en su oficina. ¿Le gustaría agendarla? 📋",
        "aclaracion_permiso_si": "🙏 Disculpe, ¿desea que revisemos sus permisos en una visita técnica gratuita? Podemos coordinar según su disponibilidad 😊",
        "permiso_no": "No se preocupe, estamos para ayudarle desde cero. Podemos visitarle para explicarle paso a paso lo que necesita. Es totalmente gratuito. ¿Prefiere que vayamos a su finca o a su oficina? 📅",
        "aclaracion_permiso_no": "🙏 Gracias por su mensaje. ¿Le interesaría recibir nuestra asesoría gratuita para iniciar su proceso ambiental? Solo indíquenos cómo le es más cómodo reunirse 😊",
        "cierre": "Solo necesitamos que nos indique día, hora y si desea que lo visitemos en finca o en su oficina. Esta evaluación no tiene ningún costo 🙌",
        "aclaracion_cierre": "🙏 No logre identificar su disponibilidad. ¿Podría indicarnos día, hora y lugar para su cita? Es sin compromiso y 100% gratuita 🌱",
        "agradecimiento": "🙌 Su cita ha sido registrada. El Ing. Darwin González Romero se comunicará con usted mediante el número 0984770663 para coordinar los detalles. Gracias por confiar en nosotros 🌱"
    },

    "camaronera": {
        "introduccion": "🦐 ¡Excelente actividad! Justamente nosotros trabajamos con productores camaroneros para ayudarlos a cumplir con la normativa ambiental. ¿Actualmente cuenta con registro o licencia ambiental?\n\n👉 Ya tengo\n👉 No tengo ninguno",
        "aclaracion_introduccion": "🙏 Solo para entender mejor, ¿podría indicarnos si ya ha tramitado su permiso ambiental (registro o licencia)? 😊",
        "permiso_si": "Perfecto. Podemos hacer una verificación gratuita de sus documentos y condiciones actuales. Esto le ayudará a evitar problemas futuros. Podemos visitarle en su camaronera o en su oficina. ¿Desea que agendemos? 📅",
        "aclaracion_permiso_si": "🙏 ¿Desea que agendemos una evaluación para revisar sus permisos actuales sin compromiso? Estamos a su disposición 😊",
        "permiso_no": "Tranquilo, estamos aquí para ayudarle a regularizar su actividad. Podemos visitarle para explicarle el proceso completo. Es totalmente gratuito 🙌 ¿Le gustaría agendar una cita?",
        "aclaracion_permiso_no": "🙏 Si está comenzando desde cero, podemos guiarle paso a paso. ¿Desea una cita gratuita para iniciar su proceso ambiental?",
        "cierre": "Solo indique el día y hora en que podríamos visitarle. Puede ser en la camaronera o en su oficina. La cita es gratuita 🙌",
        "aclaracion_cierre": "🙏 Para poder agendar, necesitamos saber qué día, hora y lugar prefiere para la reunión. Es completamente gratis 😊",
        "agradecimiento": "🙌 Su cita ha sido registrada. El Ing. Darwin González Romero se comunicará con usted mediante el número 0984770663 para coordinar los detalles. Gracias por confiar en DALGORO 🌊"
    },

    "mineria": {
        "introduccion": "⛏️ ¡Gracias por su mensaje! Trabajamos con actividades mineras para ayudarles a cumplir con los requisitos ambientales que exige la autoridad. ¿Nos puede indicar si ya cuenta con algún permiso como registro o licencia ambiental?\n\n👉 Ya tengo permiso\n👉 Aún no tengo",
        "aclaracion_introduccion": "🙏 ¿Nos puede confirmar si tiene algún tipo de permiso ambiental? Así podremos asesorarle correctamente 😊",
        "permiso_si": "✅ Excelente. Podemos revisar si está todo en regla y vigente. Podemos visitarle en su concesión o en su oficina para una evaluación técnica sin costo. ¿Desea agendarla?",
        "aclaracion_permiso_si": "🙏 ¿Desea que revisemos juntos sus permisos actuales en una visita sin compromiso? Estamos listos para ayudarle 😊",
        "permiso_no": "Comprendemos, muchos inician sin saber los pasos. Podemos ayudarle desde el inicio, sin costo. Podemos visitarle en la mina o en su oficina. ¿Le gustaría que coordinemos una cita?",
        "aclaracion_permiso_no": "🙏 ¿Le interesaría que le visitemos para explicarle cómo empezar el proceso de regularización ambiental? La asesoría es gratuita.",
        "cierre": "Solo indíquenos el día, hora y si prefiere que visitemos su mina o su oficina. La evaluación no tiene ningún costo ⛏️",
        "aclaracion_cierre": "🙏 No logramos identificar su disponibilidad. ¿Podría confirmarnos cuándo y dónde desea reunirse con nosotros? 😊",
        "agradecimiento": "🙌 Su cita fue registrada con éxito. El Ing. Darwin González Romero se comunicará con usted mediante el número 0984770663 para coordinar los detalles. ¡Gracias por su confianza! ⛏️"
    },
    
    "cacaotera": {
        "introduccion": "🍫 ¡Excelente actividad! Justamente nosotros trabajamos con productores cacaoteros como usted para que cumplan con la normativa ambiental sin complicaciones. ¿Nos puede confirmar si ya cuenta con permiso ambiental (registro o licencia)?\n\n👉 Ya tengo permiso\n👉 No tengo aún",
        "aclaracion_introduccion": "🙏 ¿Podría confirmarnos si tiene permiso ambiental? Así podremos darle una guía más adecuada 😊",
        "permiso_si": "✅ Perfecto. Es importante verificar que esté vigente y sin observaciones. Podemos hacer una visita técnica gratuita en su finca o en su oficina. ¿Desea agendarla?",
        "aclaracion_permiso_si": "🙏 ¿Le gustaría que revisemos sus documentos en una visita sin compromiso? Podemos ajustarnos a su disponibilidad 😊",
        "permiso_no": "No se preocupe, estamos para acompañarle desde el inicio. Podemos visitarle donde le quede mejor para explicarle los pasos a seguir. ¿Prefiere finca o su oficina? 🍫",
        "aclaracion_permiso_no": "🙏 Podemos iniciar juntos su proceso ambiental. ¿Le interesa una reunión gratuita para orientarle desde el principio?",
        "cierre": "Solo indíquenos día, hora y lugar donde podamos visitarle. Esta evaluación es completamente gratuita y sin compromiso 🙌",
        "aclaracion_cierre": "🙏 ¿Nos podría indicar cuándo y dónde prefiere que le visitemos? La cita es sin costo y 100% personalizada 🍃",
        "agradecimiento": "🙌 Su cita ha sido registrada. El Ing. Darwin González Romero se comunicará con usted mediante el número 0984770663 para coordinar los detalles. ¡Gracias por su confianza en nosotros! 🍫"
    },

    "ciclo_corto": {
        "introduccion": "🌽 ¡Excelente actividad! Si trabaja con cultivos de ciclo corto como maíz, arroz o hortalizas, es posible que requiera permisos ambientales. ¿Ya tiene algún permiso ambiental vigente?\n\n👉 Sí, ya tengo\n👉 No tengo aún",
        "aclaracion_introduccion": "🙏 ¿Nos puede indicar si ya cuenta con un registro o licencia ambiental para su cultivo? 😊",
        "permiso_si": "Excelente. Podemos verificar que esté actualizado y conforme con la normativa. Podemos visitarle sin costo para una evaluación técnica. ¿Le interesa?",
        "aclaracion_permiso_si": "🙏 ¿Desea que revisemos juntos sus documentos en una cita sin compromiso? Podemos ir a su finca u oficina 🌽",
        "permiso_no": "No hay problema. Podemos guiarle desde cero y explicarle cómo cumplir con la normativa sin complicarse. ¿Prefiere que le visitemos en su finca o en su oficina?",
        "aclaracion_permiso_no": "🙏 ¿Desea que le asesoremos para iniciar su proceso ambiental? Podemos hacerlo en una visita gratuita",
        "cierre": "Indíquenos por favor fecha, hora y lugar de la reunión. Será sin costo y le daremos una solución integral 🌱",
        "aclaracion_cierre": "🙏 Para confirmar la cita, necesitamos saber cuándo y dónde prefiere que lo visitemos. Recuerde que es una asesoría gratuita 📋",
        "agradecimiento": "🙌 Su cita fue registrada con éxito. El Ing. Darwin González Romero se comunicará con usted mediante el número 0984770663 para coordinar los detalles. Gracias por confiar en nosotros 🌾"
    },

    "granja_avicola": {
        "introduccion": "🐔 ¡Excelente actividad! Justamente nosotros ayudamos a granjas avícolas a cumplir con los permisos ambientales necesarios para operar sin sanciones. ¿Su granja ya tiene registro o licencia ambiental?\n\n👉 Sí, ya tiene\n👉 No tiene aún",
        "aclaracion_introduccion": "🙏 ¿Nos puede indicar si su granja cuenta con permiso ambiental? Así sabremos cómo ayudarle mejor 😊",
        "permiso_si": "Perfecto. Podemos verificar que esté vigente y sin observaciones. Podemos visitarle para una revisión técnica sin costo. ¿Le gustaría agendarla?",
        "aclaracion_permiso_si": "🙏 ¿Le interesa una evaluación gratuita para revisar sus permisos actuales? Podemos ajustarnos a su horario 🐔",
        "permiso_no": "Entiendo. Muchas granjas aún no lo tienen. Podemos ayudarle desde cero y explicarle cómo regularizarse. ¿Le gustaría que vayamos a su granja o a su oficina?",
        "aclaracion_permiso_no": "🙏 Si desea regularizar su actividad, podemos hacer una visita técnica gratuita. ¿Le interesa?",
        "cierre": "Solo necesitamos día, hora y el lugar que prefiera para su cita. La evaluación no tiene costo ni compromiso 🙌",
        "aclaracion_cierre": "🙏 ¿Nos puede decir cuándo y dónde desea reunirse con nosotros? Recuerde que la asesoría es gratuita 🐣",
        "agradecimiento": "🙌 Cita registrada correctamente. El Ing. Darwin González Romero se comunicará con usted mediante el número número 0984770663 para coordinar los detalles. ¡Gracias por confiar en nosotros! 🐥"
    },

    "granja_porcina": {
        "introduccion": "🐷 ¡Excelente actividad! Justamente nosotros nos especializamos en ayudar a granjas porcinas a cumplir con los requisitos ambientales exigidos por la autoridad. ¿Su granja ya cuenta con permiso ambiental?\n\n👉 Sí\n👉 No",
        "aclaracion_introduccion": "🙏 ¿Nos podría decir si su granja porcina tiene permiso ambiental (registro o licencia)? Así sabremos cómo ayudarle mejor 😊",
        "permiso_si": "Muy bien. Podemos realizar una visita técnica gratuita para revisar que todo esté conforme a la normativa. ¿Desea que la agendemos?",
        "aclaracion_permiso_si": "🙏 ¿Desea que revisemos sus permisos en una visita sin compromiso? Podemos ir hasta su granja o su oficina 🐷",
        "permiso_no": "No hay problema. Podemos ayudarle a iniciar el proceso desde cero. Le ofrecemos una reunión gratuita en la ubicación que prefiera. ¿Desea que le visitemos?",
        "aclaracion_permiso_no": "🙏 Podemos empezar con una visita técnica sin costo. ¿Le interesa coordinarla para su granja porcina?",
        "cierre": "Solo necesitamos día, hora y lugar donde podamos reunirnos con usted. La evaluación es gratuita 🐖",
        "aclaracion_cierre": "🙏 Para confirmar su cita, necesitamos saber cuándo y dónde desea que le visitemos. Estamos para ayudarle 😊",
        "agradecimiento": "🙌 Su cita fue registrada con éxito. El Ing. Darwin González Romero se comunicará con usted mediante el número 0984770663 para coordinar los detalles. Gracias por confiar en nosotros 🐽"
    },
    
 "hotel": {
        "introduccion": "🏨 ¡Excelente actividad! Justamente nosotros tenemos experiencia en asesorar a hoteles para que cumplan con los requisitos ambientales sin contratiempos. ¿Podría indicarnos si su hotel ya cuenta con permiso ambiental (registro o licencia)?\n\n👉 Sí, ya tiene\n👉 No tiene aún",
        "aclaracion_introduccion": "🙏 Para orientarle mejor, ¿su hotel ya tiene algún permiso ambiental? 😊",
        "permiso_si": "Perfecto. Podemos revisar que sus permisos estén actualizados y en regla. Podemos visitarle directamente en su hotel o en su oficina. ¿Desea agendar una evaluación gratuita?",
        "aclaracion_permiso_si": "🙏 ¿Desea que le visitemos para revisar sus documentos actuales? La asesoría es gratuita 🏨",
        "permiso_no": "No se preocupe, estamos aquí para ayudarle desde el inicio. Podemos explicarle todo el proceso en una visita gratuita a su hotel o a su oficina. ¿Le interesa agendarla?",
        "aclaracion_permiso_no": "🙏 Si desea empezar el proceso ambiental, podemos hacer una evaluación sin costo. ¿Desea que la coordinemos?",
        "cierre": "Solo necesitamos saber día, hora y si prefiere que lo visitemos en su hotel o en su oficina. La asesoría no tiene costo ni compromiso 🙌",
        "aclaracion_cierre": "🙏 ¿Nos puede confirmar cuándo y dónde desea que le visitemos? La evaluación es gratuita y personalizada 🏨",
        "agradecimiento": "🙌 Su cita fue registrada. El Ing. Darwin González Romero se comunicará con usted mediante el número 0984770663 para coordinar los detalles. ¡Gracias por su confianza! 🏨"
    },

    "industria": {
        "introduccion": "🏭 ¡Excelente actividad! Justamente nosotros apoyamos a empresas industriales a cumplir con todas sus obligaciones ambientales. ¿Actualmente su industria tiene registro o licencia ambiental?\n\n👉 Sí, ya tiene\n👉 No tiene aún",
        "aclaracion_introduccion": "🙏 ¿Nos puede confirmar si su empresa ya cuenta con permisos ambientales vigentes? Así sabremos cómo ayudarle 😊",
        "permiso_si": "Excelente. Podemos visitar su planta o su oficina para revisar si sus permisos están al día. ¿Desea que agendemos una evaluación gratuita?",
        "aclaracion_permiso_si": "🙏 ¿Desea que le visitemos para una evaluación técnica de sus permisos actuales? Sin costo y sin compromiso 🏭",
        "permiso_no": "Podemos acompañarle desde cero para que cumpla con toda la normativa. Podemos visitarle donde le sea más cómodo. ¿Le gustaría agendar una cita gratuita?",
        "aclaracion_permiso_no": "🙏 Si desea comenzar su proceso ambiental, podemos guiarle paso a paso. ¿Desea una reunión sin compromiso?",
        "cierre": "Por favor indíquenos día, hora y lugar para su evaluación técnica. Podemos visitarle en planta o en oficina. La cita no tiene costo 🙌",
        "aclaracion_cierre": "🙏 ¿Cuándo y dónde le gustaría que le visitemos? La asesoría es totalmente gratuita y personalizada 🏗️",
        "agradecimiento": "🙌 Cita registrada exitosamente. El Ing. Darwin González Romero se comunicará con usted mediante el número 0984770663 para coordinar los detalles. ¡Gracias por confiar en DALGORO! 🏭"
    },

    "otros": {
        "introduccion": "🌿 Muy bien entiendo. Para poder orientarle mejor, nos gustaría conocer más sobre su actividad productiva. Podemos visitarle personalmente para entender su situación y brindarle una solución completa. ¿Le gustaría agendar una evaluación gratuita?\n\n👉 Sí, deseo agendar\n👉 No por ahora",
        "aclaracion_introduccion": "🙏 ¿Desea que le visitemos para conocer mejor su actividad y orientarle con una evaluación gratuita? 🌿",
        "permiso_si": "Gracias por compartirlo. Podemos revisar que todo esté conforme a la normativa. La asesoría es gratuita y personalizada. ¿Cuándo le viene bien que le visitemos?",
        "aclaracion_permiso_si": "🙏 ¿Nos puede indicar si desea la evaluación para validar sus permisos actuales? Podemos ir hasta su oficina o sitio de operación 😊",
        "permiso_no": "Estamos aquí para acompañarle desde el inicio. Podemos ir a su oficina o donde usted nos indique. Solo necesitamos coordinar día y hora. ¿Le interesa?",
        "aclaracion_permiso_no": "🙏 ¿Desea nuestra ayuda para iniciar su proceso ambiental? Solo indíquenos si desea una cita presencial gratuita",
        "cierre": "Indíquenos cuándo y dónde desea que le visitemos. La evaluación es gratuita y sin compromiso 🌱",
        "aclaracion_cierre": "🙏 ¿Nos puede decir día, hora y lugar para programar su cita? Le visitaremos con gusto para conocer su caso de forma directa",
        "agradecimiento": "🙌 Su cita ha sido registrada correctamente. El Ing. Darwin González Romero se comunicará con usted mediante el número 0984770663 para confirmar los detalles. ¡Gracias por confiar en nosotros! 🌿"
    }
} 

# Refuerzo de seguridad para asegurar que todas las actividades tengan clave 'agradecimiento'
for actividad in [
    "bananera", "camaronera", "mineria", "cacaotera", "ciclo_corto",
    "granja_avicola", "granja_porcina", "hotel", "industria", "otros"
]:
    if actividad not in FLUJOS_POR_ACTIVIDAD:
        FLUJOS_POR_ACTIVIDAD[actividad] = {}
    if "agradecimiento" not in FLUJOS_POR_ACTIVIDAD[actividad]:
        FLUJOS_POR_ACTIVIDAD[actividad]["agradecimiento"] = "✅ Su cita ha sido registrada correctamente. El Ing. Darwin González Romero se comunicará con usted mediante el número 0984770663 para confirmar los detalles. ¡Gracias por confiar en nosotros! 🌿"

def obtener_respuesta_por_actividad(actividad, etapa):
    flujo = FLUJOS_POR_ACTIVIDAD.get(actividad, {})

    if not etapa:
        return "🤖 Aún no logro comprender su solicitud. ¿Podría explicarnos un poco más sobre su actividad o requerimiento?"

    # Limpieza automática de errores comunes como 'aclaracion_aclaracion_permiso_si'
    etapa_limpia = etapa
    while etapa_limpia.startswith("aclaracion_aclaracion_"):
        etapa_limpia = etapa_limpia.replace("aclaracion_aclaracion_", "aclaracion_", 1)

    if etapa_limpia not in flujo:
        etapa_limpia = etapa_limpia.replace("aclaracion_", "")
    
    respuesta = flujo.get(etapa_limpia)
    
    if respuesta:
        return respuesta
    else:
        return "📝 Estamos para ayudarle. ¿Podría indicarnos si ya cuenta con permisos ambientales o desea iniciar el proceso?"

def detectar_actividad(texto):
    texto = texto.lower().strip()

    if any(p in texto for p in [
        "banano", "bananera", "finca bananera", "plantación de banano", "guineo", "guineal", "banana"
    ]):
        return "bananera"

    elif any(p in texto for p in [
        "camaronera", "camarón", "piscina camaronera", "piscinas", "camaronicultura", "piscinas de camarón"
    ]):
        return "camaronera"

    elif any(p in texto for p in [
        "minería", "mina", "material pétreo", "extracción minera", "cantera", "áridos", "grava", "ripio", "piedra"
    ]):
        return "mineria"

    elif any(p in texto for p in [
        "cacao", "cacaotera", "plantación de cacao", "cacaotal", "trabajo con cacao", "finca de cacao"
    ]):
        return "cacaotera"

    elif any(p in texto for p in [
        "ciclo corto", "maíz", "arroz", "hortalizas", "cultivo pequeño", "frijol", "frejol", "legumbres", "tomate", "cebolla", "verde"
    ]):
        return "ciclo corto"

    elif any(p in texto for p in [
        "cerdo", "porcino", "granja porcina", "chancho", "lechón", "cría de cerdos", "cerdos", "chanchería"
    ]):
        return "granja porcina"

    elif any(p in texto for p in [
        "pollo", "gallina", "granja avícola", "aves", "pollos", "ponedoras", "gallinero", "pollera"
    ]):
        return "granja avicola"

    elif any(p in texto for p in [
        "hotel", "hospedaje", "hostal", "turismo", "alojamiento", "cabañas", "resort"
    ]):
        return "hotel"

    elif any(p in texto for p in [
        "industria", "fábrica", "empresa industrial", "procesadora", "procesamiento", "industrial"
    ]):
        return "industria"

    # Si el texto es suficientemente largo, se asume como "otros"
    if len(texto) >= 10:
        return "otros"

    # Si no hay coincidencia ni suficiente información
    return None

PERMISOS_SI = [
    "sí tengo", "ya tengo", "cuento con permiso", "cuento con registro", "sí contamos", "sí, tengo", 
    "tengo permiso", "sí", "sí tengo los papeles", "sí tengo la licencia", "sí tengo el permiso",
    "sí cuento con eso", "sí cuento con el registro", "sí tengo eso al día", 
    "mis papeles están en regla", "sí, ya está hecho", "ya tengo todo", 
    "sí me lo aprobaron", "me lo dieron hace tiempo", "ya está aprobado", 
    "ya está legalizado", "sí, está vigente", "sí está al día", 
    "sí, lo tengo actualizado", "sí, me lo entregaron", "sí está en orden", 
    "tengo los documentos listos", "ya tengo todo en regla"
]

PERMISOS_NO = [
    "no tengo", "no contamos", "aún no", "todavía no", "ninguno", "no", 
    "no tengo ninguno", "no cuento con", "aún no he sacado", "no me lo han dado", 
    "todavía no lo tramito", "no está hecho", "aún no empiezo", "no tengo los papeles", 
    "no he hecho el trámite", "no tengo ese permiso", "no tengo el registro", 
    "me falta sacar eso", "estoy en eso", "me falta eso", "no lo he gestionado", 
    "no me han aprobado nada", "nunca he hecho ese trámite", 
    "no me han dado nada", "no está legalizado", "no tengo nada aún"
]

def contiene_permiso_si(texto):
    texto = texto.lower()
    return any(exp in texto for exp in PERMISOS_SI)

def contiene_permiso_no(texto):
    texto = texto.lower()
    return any(exp in texto for exp in PERMISOS_NO)

for actividad in FLUJOS_POR_ACTIVIDAD:
    FLUJOS_POR_ACTIVIDAD[actividad]["salida_amable"] = (
        "👌 Entiendo perfectamente. Si más adelante desea nuestra ayuda ambiental, estaremos disponibles por este medio. "
        "Gracias por habernos escrito 🌱"
    )
