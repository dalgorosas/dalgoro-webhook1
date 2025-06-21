import difflib

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
        "introduccion": "🍌 ¡Qué buena noticia! Justo nos especializamos en apoyar a fincas bananeras como la suya en todo lo relacionado al cumplimiento ambiental.\nPara saber cómo podemos ayudarle mejor, ¿me puede contar si ya cuenta con un permiso ambiental, como un registro o una licencia?\n\n👉 Ya tengo permiso\n👉 Aún no tengo ninguno",
        "aclaracion_introduccion": "🙏 ¡Gracias por responder! Para poder orientarle mejor, ¿me podría confirmar si ya cuenta con algún tipo de permiso ambiental (registro o licencia)?\nCon eso podremos ajustar mejor la asesoría para su caso 🌿",
        "permiso_si": "✅ Perfecto, eso ya es un buen paso. Tener un permiso ambiental demuestra compromiso, pero también es clave mantenerlo actualizado y sin observaciones.\n\nPodemos revisar su documentación y explicarle si hay algo que necesita mejorar para evitar sanciones o rechazos futuros.\n\nEsta revisión es gratuita y se adapta a su caso particular 🌿\n\n¿Le gustaría saber cómo funciona este proceso de verificación y cómo podemos ayudarle?",
        "aclaracion_permiso_si": "🙏 Gracias por el detalle. Podemos ayudarle revisando sus permisos actuales y orientándole sobre cómo mantener todo al día sin complicaciones.\n\nNuestro equipo puede explicarle paso a paso qué revisar, cómo corregir observaciones y cómo estar tranquilo ante una inspección ambiental.\n\n¿Desea que le contemos cómo funciona esa revisión gratuita y lo que incluye?",
        "permiso_no": "No se preocupe, todos empezamos por algún lado. Lo bueno es que en este momento usted ya está dando el paso correcto 💪\n\nPodemos acompañarle desde cero, explicándole paso a paso lo que necesita y cómo conseguir sus permisos sin complicaciones.\nEsta asesoría es totalmente gratuita y puede marcar la diferencia en el cumplimiento ambiental de su finca 🌿\n\n¿Le interesa que le contemos cómo sería ese proceso y lo que incluiría?",
        "aclaracion_permiso_no": "🙏 Gracias por escribirnos. Si quiere, podemos explicarle cómo se obtiene el permiso ambiental desde cero, paso a paso, y así evitar sanciones o rechazos más adelante.\n\n¿Le gustaría que le contemos cómo funciona?",
        "cierre": "Perfecto, estamos listos para agendar su evaluación gratuita ✅\n\n¿Podría indicarnos el día, la hora y si prefiere que vayamos a su finca o a su oficina?\nEs un servicio sin costo y totalmente personalizado 🌱",
        "aclaracion_cierre": "🙏 Para poder agendar su visita, solo necesito que me indique:\n\n📅 Día\n⏰ Hora\n📍 Lugar (finca u oficina)\n\nRecuerde que es 100/100 gratuita y sin compromiso 🙌",
        "agradecimiento": "🙌 ¡Listo! Su cita ha quedado registrada con éxito.\n\nEl Ing. Darwin González Romero se comunicará con usted para coordinar los detalles.\n\nMuchas gracias por confiar en nosotros. Estamos aquí para ayudarle a que su finca cumpla con todo y sin complicaciones 🌿"
    },

    "camaronera": {
        "introduccion": "🦐 ¡Excelente! Justo trabajamos con camaroneras que buscan cumplir con los requisitos ambientales sin complicaciones.\nPara brindarle una orientación adecuada, ¿me puede contar si ya cuenta con un permiso ambiental, como un registro o una licencia?\n\n👉 Ya tengo permiso\n👉 Aún no tengo ninguno",
        "aclaracion_introduccion": "🙏 Gracias por responder. Para orientarle mejor, ¿me podría confirmar si ya cuenta con algún tipo de permiso ambiental (registro o licencia)?\nCon eso podremos ajustar la asesoría a su situación específica 🌿",
        "permiso_si": "✅ Perfecto, eso ya es un buen paso. Tener un permiso ambiental demuestra compromiso, pero también es clave mantenerlo actualizado y sin observaciones.\n\nPodemos revisar su documentación y explicarle si hay algo que necesita mejorar para evitar sanciones o rechazos futuros.\n\nEsta revisión es gratuita y se adapta a su caso particular 🌿\n\n¿Le gustaría saber cómo funciona este proceso de verificación y cómo podemos ayudarle?",
        "aclaracion_permiso_si": "🙏 Gracias por el detalle. Podemos ayudarle revisando sus permisos actuales y orientándole sobre cómo mantener todo al día sin complicaciones.\n\nNuestro equipo puede explicarle paso a paso qué revisar, cómo corregir observaciones y cómo estar tranquilo ante una inspección ambiental.\n\n¿Desea que le contemos cómo funciona esa revisión gratuita y lo que incluye?",
        "permiso_no": "No se preocupe, todos empezamos por algún lado. Lo bueno es que en este momento usted ya está dando el paso correcto 💪\n\nPodemos acompañarle desde cero, explicándole paso a paso lo que necesita y cómo conseguir sus permisos sin complicaciones.\nEsta asesoría es totalmente gratuita y puede marcar la diferencia en el cumplimiento ambiental de su camaronera 🌿\n\n¿Le interesa que le contemos cómo sería ese proceso y lo que incluiría?",
        "aclaracion_permiso_no": "🙏 Gracias por escribirnos. Si quiere, podemos explicarle cómo se obtiene el permiso ambiental desde cero, paso a paso, y así evitar sanciones o rechazos más adelante.\n\n¿Le gustaría que le contemos cómo funciona?",
        "cierre": "Perfecto, estamos listos para agendar su evaluación gratuita ✅\n\n¿Podría indicarnos el día, la hora y si prefiere que vayamos a su camaronera o a su oficina?\nEs un servicio sin costo y totalmente personalizado 🌱",
        "aclaracion_cierre": "🙏 Para poder agendar su visita, solo necesito que me indique:\n\n📅 Día\n⏰ Hora\n📍 Lugar (camaronera u oficina)\n\nRecuerde que es 100/100 gratuita y sin compromiso 🙌",
        "agradecimiento": "🙌 ¡Listo! Su cita ha quedado registrada con éxito.\n\nEl Ing. Darwin González Romero se comunicará con usted para coordinar los detalles.\n\nMuchas gracias por confiar en nosotros. Estamos aquí para ayudarle a que su camaronera cumpla con todo y sin complicaciones 🌿"
    },

    "minería": {
        "introduccion": "⛏️ Gracias por contactarnos. Trabajamos con varios proyectos mineros que necesitan cumplir correctamente con los requisitos ambientales.\nPara brindarle una asesoría ajustada a su caso, ¿me puede contar si ya cuenta con un permiso ambiental, como un registro o una licencia?\n\n👉 Ya tengo permiso\n👉 Aún no tengo ninguno",
        "aclaracion_introduccion": "🙏 Gracias por su respuesta. Solo para confirmar, ¿ya cuenta con algún tipo de permiso ambiental (registro o licencia)?\nCon eso podremos enfocar mejor nuestra asesoría 🌿",
        "permiso_si": "✅ Excelente, ese ya es un buen paso. Tener un permiso ambiental es fundamental, pero también es importante que esté vigente y sin observaciones.\n\nPodemos revisar sus documentos y explicarle si hay algo que podría mejorar o actualizar para evitar sanciones o rechazos.\n\nEsta revisión es gratuita y adaptada a su operación minera 🌿\n\n¿Le gustaría saber cómo funciona este proceso de verificación y cómo podemos ayudarle?",
        "aclaracion_permiso_si": "🙏 Gracias por el detalle. Podemos ayudarle revisando los permisos que ya tiene y guiándole para que todo esté al día y en regla.\n\nLe explicamos paso a paso qué revisar, cómo prevenir observaciones y cómo prepararse para auditorías o inspecciones.\n\n¿Desea que le contemos cómo funciona esa revisión gratuita y lo que incluye?",
        "permiso_no": "No se preocupe, todos empezamos por algún lado. Lo importante es que ya está tomando el paso correcto 💪\n\nPodemos acompañarle desde cero, explicándole qué necesita y cómo obtener sus permisos sin complicaciones.\nEsta asesoría es totalmente gratuita y puede marcar la diferencia en la viabilidad ambiental de su proyecto 🌿\n\n¿Le interesa que le contemos cómo sería ese proceso y lo que incluiría?",
        "aclaracion_permiso_no": "🙏 Gracias por escribirnos. Si lo desea, podemos explicarle cómo se obtiene el permiso ambiental paso a paso, y cómo evitar sanciones o rechazos más adelante.\n\n¿Le gustaría que le contemos cómo funciona?",
        "cierre": "Perfecto, estamos listos para agendar su evaluación gratuita ✅\n\n¿Podría indicarnos el día, la hora y si prefiere que vayamos al sitio del proyecto o a su oficina?\nEs un servicio sin costo y totalmente personalizado 🌱",
        "aclaracion_cierre": "🙏 Para poder agendar su visita, solo necesito que me indique:\n\n📅 Día\n⏰ Hora\n📍 Lugar (proyecto u oficina)\n\nRecuerde que es 100/100 gratuita y sin compromiso 🙌",
        "agradecimiento": "🙌 ¡Listo! Su cita ha quedado registrada con éxito.\n\nEl Ing. Darwin González Romero se comunicará con usted para coordinar los detalles.\n\nMuchas gracias por confiar en nosotros. Estamos aquí para ayudarle a que su proyecto minero cumpla con todo y sin complicaciones 🌿"
    },

    "cacaotera": {
        "introduccion": "🍫 ¡Qué gusto recibir su mensaje! Apoyamos a fincas cacaoteras que desean cumplir con la normativa ambiental de forma clara y sin complicaciones.\nPara poder ayudarle mejor, ¿me puede contar si ya cuenta con un permiso ambiental, como un registro o una licencia?\n\n👉 Ya tengo permiso\n👉 Aún no tengo ninguno",
        "aclaracion_introduccion": "🙏 Gracias por responder. ¿Me podría confirmar si ya cuenta con algún tipo de permiso ambiental (registro o licencia)?\nAsí podremos ajustar la asesoría a su situación 🌿",
        "permiso_si": "✅ Excelente, ese ya es un gran paso. Tener un permiso ambiental es importante, pero también es clave mantenerlo vigente y sin observaciones que puedan afectar su producción.\n\nPodemos revisar su documentación y explicarle si hay algo que necesite actualizar para evitar sanciones o rechazos.\n\nEsta revisión es gratuita y adaptada a su finca cacaotera 🌱\n\n¿Le gustaría saber cómo funciona este proceso de verificación y cómo podemos ayudarle?",
        "aclaracion_permiso_si": "🙏 Gracias por el detalle. Podemos ayudarle revisando los permisos que ya tiene y orientándole para mantener todo en regla sin complicaciones.\n\nNuestro equipo le explicará paso a paso qué revisar y cómo estar tranquilo ante una inspección ambiental.\n\n¿Desea que le contemos cómo funciona esa revisión gratuita y lo que incluye?",
        "permiso_no": "No se preocupe, todos empezamos por algún lado. Lo importante es que usted ya está tomando el camino correcto 💪\n\nPodemos acompañarle desde cero, explicándole qué necesita y cómo obtener sus permisos sin complicaciones.\nEsta asesoría es totalmente gratuita y puede marcar una gran diferencia en la gestión ambiental de su finca 🌿\n\n¿Le interesa que le contemos cómo sería ese proceso y lo que incluiría?",
        "aclaracion_permiso_no": "🙏 Gracias por escribirnos. Si lo desea, podemos explicarle cómo obtener el permiso ambiental desde cero, paso a paso, y así evitar sanciones o rechazos más adelante.\n\n¿Le gustaría que le contemos cómo funciona?",
        "cierre": "Perfecto, estamos listos para agendar su evaluación gratuita ✅\n\n¿Podría indicarnos el día, la hora y si prefiere que vayamos a su finca o a su oficina?\nEs un servicio sin costo y totalmente personalizado 🌱",
        "aclaracion_cierre": "🙏 Para poder agendar su visita, solo necesito que me indique:\n\n📅 Día\n⏰ Hora\n📍 Lugar (finca u oficina)\n\nRecuerde que es 100/100 gratuita y sin compromiso 🙌",
        "agradecimiento": "🙌 ¡Listo! Su cita ha quedado registrada con éxito.\n\nEl Ing. Darwin González Romero se comunicará con usted para coordinar los detalles.\n\nMuchas gracias por confiar en nosotros. Estamos aquí para ayudarle a que su finca cumpla con todo y sin complicaciones 🌿"
    },

    "cultivo de ciclo corto": {
        "introduccion": "🌽 ¡Qué gusto saber de usted! Apoyamos cultivos de ciclo corto que necesitan cumplir con la normativa ambiental sin complicarse.\nPara brindarle una asesoría ajustada a su caso, ¿me puede contar si ya cuenta con un permiso ambiental, como un registro o una licencia?\n\n👉 Ya tengo permiso\n👉 Aún no tengo ninguno",
        "aclaracion_introduccion": "🙏 Gracias por responder. ¿Me podría confirmar si ya cuenta con algún tipo de permiso ambiental (registro o licencia)?\nAsí podremos adaptar mejor la asesoría a su situación 🌿",
        "permiso_si": "✅ Muy bien, contar con un permiso ambiental es un gran paso, pero es importante que esté actualizado y sin observaciones.\n\nPodemos revisar su documentación y explicarle si hay algo que necesita corregir o actualizar para evitar sanciones.\n\nEsta revisión es gratuita y enfocada en cultivos de ciclo corto 🌱\n\n¿Le gustaría saber cómo funciona este proceso y cómo podemos ayudarle?",
        "aclaracion_permiso_si": "🙏 Gracias por el detalle. Podemos ayudarle revisando sus permisos y orientándole para mantener todo en regla sin complicaciones.\n\nLe explicamos paso a paso qué revisar y cómo estar preparado ante una inspección ambiental.\n\n¿Desea que le contemos cómo funciona esa revisión gratuita y lo que incluye?",
        "permiso_no": "No se preocupe, todos empezamos por algún lado. Lo importante es que ya está dando el paso correcto 💪\n\nPodemos acompañarle desde cero, explicándole lo que necesita y cómo obtener sus permisos sin complicarse.\nEsta asesoría es gratuita y puede marcar una gran diferencia para su cultivo 🌿\n\n¿Le interesa que le contemos cómo sería ese proceso y lo que incluiría?",
        "aclaracion_permiso_no": "🙏 Gracias por escribirnos. Si lo desea, podemos explicarle cómo se obtiene el permiso ambiental paso a paso, y así evitar sanciones o rechazos más adelante.\n\n¿Le gustaría que le contemos cómo funciona?",
        "cierre": "Perfecto, estamos listos para agendar su evaluación gratuita ✅\n\n¿Podría indicarnos el día, la hora y si prefiere que vayamos a su finca o a su oficina?\nEs un servicio sin costo y totalmente personalizado 🌱",
        "aclaracion_cierre": "🙏 Para poder agendar su visita, solo necesito que me indique:\n\n📅 Día\n⏰ Hora\n📍 Lugar (finca u oficina)\n\nRecuerde que es 100/100 gratuita y sin compromiso 🙌",
        "agradecimiento": "🙌 ¡Listo! Su cita ha quedado registrada con éxito.\n\nEl Ing. Darwin González Romero se comunicará con usted para coordinar los detalles.\n\nMuchas gracias por confiar en nosotros. Estamos aquí para ayudarle a que su cultivo cumpla con todo y sin complicaciones 🌿"
    },

    "granja porcina": {
        "introduccion": "🐖 ¡Qué bueno que nos contacta! Apoyamos a granjas porcinas en todo el proceso de cumplimiento ambiental, desde los permisos hasta el manejo adecuado de residuos.\nPara poder ayudarle mejor, ¿me puede contar si ya cuenta con un permiso ambiental, como un registro o una licencia?\n\n👉 Ya tengo permiso\n👉 Aún no tengo ninguno",
        "aclaracion_introduccion": "🙏 Gracias por responder. ¿Me podría confirmar si ya cuenta con algún tipo de permiso ambiental (registro o licencia)?\nAsí podremos ofrecerle una asesoría ajustada a su caso 🌿",
        "permiso_si": "✅ Excelente, ya tener un permiso es un buen avance. Sin embargo, es importante revisar que esté vigente y que no haya observaciones pendientes que puedan generar problemas.\n\nPodemos revisar sus documentos y explicarle si hay algo que necesita actualizar para evitar sanciones.\n\nEsta revisión es gratuita y enfocada en granjas porcinas como la suya 🌱\n\n¿Le gustaría saber cómo funciona este proceso de verificación y cómo podemos ayudarle?",
        "aclaracion_permiso_si": "🙏 Gracias por el detalle. Podemos ayudarle revisando su permiso actual y orientándole para mantener todo al día.\n\nLe explicamos paso a paso qué revisar, cómo evitar observaciones y estar tranquilo ante cualquier inspección.\n\n¿Desea que le contemos cómo funciona esa revisión gratuita y lo que incluye?",
        "permiso_no": "No se preocupe, todos empezamos por algún lado. Lo importante es que usted ya está tomando el paso correcto 💪\n\nPodemos acompañarle desde cero, explicándole lo que necesita y cómo obtener sus permisos sin complicarse.\nEsta asesoría es gratuita y puede marcar una gran diferencia para su granja porcina 🌿\n\n¿Le interesa que le contemos cómo sería ese proceso y lo que incluiría?",
        "aclaracion_permiso_no": "🙏 Gracias por escribirnos. Si lo desea, podemos explicarle cómo se obtiene el permiso ambiental paso a paso, y cómo evitar sanciones o rechazos más adelante.\n\n¿Le gustaría que le contemos cómo funciona?",
        "cierre": "Perfecto, estamos listos para agendar su evaluación gratuita ✅\n\n¿Podría indicarnos el día, la hora y si prefiere que vayamos a su granja o a su oficina?\nEs un servicio sin costo y totalmente personalizado 🌱",
        "aclaracion_cierre": "🙏 Para poder agendar su visita, solo necesito que me indique:\n\n📅 Día\n⏰ Hora\n📍 Lugar (granja u oficina)\n\nRecuerde que es 100/100 gratuita y sin compromiso 🙌",
        "agradecimiento": "🙌 ¡Listo! Su cita ha quedado registrada con éxito.\n\nEl Ing. Darwin González Romero se comunicará con usted para coordinar los detalles.\n\nMuchas gracias por confiar en nosotros. Estamos aquí para ayudarle a que su granja cumpla con todo y sin complicaciones 🌿"
    },

    "granja avícola": {
        "introduccion": "🐔 ¡Qué gusto saber de usted! Trabajamos con granjas avícolas que desean cumplir con la normativa ambiental de forma clara y sin complicaciones.\nPara poder brindarle una asesoría adecuada, ¿me puede contar si ya cuenta con un permiso ambiental, como un registro o una licencia?\n\n👉 Ya tengo permiso\n👉 Aún no tengo ninguno",
        "aclaracion_introduccion": "🙏 Gracias por responder. ¿Me podría confirmar si ya cuenta con algún tipo de permiso ambiental (registro o licencia)?\nAsí podremos adaptar la asesoría a su caso 🌿",
        "permiso_si": "✅ Excelente, contar con un permiso ambiental es un paso clave, pero también es importante asegurarse de que esté actualizado y sin observaciones pendientes.\n\nPodemos revisar su documentación y explicarle si hay algo que necesita corregir para evitar sanciones o rechazos.\n\nEsta revisión es gratuita y está enfocada en granjas avícolas como la suya 🌱\n\n¿Le gustaría saber cómo funciona este proceso de verificación y cómo podemos ayudarle?",
        "aclaracion_permiso_si": "🙏 Gracias por el detalle. Podemos ayudarle revisando su permiso actual y guiándole para mantener todo al día sin complicaciones.\n\nLe explicamos paso a paso qué revisar y cómo evitar problemas durante una inspección ambiental.\n\n¿Desea que le contemos cómo funciona esa revisión gratuita y lo que incluye?",
        "permiso_no": "No se preocupe, todos empezamos por algún lado. Lo importante es que usted ya está dando el paso correcto 💪\n\nPodemos acompañarle desde cero, explicándole lo que necesita y cómo obtener sus permisos sin complicarse.\nEsta asesoría es gratuita y puede marcar una gran diferencia para su granja avícola 🌿\n\n¿Le interesa que le contemos cómo sería ese proceso y lo que incluiría?",
        "aclaracion_permiso_no": "🙏 Gracias por escribirnos. Si lo desea, podemos explicarle cómo obtener el permiso ambiental paso a paso, y así evitar sanciones o rechazos más adelante.\n\n¿Le gustaría que le contemos cómo funciona?",
        "cierre": "Perfecto, estamos listos para agendar su evaluación gratuita ✅\n\n¿Podría indicarnos el día, la hora y si prefiere que vayamos a su granja o a su oficina?\nEs un servicio sin costo y totalmente personalizado 🌱",
        "aclaracion_cierre": "🙏 Para poder agendar su visita, solo necesito que me indique:\n\n📅 Día\n⏰ Hora\n📍 Lugar (granja u oficina)\n\nRecuerde que es 100/100 gratuita y sin compromiso 🙌",
        "agradecimiento": "🙌 ¡Listo! Su cita ha quedado registrada con éxito.\n\nEl Ing. Darwin González Romero se comunicará con usted para coordinar los detalles.\n\nMuchas gracias por confiar en nosotros. Estamos aquí para ayudarle a que su granja cumpla con todo y sin complicaciones 🌿"
    },

    "hotel": {
        "introduccion": "🏨 ¡Gracias por escribirnos! Ayudamos a hoteles a cumplir con todos los requisitos ambientales, de manera clara y sin complicaciones.\nPara orientarle mejor, ¿me puede contar si ya cuenta con un permiso ambiental, como un registro o una licencia?\n\n👉 Ya tengo permiso\n👉 Aún no tengo ninguno",
        "aclaracion_introduccion": "🙏 Gracias por responder. ¿Me podría confirmar si ya cuenta con algún tipo de permiso ambiental (registro o licencia)?\nCon eso podremos ajustar la asesoría a la situación de su hotel 🌿",
        "permiso_si": "✅ Perfecto, contar con un permiso ambiental es un buen paso. Sin embargo, es importante asegurarse de que esté actualizado y sin observaciones que puedan afectar el funcionamiento del hotel.\n\nPodemos revisar su documentación y explicarle si hay algo que necesita corregir o mejorar.\n\nEsta revisión es gratuita y pensada para establecimientos como el suyo 🌱\n\n¿Le gustaría saber cómo funciona este proceso de verificación y cómo podemos ayudarle?",
        "aclaracion_permiso_si": "🙏 Gracias por el detalle. Podemos ayudarle revisando su permiso actual y guiándole para mantener todo en regla y sin complicaciones.\n\nLe explicamos paso a paso qué revisar, cómo prepararse para inspecciones y cómo evitar observaciones.\n\n¿Desea que le contemos cómo funciona esa revisión gratuita y lo que incluye?",
        "permiso_no": "No se preocupe, todos empezamos por algún lado. Lo importante es que usted ya está tomando el paso correcto 💪\n\nPodemos acompañarle desde cero, explicándole lo que necesita y cómo obtener sus permisos sin complicarse.\nEsta asesoría es gratuita y puede marcar una gran diferencia para su hotel 🌿\n\n¿Le interesa que le contemos cómo sería ese proceso y lo que incluiría?",
        "aclaracion_permiso_no": "🙏 Gracias por escribirnos. Si lo desea, podemos explicarle cómo se obtiene el permiso ambiental paso a paso, y cómo evitar sanciones o rechazos más adelante.\n\n¿Le gustaría que le contemos cómo funciona?",
        "cierre": "Perfecto, estamos listos para agendar su evaluación gratuita ✅\n\n¿Podría indicarnos el día, la hora y si prefiere que vayamos a su hotel o a su oficina?\nEs un servicio sin costo y totalmente personalizado 🌱",
        "aclaracion_cierre": "🙏 Para poder agendar su visita, solo necesito que me indique:\n\n📅 Día\n⏰ Hora\n📍 Lugar (hotel u oficina)\n\nRecuerde que es 100/100 gratuita y sin compromiso 🙌",
        "agradecimiento": "🙌 ¡Listo! Su cita ha quedado registrada con éxito.\n\nEl Ing. Darwin González Romero se comunicará con usted para coordinar los detalles.\n\nMuchas gracias por confiar en nosotros. Estamos aquí para ayudarle a que su hotel cumpla con todo y sin complicaciones 🌿"
    },

    "industria": {
        "introduccion": "🏭 ¡Un gusto recibir su mensaje! Asesoramos a industrias que necesitan cumplir con los requisitos ambientales para operar con tranquilidad y sin complicaciones.\nPara poder ayudarle mejor, ¿me puede contar si ya cuenta con un permiso ambiental, como un registro o una licencia?\n\n👉 Ya tengo permiso\n👉 Aún no tengo ninguno",
        "aclaracion_introduccion": "🙏 Gracias por responder. ¿Me podría confirmar si ya cuenta con algún tipo de permiso ambiental (registro o licencia)?\nAsí podremos ajustar la asesoría a su caso específico 🌿",
        "permiso_si": "✅ Excelente. Tener un permiso ambiental es esencial, pero también es importante verificar que esté vigente y que no tenga observaciones que puedan generar sanciones.\n\nPodemos revisar su documentación actual y explicarle si hay algo que conviene corregir o actualizar.\n\nEsta revisión es gratuita y adaptada al tipo de actividad que maneja su industria 🌱\n\n¿Le gustaría saber cómo funciona este proceso de verificación y cómo podemos ayudarle?",
        "aclaracion_permiso_si": "🙏 Gracias por el detalle. Podemos ayudarle revisando el permiso que ya tiene y guiándole para mantener todo en regla sin complicaciones.\n\nLe explicamos paso a paso qué revisar, cómo prepararse para auditorías y evitar observaciones ambientales.\n\n¿Desea que le contemos cómo funciona esa revisión gratuita y lo que incluye?",
        "permiso_no": "No se preocupe, todos empezamos por algún lado. Lo importante es que ya está dando el paso correcto 💪\n\nPodemos acompañarle desde cero, explicándole qué necesita y cómo obtener sus permisos sin complicarse.\nEsta asesoría es totalmente gratuita y puede marcar una gran diferencia para el cumplimiento ambiental de su industria 🌿\n\n¿Le interesa que le contemos cómo sería ese proceso y lo que incluiría?",
        "aclaracion_permiso_no": "🙏 Gracias por escribirnos. Si lo desea, podemos explicarle cómo se obtiene el permiso ambiental paso a paso, y cómo evitar sanciones o rechazos más adelante.\n\n¿Le gustaría que le contemos cómo funciona?",
        "cierre": "Perfecto, estamos listos para agendar su evaluación gratuita ✅\n\n¿Podría indicarnos el día, la hora y si prefiere que vayamos a su planta industrial o a su oficina?\nEs un servicio sin costo y totalmente personalizado 🌱",
        "aclaracion_cierre": "🙏 Para poder agendar su visita, solo necesito que me indique:\n\n📅 Día\n⏰ Hora\n📍 Lugar (planta u oficina)\n\nRecuerde que es 100/100 gratuita y sin compromiso 🙌",
        "agradecimiento": "🙌 ¡Listo! Su cita ha quedado registrada con éxito.\n\nEl Ing. Darwin González Romero se comunicará con usted para coordinar los detalles.\n\nMuchas gracias por confiar en nosotros. Estamos aquí para ayudarle a que su industria cumpla con todo y sin complicaciones 🌿"
    },

    "otros": {
        "introduccion": (
        "🌿 Entendido, gracias por su mensaje. Para poder orientarle mejor, nos gustaría conocer un poco más sobre su actividad productiva.\n\n"
        "Podemos visitarle personalmente para entender su caso y brindarle una solución completa, sin compromiso.\n\n"
        "¿Le gustaría agendar una evaluación gratuita o prefiere primero conocer más detalles?\n\n"
        "👉 Sí, deseo agendar\n👉 No por ahora"
        ),
        "aclaracion_introduccion": (
        "🙏 Solo para confirmar, ¿le gustaría que le visitemos o prefiere primero que le expliquemos cómo funciona el proceso?\n\n"
        "La evaluación es gratuita y sin compromiso, y le ayudará a tener claridad sobre sus obligaciones 🌱"
        ),
        "permiso_si": (
        "✅ Gracias por compartirlo. Contar con un permiso ya es un buen comienzo.\n\n"
        "Podemos revisar si todo está conforme a la normativa vigente o si requiere alguna actualización.\n\n"
        "La asesoría inicial es gratuita. ¿Le interesa que le contemos cómo sería ese proceso y lo que incluiría? 😊"
        ),
        "aclaracion_permiso_si": (
        "🙏 Solo para confirmar, ¿desea que la evaluación gratuita de sus documentos y explicarle cómo fortalecer su cumplimiento?\n\n"
        "La visita no tiene costo, y es una forma rápida de evitar observaciones futuras 🚗"
        ),
        "permiso_no": (
        "🌱 No se preocupe, muchos de nuestros clientes inician desde cero.\n\n"
        "Podemos explicarle paso a paso lo que necesita y cómo empezar sin complicaciones ni multas.\n\n"
        "¿Desea una evaluación para darle esta orientación gratuita?"
        ),
        "aclaracion_permiso_no": (
        "🙏 Gracias por escribirnos. Si lo desea, podemos explicarle cómo se obtiene el permiso ambiental paso a paso, y cómo evitar sanciones o rechazos más adelante.\n\n¿Le gustaría que le contemos cómo funciona?"
        ),
        "cierre": (
        "Perfecto, solo necesitamos saber:\n"
        "📅 Día\n"
        "⏰ Hora\n"
        "📍 Lugar (oficina o sitio de trabajo)\n\n"
        "La evaluación es gratuita, sin compromiso y le brindará una guía clara para tomar decisiones 🌿"
        ),
        "aclaracion_cierre": (
        "🙏 ¿Nos puede indicar día, hora y lugar para programar su cita?\n\n"
        "Podemos agendar una visita tentativa si aún no tiene una fecha fija. Solo indíquenos cuándo le vendría mejor 🌱"
        ),
        "agradecimiento": (
        "🙌 Su cita ha sido registrada correctamente.\n\n"
        "El Ing. Darwin González Romero se comunicará con usted para confirmar todos los detalles.\n\n"
        "¡Gracias por confiar en nosotros! Estamos aquí para acompañarle de forma segura y profesional 🌿"
        )
    },
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
    "sí tengo", "ya tengo", "ya lo tengo", "ya lo hice", "ya está listo",
    "cuento con permiso", "cuento con el registro", "ya tengo el registro",
    "sí contamos", "sí, tengo", "tengo permiso", "tengo el permiso",
    "sí tengo los papeles", "sí tengo la licencia", "sí tengo el permiso",
    "sí cuento con eso", "sí cuento con el registro", "sí tengo eso al día",
    "mis papeles están en regla", "sí, ya está hecho", "ya tengo todo",
    "sí me lo aprobaron", "me lo dieron hace tiempo", "ya está aprobado",
    "ya está legalizado", "ya está aprobado por el ministerio",
    "sí, está vigente", "sí está al día", "sí, lo tengo actualizado",
    "sí, me lo entregaron", "sí está en orden", "sí tengo todo en orden",
    "tengo los documentos listos", "ya tengo todo en regla",
    "sí tengo todo en regla", "sí, todo está en orden", "ya está todo aprobado",
    "sí, ya está legalizado", "está al día", "ya está aprobado y firmado",
    "lo hice hace rato", "eso ya está hecho", "lo gestioné hace tiempo",
    "eso ya está listo", "ya lo tramité", "sí ya cumplí", "ya está completo",
    "sí tengo todo lo que piden", "todo está al día", "todo está aprobado",
    "ya lo tengo desde antes", "sí, ya cumplimos con eso", "ya fue aprobado",
    "sí, eso ya lo tengo", "sí, ya me lo entregaron", "todo está como debe ser",
    "sí tengo todo legal", "sí, todo está legalizado", "sí tengo todos los papeles"
]
import difflib

def contiene_permiso_si(texto, umbral=0.85):
    texto = texto.lower()
    for frase in PERMISOS_SI:
        frase = frase.lower()
        if frase in texto:
            return True
        similitud = difflib.SequenceMatcher(None, texto, frase).ratio()
        if similitud >= umbral:
            return True
    return False

PERMISOS_NO = [
    "no tengo", "no tengo todavía", "todavía no", "aún no", "no contamos", "ninguno", "no",
    "no tengo ninguno", "no cuento con", "aún no he sacado", "aún no saco eso",
    "todavía no lo tramito", "no está hecho", "no he tramitado", "no está hecho aún",
    "no he hecho nada", "no he hecho el trámite", "no tengo los papeles", "no tengo ese permiso",
    "no tengo el registro", "me falta sacar eso", "me falta eso", "no lo he gestionado",
    "no me han aprobado nada", "no me han dado nada", "nunca he hecho ese trámite",
    "no está legalizado", "no tengo nada aún", "no tengo todavía eso", "estoy por comenzar",
    "estoy en eso", "me falta comenzar", "recién voy a empezar", "recién voy a tramitar",
    "no he iniciado eso", "no tengo nada de eso", "no tengo nada listo", "no he hecho ese proceso",
    "no he movido nada aún", "todavía no lo hago", "no tengo permiso todavía",
    "todavía no tengo eso", "recién estoy averiguando", "recién estoy viendo",
    "no he sacado ese papel", "me falta hacer eso", "todavía no tramito nada",
    "no tengo lo del ministerio", "no tengo ningún documento", "no tengo esos papeles",
    "eso aún no lo tengo", "no tengo ese documento", "no tengo ni idea de eso",
    "no tengo ningún trámite hecho", "no tengo nada aprobado aún"
]

def contiene_permiso_no(texto, umbral=0.85):
    texto = texto.lower()
    for frase in PERMISOS_NO:
        frase = frase.lower()
        if frase in texto:
            return True
        similitud = difflib.SequenceMatcher(None, texto, frase).ratio()
        if similitud >= umbral:
            return True
    return False

def contiene_permiso_si(texto):
    texto = texto.lower()
    return any(exp in texto for exp in PERMISOS_SI)

def contiene_permiso_no(texto):
    texto = texto.lower()
    return any(exp in texto for exp in PERMISOS_NO)

def clasificar_permiso(texto):
    texto = texto.lower()

    if contiene_permiso_si(texto):
        return "si"
    elif contiene_permiso_no(texto):
        return "no"
    elif any(p in texto for p in ["permiso", "registro", "licencia", "documento", "papeles"]):
        return "mencion"
    else:
        return None

for actividad in FLUJOS_POR_ACTIVIDAD:
    FLUJOS_POR_ACTIVIDAD[actividad]["salida_amable"] = (
        "👌 Entiendo perfectamente. Si más adelante desea nuestra ayuda ambiental, estaremos disponibles por este medio. "
        "Gracias por habernos escrito 🌱"
    )
    FLUJOS_POR_ACTIVIDAD[actividad]["salida_ambigua"] = (
        "🙏 Entiendo que necesitas más tiempo para decidirlo. Cuando estés listo, puedes escribirnos y retomamos la conversación sin problema. ¡Gracias por tu interés en DALGORO! 🌿"
    )

if __name__ == "__main__":
    pruebas_si = ["sí tengo los papeles", "ya tengo todo en regla", "sí, ya está hecho"]
    pruebas_no = ["no tengo todavía", "aún no empiezo", "no me lo han aprobado"]

    for texto in pruebas_si:
        print(f"{texto} → contiene_permiso_si: {contiene_permiso_si(texto)}")

    for texto in pruebas_no:
        print(f"{texto} → contiene_permiso_no: {contiene_permiso_no(texto)}")
