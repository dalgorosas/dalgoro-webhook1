
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
        "permiso_si": "✅ Perfecto, eso ya es un buen paso. En estos casos, revisamos si la documentación está actualizada y sin observaciones que puedan generar problemas.\nPodemos hacer una visita gratuita a su finca o, si le resulta más cómodo, ir hasta su oficina para revisarlo todo con usted.\n¿Le gustaría que coordinemos esa visita? 📋",
        "aclaracion_permiso_si": "🙏 Gracias por el detalle. Entonces, ¿le interesaría que uno de nuestros técnicos le visite sin compromiso para revisar cómo están sus permisos?\nSolo necesitamos saber qué día y lugar le quedan mejor 😊",
        "permiso_no": "No se preocupe, todos empezamos por algún lado. Lo bueno es que en este momento usted ya está dando el paso correcto 💪\n\nPodemos acompañarle desde cero, explicándole paso a paso lo que necesita y cómo conseguir sus permisos sin complicaciones.\nLa asesoría es totalmente gratuita. ¿Prefiere que le visitemos en su finca o en su oficina? 📅",
        "aclaracion_permiso_no": "🙏 Gracias por escribirnos. Para ayudarle mejor, ¿le gustaría que agendemos una visita gratuita donde le explicamos todo lo que necesita para iniciar su proceso ambiental?\nSolo cuéntenos si le conviene más que le visitemos en su finca o en su oficina 😊",
        "cierre": "Perfecto, estamos listos para agendar su evaluación gratuita ✅\n\n¿Podría indicarnos el día, la hora y si prefiere que vayamos a su finca o a su oficina?\nEs un servicio sin costo y totalmente personalizado 🌱",
        "aclaracion_cierre": "🙏 Para poder agendar su visita, solo necesito que me indique:\n\n📅 Día\n⏰ Hora\n📍 Lugar (finca u oficina)\n\nRecuerde que es 100% gratuita y sin compromiso 🙌",
        "agradecimiento": "🙌 ¡Listo! Su cita ha quedado registrada con éxito.\n\nEl Ing. Darwin González Romero se comunicará con usted directamente al número 0984770663 para coordinar los detalles.\n\nMuchas gracias por confiar en nosotros. Estamos aquí para ayudarle a que su finca cumpla con todo y sin complicaciones 🌿"
    },

    "camaronera": {
        "introduccion": "🦐 ¡Qué excelente actividad! Justamente trabajamos codo a codo con camaroneros como usted para facilitarles todo el cumplimiento ambiental y evitar complicaciones con la autoridad.\n\nPara saber cómo podemos ayudarle mejor, ¿nos podría contar si ya cuenta con un permiso ambiental, como un registro o una licencia?\n\n👉 Sí, ya tengo\n👉 No tengo ninguno",
        "aclaracion_introduccion": "🙏 Muchas gracias por escribirnos. Solo para ubicar mejor su situación, ¿ya ha tramitado algún tipo de permiso ambiental (registro o licencia)?\nCon esa información sabremos cómo orientarle correctamente 😊",
        "permiso_si": "✅ ¡Perfecto! Si ya cuenta con un permiso, lo ideal es asegurarnos de que esté al día y sin observaciones pendientes, así se evita cualquier contratiempo a futuro.\n\nPodemos realizar una verificación totalmente gratuita. Podemos visitarle directamente en su camaronera o, si lo prefiere, ir hasta su oficina para mayor comodidad.\n\n¿Le gustaría que coordinemos esa evaluación? 📋",
        "aclaracion_permiso_si": "🙏 Entiendo. Entonces, ¿le interesaría que hagamos una revisión gratuita de sus permisos?\nSolo necesitamos acordar cuándo y dónde le resulta mejor 😊",
        "permiso_no": "No hay problema, ¡para eso estamos! 💪 Muchas camaroneras comienzan sin permiso, y nuestro trabajo es acompañarlas desde cero.\n\nPodemos explicarle todo el proceso, qué se necesita y cómo cumplir sin enredos.\nLo mejor: la asesoría es totalmente gratuita.\n\n¿Le gustaría que le visitemos en su camaronera o en su oficina para comenzar? 📅",
        "aclaracion_permiso_no": "🙏 Entiendo que está iniciando el proceso, y eso está muy bien.\nPodemos orientarle paso a paso para que regularice su actividad.\n¿Desea que agendemos una reunión gratuita para explicarle todo con claridad y sin compromiso? 😊",
        "cierre": "Excelente, estamos listos para agendar su visita personalizada 🌱\n\nSolo indíquenos qué día y hora le convienen, y si desea que vayamos a su camaronera o a su oficina.\n\nRecuerde que la asesoría es completamente gratuita y sin compromiso 🙌",
        "aclaracion_cierre": "🙏 Para coordinar su visita, solo necesitamos que nos confirme:\n📅 Día\n⏰ Hora\n📍 Lugar (camaronera u oficina)\n\n¡Es sin costo y le garantizamos una orientación clara y útil! 😊",
        "agradecimiento": "🙌 ¡Cita registrada con éxito!\n\nEl Ing. Darwin González Romero se pondrá en contacto con usted al número 0984770663 para confirmar los detalles de la visita.\n\nGracias por confiar en DALGORO. Estamos aquí para que su actividad camaronera cumpla con todo lo necesario, de forma segura y tranquila 🌊"
    },

    "mineria": {
        "introduccion": "⛏️ ¡Gracias por su mensaje! Trabajamos directamente con actividades mineras para ayudarles a cumplir con todos los requisitos ambientales que exige la autoridad.\n\n¿Nos puede indicar si ya cuenta con algún permiso como registro o licencia ambiental?\n\n👉 Ya tengo permiso\n👉 Aún no tengo",
        "aclaracion_introduccion": "🙏 Para poder orientarle mejor, ¿nos puede confirmar si ya cuenta con algún tipo de permiso ambiental (registro o licencia)?\nCon eso sabremos cómo ayudarle de forma más precisa 😊",
        "permiso_si": "✅ Excelente. Si ya tiene permiso, podemos verificar si todo está en regla, vigente y sin observaciones que puedan generar sanciones.\n\nPodemos hacer una evaluación técnica gratuita en su concesión minera o, si lo prefiere, en su oficina.\n\n¿Le gustaría que la agendemos? 📋",
        "aclaracion_permiso_si": "🙏 Gracias por su respuesta. ¿Le interesaría que revisemos juntos sus permisos actuales en una visita sin compromiso?\nEstamos listos para ayudarle cuando usted lo disponga 😊",
        "permiso_no": "Entiendo, muchos proyectos mineros comienzan sin conocer el proceso regulatorio, y eso es completamente normal.\n\nNosotros podemos acompañarle desde el inicio, explicándole cada paso y ayudándole a cumplir con la normativa sin enredos.\n\nPodemos visitarle en el sitio de la mina o en su oficina, como usted prefiera. ¿Desea que coordinemos la cita? ⛏️",
        "aclaracion_permiso_no": "🙏 Si desea iniciar su regularización ambiental, podemos visitarle sin compromiso para explicarle todo el proceso.\nLa asesoría es completamente gratuita. ¿Le gustaría que agendemos esa cita? 😊",
        "cierre": "Perfecto, estamos listos para agendar la evaluación técnica gratuita.\n\nSolo indíquenos el día, la hora y si desea que le visitemos en su mina o en su oficina.\n\nNo tiene ningún costo y es una excelente oportunidad para avanzar con respaldo técnico ✅",
        "aclaracion_cierre": "🙏 No logramos identificar su disponibilidad. ¿Podría confirmarnos el día, la hora y el lugar que le resulte más cómodo para la reunión?\nEstamos atentos para coordinarlo todo sin complicaciones 😊",
        "agradecimiento": "🙌 Su cita fue registrada con éxito.\n\nEl Ing. Darwin González Romero se comunicará con usted mediante el número 0984770663 para coordinar los detalles de la visita.\n\n¡Gracias por confiar en nosotros! Estamos para apoyar su actividad minera con total compromiso ⛏️"
    },

    "cacaotera": {
        "introduccion": "🍫 ¡Qué excelente actividad! Justamente trabajamos con productores cacaoteros como usted para facilitarles el cumplimiento de la normativa ambiental sin complicaciones.\n\n¿Nos puede confirmar si ya cuenta con permiso ambiental (registro o licencia)?\n\n👉 Ya tengo permiso\n👉 No tengo aún",
        "aclaracion_introduccion": "🙏 Gracias por su mensaje. ¿Podría confirmarnos si ya tiene algún tipo de permiso ambiental (registro o licencia)?\nAsí podremos brindarle una guía más adecuada a su situación 😊",
        "permiso_si": "✅ Perfecto. Contar con un permiso es un buen primer paso. Ahora lo importante es asegurarnos de que esté vigente y sin observaciones pendientes.\n\nPodemos hacer una visita técnica completamente gratuita, ya sea en su finca o en su oficina, para revisar los detalles.\n\n¿Le gustaría que la agendemos? 📋",
        "aclaracion_permiso_si": "🙏 Gracias por la información. ¿Le gustaría que revisemos sus documentos en una visita sin compromiso?\nNos podemos ajustar a la fecha y lugar que le resulten más cómodos 😊",
        "permiso_no": "No se preocupe, muchas personas inician sin saber los pasos exactos, y justo para eso estamos nosotros 🍃\n\nPodemos acompañarle desde cero, explicándole paso a paso lo que necesita y cómo cumplir con la normativa sin complicarse.\n\n¿Prefiere que nos acerquemos a su finca o a su oficina? La asesoría es gratuita 🍫",
        "aclaracion_permiso_no": "🙏 Si desea comenzar su proceso ambiental, podemos visitarle y explicarle todo desde el inicio.\nLa cita es sin costo y totalmente personalizada. ¿Le interesaría agendarla? 😊",
        "cierre": "Perfecto, estamos listos para coordinar su evaluación gratuita.\n\nSolo indíquenos el día, la hora y si desea que le visitemos en su finca o en su oficina.\n\nSerá una reunión sin compromiso, pensada para darle toda la información que necesita 🙌",
        "aclaracion_cierre": "🙏 Para agendar su cita, solo necesitamos saber lo siguiente:\n📅 Día\n⏰ Hora\n📍 Lugar (finca u oficina)\n\nLa asesoría es completamente gratuita y ajustada a su caso 🍃",
        "agradecimiento": "🙌 Su cita ha sido registrada con éxito.\n\nEl Ing. Darwin González Romero se comunicará con usted mediante el número 0984770663 para coordinar todos los detalles.\n\n¡Gracias por confiar en nosotros! Estamos aquí para apoyar su actividad cacaotera 🍫"
    },

    "ciclo_corto": {
        "introduccion": "🌽 ¡Qué buena noticia! Si trabaja con cultivos de ciclo corto como maíz, arroz o hortalizas, es importante saber si requiere permisos ambientales para evitar sanciones innecesarias.\n\n¿Ya cuenta con algún permiso ambiental vigente (registro o licencia)?\n\n👉 Sí, ya tengo\n👉 No tengo aún",
        "aclaracion_introduccion": "🙏 Para poder orientarle mejor, ¿nos puede indicar si ya cuenta con un registro o una licencia ambiental para su cultivo?\nCon eso le daremos una guía ajustada a su caso 😊",
        "permiso_si": "✅ Excelente. Tener el permiso es un buen comienzo, y es clave asegurarse de que esté actualizado y conforme con la normativa vigente.\n\nPodemos hacer una evaluación técnica totalmente gratuita. Podemos visitarle en su finca o en su oficina, según lo que le sea más cómodo.\n\n¿Le interesa que agendemos esa cita? 🌱",
        "aclaracion_permiso_si": "🙏 Perfecto. ¿Le gustaría que revisemos sus documentos en una visita sin compromiso?\nPodemos coordinar para ir a su finca o también a su oficina, como le convenga 🌽",
        "permiso_no": "No se preocupe, muchos productores inician sin saber que necesitan permisos. Nosotros estamos para guiarle paso a paso, desde cero y sin complicaciones.\n\nPodemos explicarle el proceso en una visita totalmente gratuita. ¿Le gustaría que le visitemos en su finca o en su oficina? 📋",
        "aclaracion_permiso_no": "🙏 Si desea comenzar con su proceso ambiental, podemos agendar una visita gratuita donde le explicamos todo desde el inicio.\nSolo díganos si prefiere finca u oficina 😊",
        "cierre": "Perfecto, solo necesitamos que nos indique:\n📅 Fecha\n⏰ Hora\n📍 Lugar (finca u oficina)\n\nLa evaluación es sin costo y le brindaremos una solución clara y completa 🌱",
        "aclaracion_cierre": "🙏 Para confirmar la cita, indíquenos por favor el día, la hora y el lugar donde prefiere que le visitemos.\nRecuerde que es una asesoría gratuita y personalizada 📋",
        "agradecimiento": "🙌 Su cita fue registrada con éxito.\n\nEl Ing. Darwin González Romero se comunicará con usted mediante el número 0984770663 para coordinar todos los detalles.\n\nGracias por confiar en nosotros. Estamos aquí para apoyar su cultivo de ciclo corto 🌾"
    },

    "granja_avicola": {
        "introduccion": "🐔 ¡Qué buena actividad! Justamente apoyamos a granjas avícolas como la suya para que cumplan con todos los requisitos ambientales y eviten sanciones innecesarias.\n\n¿Su granja ya cuenta con registro o licencia ambiental?\n\n👉 Sí, ya tiene\n👉 No tiene aún",
        "aclaracion_introduccion": "🙏 Para poder ayudarle mejor, ¿nos puede confirmar si su granja ya cuenta con algún tipo de permiso ambiental (registro o licencia)?\nCon eso podremos brindarle una orientación precisa 😊",
        "permiso_si": "✅ Perfecto. Contar con el permiso es un buen primer paso. Ahora es importante asegurarse de que esté vigente y sin observaciones que puedan generar problemas más adelante.\n\nPodemos visitarle para hacer una revisión técnica completamente gratuita.\n¿Le gustaría que agendemos esa evaluación? 🐥",
        "aclaracion_permiso_si": "🙏 Gracias por su respuesta. ¿Le interesaría que hagamos una evaluación gratuita para revisar sus permisos actuales?\nPodemos ajustarnos a su horario y reunirnos en su granja o en su oficina 🐔",
        "permiso_no": "Entiendo, muchas granjas avícolas aún no han iniciado el proceso, y es totalmente normal.\n\nNosotros podemos guiarle desde cero y explicarle todo lo que necesita para regularizar su actividad, paso a paso y sin complicaciones.\n\n¿Le gustaría que le visitemos en su granja o en su oficina para empezar? 📋",
        "aclaracion_permiso_no": "🙏 Si desea comenzar con su proceso de regularización ambiental, podemos visitarle para explicarle todo en una asesoría gratuita y sin compromiso.\n¿Le interesaría agendarla? 😊",
        "cierre": "Excelente, solo necesitamos que nos indique:\n📅 Día\n⏰ Hora\n📍 Lugar (granja u oficina)\n\nLa evaluación es sin costo, y le ayudará a tener claridad sobre su situación actual 🙌",
        "aclaracion_cierre": "🙏 Para confirmar la cita, por favor indíquenos cuándo y dónde le gustaría reunirse con nosotros.\nRecuerde que la asesoría es gratuita y personalizada 🐣",
        "agradecimiento": "🙌 Cita registrada correctamente.\n\nEl Ing. Darwin González Romero se comunicará con usted mediante el número 0984770663 para coordinar los detalles de la visita.\n\n¡Gracias por confiar en nosotros! Estamos para ayudarle a cumplir con todo lo ambiental 🐥"
    },

    "granja_porcina": {
        "introduccion": "🐷 ¡Excelente actividad! Justamente nos especializamos en apoyar a granjas porcinas como la suya para que cumplan con todos los requisitos ambientales exigidos por la autoridad.\n\n¿Su granja ya cuenta con un permiso ambiental (registro o licencia)?\n\n👉 Sí\n👉 No",
        "aclaracion_introduccion": "🙏 Gracias por escribirnos. ¿Nos podría confirmar si su granja porcina ya cuenta con algún permiso ambiental?\nCon esa información podremos orientarle de forma precisa 😊",
        "permiso_si": "✅ Muy bien. Tener el permiso es un paso importante. Lo que sigue es asegurarnos de que esté vigente, actualizado y sin observaciones pendientes.\n\nPodemos realizar una visita técnica gratuita para revisarlo todo con usted, sin compromiso.\n¿Le gustaría que la agendemos? 🐖",
        "aclaracion_permiso_si": "🙏 Entiendo. ¿Desea que revisemos sus permisos en una visita sin compromiso?\nPodemos acudir directamente a su granja o, si prefiere, a su oficina 🐷",
        "permiso_no": "No se preocupe, muchos productores comienzan sin conocer el proceso ambiental.\n\nNosotros podemos guiarle desde cero, explicándole paso a paso lo que necesita para regularizar su actividad.\n\nLa asesoría es completamente gratuita. ¿Prefiere que le visitemos en su granja o en su oficina? 📋",
        "aclaracion_permiso_no": "🙏 Con gusto podemos coordinar una visita técnica sin costo para explicarle cómo iniciar su regularización.\n¿Le interesaría que la agendemos? 😊",
        "cierre": "Perfecto, estamos listos para programar su evaluación gratuita.\n\nSolo necesitamos que nos indique:\n📅 Día\n⏰ Hora\n📍 Lugar (granja u oficina)\n\nSerá una reunión sin compromiso, pensada para darle total claridad sobre los pasos a seguir 🐖",
        "aclaracion_cierre": "🙏 Para confirmar su cita, por favor indíquenos cuándo y dónde desea que le visitemos.\nEstamos para ayudarle con gusto 😊",
        "agradecimiento": "🙌 Su cita fue registrada con éxito.\n\nEl Ing. Darwin González Romero se comunicará con usted mediante el número 0984770663 para coordinar todos los detalles.\n\nGracias por confiar en nosotros. Estamos aquí para apoyar su granja porcina con compromiso y experiencia 🐽"
    },

    "hotel": {
        "introduccion": "🏨 ¡Qué buena actividad! Tenemos amplia experiencia asesorando a hoteles para que cumplan con los requisitos ambientales sin contratiempos.\n\n¿Podría indicarnos si su hotel ya cuenta con un permiso ambiental (registro o licencia)?\n\n👉 Sí, ya tiene\n👉 No tiene aún",
        "aclaracion_introduccion": "🙏 Para poder orientarle mejor, ¿su hotel ya cuenta con algún tipo de permiso ambiental (registro o licencia)?\nCon eso sabremos cómo apoyarle de forma más precisa 😊",
        "permiso_si": "✅ Perfecto. Si ya cuenta con permisos, lo ideal es asegurarse de que estén actualizados, vigentes y sin observaciones que puedan generar sanciones.\n\nPodemos hacer una evaluación gratuita directamente en su hotel o, si lo prefiere, en su oficina.\n¿Le gustaría que la coordinemos? 🏨",
        "aclaracion_permiso_si": "🙏 Gracias por su respuesta. ¿Le gustaría que le visitemos para revisar sus documentos actuales?\nLa asesoría es sin costo y nos adaptamos a su disponibilidad 🗂️",
        "permiso_no": "No se preocupe, muchos negocios inician sin tener clara la normativa, y justamente nosotros estamos para guiarle desde el inicio.\n\nPodemos explicarle todo el proceso en una visita gratuita, ya sea en su hotel o en su oficina.\n¿Le interesaría que coordinemos esa reunión? 📅",
        "aclaracion_permiso_no": "🙏 Si desea iniciar su proceso ambiental, con gusto podemos hacer una evaluación técnica sin costo.\n¿Le gustaría que la programemos? 😊",
        "cierre": "Perfecto, solo necesitamos saber:\n📅 Día\n⏰ Hora\n📍 Lugar (hotel u oficina)\n\nLa asesoría no tiene costo ni compromiso, y le daremos una visión clara de lo que necesita 🙌",
        "aclaracion_cierre": "🙏 Para confirmar su cita, indíquenos cuándo y dónde desea que le visitemos.\nLa evaluación es gratuita y adaptada a su caso específico 🏨",
        "agradecimiento": "🙌 Su cita fue registrada con éxito.\n\nEl Ing. Darwin González Romero se comunicará con usted mediante el número 0984770663 para coordinar los detalles.\n\n¡Gracias por confiar en nosotros! Estamos aquí para respaldar su compromiso ambiental 🏨"
    },

    "industria": {
        "introduccion": "🏭 ¡Excelente actividad! Justamente apoyamos a empresas del sector industrial para que cumplan con todas sus obligaciones ambientales de forma segura y sin contratiempos.\n\n¿Actualmente su industria cuenta con un permiso ambiental (registro o licencia)?\n\n👉 Sí, ya tiene\n👉 No tiene aún",
        "aclaracion_introduccion": "🙏 Para poder asesorarle correctamente, ¿nos podría confirmar si su empresa ya cuenta con un permiso ambiental vigente?\nCon eso sabremos cómo ayudarle mejor 😊",
        "permiso_si": "✅ Excelente. Tener el permiso es el primer paso, y lo siguiente es asegurarnos de que esté al día y sin observaciones que puedan afectar su operación.\n\nPodemos visitarle directamente en su planta industrial o en su oficina para realizar una evaluación técnica sin costo.\n¿Le gustaría que la agendemos? 🏗️",
        "aclaracion_permiso_si": "🙏 Con gusto. ¿Desea que le visitemos para una revisión técnica de sus permisos actuales?\nLa evaluación es gratuita y sin compromiso 🏭",
        "permiso_no": "No hay problema, muchas industrias inician sin claridad sobre el proceso ambiental.\n\nNosotros podemos acompañarle desde cero, explicándole paso a paso cómo cumplir con la normativa vigente.\n\nPodemos visitarle en planta o en su oficina. ¿Le gustaría agendar una cita gratuita? 📋",
        "aclaracion_permiso_no": "🙏 Si desea comenzar su proceso de regularización ambiental, podemos guiarle paso a paso en una reunión sin compromiso.\n¿Le interesaría que la coordinemos? 😊",
        "cierre": "Perfecto, solo necesitamos que nos indique:\n📅 Día\n⏰ Hora\n📍 Lugar (planta u oficina)\n\nLa cita es completamente gratuita y pensada para brindarle claridad sobre su situación actual 🙌",
        "aclaracion_cierre": "🙏 ¿Cuándo y dónde le gustaría que le visitemos?\nLa asesoría es personalizada y no tiene ningún costo 🏗️",
        "agradecimiento": "🙌 Cita registrada exitosamente.\n\nEl Ing. Darwin González Romero se comunicará con usted mediante el número 0984770663 para coordinar todos los detalles.\n\n¡Gracias por confiar en DALGORO! Estamos aquí para respaldar su cumplimiento ambiental 🏭"
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
        "La asesoría inicial es gratuita. ¿Le gustaría que lo visitemos para revisar juntos su caso? 😊"
        ),
        "aclaracion_permiso_si": (
        "🙏 Solo para confirmar, ¿desea que le visitemos para validar sus permisos y explicarle cómo fortalecer su cumplimiento?\n\n"
        "La visita no tiene costo, y es una forma rápida de evitar observaciones futuras 🚗"
        ),
        "permiso_no": (
        "🌱 No se preocupe, muchos de nuestros clientes inician desde cero.\n\n"
        "Podemos explicarle paso a paso lo que necesita y cómo empezar sin complicaciones ni multas.\n\n"
        "¿Desea que le visitemos para darle esta orientación gratuita, o prefiere que le enviemos más información primero?"
        ),
        "aclaracion_permiso_no": (
        "🙏 Podemos agendarle una visita sin compromiso para explicar qué necesita según su actividad y ayudarle a empezar correctamente.\n\n"
        "¿Le gustaría agendarla ahora o desea pensarlo un poco más?"
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
        "El Ing. Darwin González Romero se comunicará con usted mediante el número 0984770663 para confirmar todos los detalles.\n\n"
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
    "sí tengo", "ya tengo", "cuento con permiso", "cuento con registro", "sí contamos", "sí, tengo", 
    "tengo permiso", "sí", "sí tengo los papeles", "sí tengo la licencia", "sí tengo el permiso",
    "sí cuento con eso", "sí cuento con el registro", "sí tengo eso al día", 
    "mis papeles están en regla", "sí, ya está hecho", "ya tengo todo", 
    "sí me lo aprobaron", "me lo dieron hace tiempo", "ya está aprobado", 
    "ya está legalizado", "sí, está vigente", "sí está al día", 
    "sí, lo tengo actualizado", "sí, me lo entregaron", "sí está en orden", 
    "tengo los documentos listos", "ya tengo todo en regla", 
    "sí tengo todo en regla", "sí, todo está en orden", "ya está todo aprobado", "sí, ya está legalizado"

]

PERMISOS_NO = [
    "no tengo", "no contamos", "aún no", "todavía no", "ninguno", "no", 
    "no tengo ninguno", "no cuento con", "aún no he sacado", "no me lo han dado", 
    "todavía no lo tramito", "no está hecho", "aún no empiezo", "no tengo los papeles", 
    "no he hecho el trámite", "no tengo ese permiso", "no tengo el registro", 
    "me falta sacar eso", "estoy en eso", "me falta eso", "no lo he gestionado", 
    "no me han aprobado nada", "nunca he hecho ese trámite", 
    "no me han dado nada", "no está legalizado", "no tengo nada aún",
    "no he tramitado", "no está hecho aún", "estoy por comenzar", "no tengo todavía"

]

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
