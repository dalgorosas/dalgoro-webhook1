class Config:
    GREEN_API_INSTANCE = "7105252633"
    GREEN_API_TOKEN = "67c2dece454947aba9d8d44daca573ccfa41c248c0424464a8"
    GREEN_API_BASE_URL = "https://api.green-api.com"

    DEFAULT_RESPONSES = {
        "hola": "¡Hola! ¿En qué podemos ayudarte?",
        "servicio": "Ofrecemos consultoría ambiental: licenciamiento, cumplimiento normativo, gestión de residuos y más. ¿Qué tipo de servicio buscas?",
        "servicios": "Ofrecemos consultoría ambiental: licenciamiento, cumplimiento normativo, gestión de residuos y más. ¿Qué tipo de servicio buscas?",
        "licencia": "Te ayudamos a obtener tu licencia ambiental sin complicaciones. ¿Tu finca, negocio o proyecto ya cuenta con estudios previos?",
        "consultoría": "Brindamos acompañamiento técnico, cumplimiento legal y soluciones ambientales. ¿Deseas asesoría mensual o por proyecto?",
        "precio": "Nuestros precios dependen del alcance del proyecto. ¿Podrías indicarnos brevemente qué necesitas para poder cotizarte?",
        "cotización": "Con gusto preparamos una cotización. ¿Qué tipo de actividad realizas y dónde estás ubicado?",
        "inicio": "Para comenzar solo necesitamos una breve descripción de tu actividad y tu ubicación. ¿Quieres que te orientemos paso a paso?",
        "comenzar": "Perfecto. ¿Puedes contarnos en qué consiste tu proyecto para indicarte cómo empezar?",
        "industria": "Trabajamos con bananeras, camaroneras, agroindustria, minería y más. ¿A qué sector perteneces?",
        "default": "Gracias por escribirnos. Por favor, indícanos el motivo de tu consulta y te ayudaremos lo antes posible."
    }

    MAX_MESSAGES_PER_MINUTE = 5
    MAX_RESPONSES_PER_HOUR = 30
