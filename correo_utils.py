import smtplib
from email.message import EmailMessage
from config_email import EMAIL_REMITENTE, EMAIL_CONTRASENA, EMAIL_DESTINATARIO, SMTP_SERVIDOR, SMTP_PUERTO

def enviar_correo_asunto(mensaje, asunto="🚨 Fallo en notificación por WhatsApp"):
    try:
        email = EmailMessage()
        email['From'] = EMAIL_REMITENTE
        email['To'] = EMAIL_DESTINATARIO
        email['Subject'] = asunto
        email.set_content(mensaje)

        with smtplib.SMTP(SMTP_SERVIDOR, SMTP_PUERTO) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_REMITENTE, EMAIL_CONTRASENA)
            smtp.send_message(email)

        print("✅ Correo enviado correctamente.")
    except Exception as e:
        print(f"❌ Error al enviar correo: {e}")
