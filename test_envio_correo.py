from correo_utils import enviar_correo_asunto

mensaje = (
    "📩 Este es un mensaje de prueba para confirmar que el sistema de respaldo por correo funciona correctamente.\n"
    "Si estás leyendo esto, el envío fue exitoso. ✅"
)
asunto = "✅ Prueba de envío de correo DALGORO"

enviar_correo_asunto(mensaje, asunto)
