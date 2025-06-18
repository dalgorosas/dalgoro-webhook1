import smtplib
from email.mime.text import MIMEText
from config_email import EMAIL_REMITENTE, EMAIL_CONTRASENA, EMAIL_DESTINATARIO, SMTP_SERVIDOR, SMTP_PUERTO

def enviar_correo_fallo_whatsapp():
    asunto = "⚠️ FALLO EN ENVÍO DE WHATSAPP"
    cuerpo = "Se ha producido un error al intentar enviar un mensaje por WhatsApp. Por favor, revisa el sistema."

    mensaje = MIMEText(cuerpo, "plain")
    mensaje["Subject"] = asunto
    mensaje["From"] = EMAIL_REMITENTE
    mensaje["To"] = EMAIL_DESTINATARIO

    try:
        with smtplib.SMTP_SSL(SMTP_SERVIDOR, SMTP_PUERTO) as servidor:
            servidor.login(EMAIL_REMITENTE, EMAIL_CONTRASENA)
            servidor.send_message(mensaje)
        print("✅ Correo enviado correctamente.")
    except Exception as e:
        print("❌ Error al enviar el correo:", e)

if __name__ == "__main__":
    enviar_correo_fallo_whatsapp()
