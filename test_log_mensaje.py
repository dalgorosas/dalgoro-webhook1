from google_sheets_utils import registrar_mensaje

# Simular mensaje recibido del cliente
registrar_mensaje(
    "593999000111",  # chat_id
    "Hola, quiero información sobre licencias ambientales.",  # mensaje
    "Recibido",  # tipo
    "WhatsApp"   # canal
)

# Simular respuesta enviada del bot
registrar_mensaje(
    "593999000111",
    "¡Hola! Ofrecemos servicios de licenciamiento...",
    "Enviado",
    "Bot"
)

from google_sheets_utils import registrar_cita_en_hoja, actualizar_estado_cita

# Paso 1: Registrar una nueva cita
registrar_cita_en_hoja(
    contacto="593999000111",
    fecha_cita="2025-06-08",
    hora="10:00",
    modalidad="Finca",
    lugar="El Guabo - vía a Balao",
    observaciones="Cita agendada por el cliente vía bot"
)

# Paso 2: Confirmar la cita y añadir observaciones
actualizar_estado_cita(
    contacto="593999000111",
    nuevo_estado="Confirmada",
    observaciones_adicionales="Cliente confirmó que estará presente a esa hora en la finca"
)
