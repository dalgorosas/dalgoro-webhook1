import requests

# ✅ Reemplaza con tus valores reales de Green API
ID_INSTANCE = "7105252633"
API_TOKEN = "d2bde5d93868489e97bda6a22e40ddd9659b990c25c8422bb2"
API_URL = "https://api.green-api.com"

def formatear_chat_id(numero):
    return f"{numero}@c.us"

def enviar_mensaje(chat_id, texto):
    url = f"{API_URL}/waInstance{ID_INSTANCE}/sendMessage/{API_TOKEN}"
    payload = {
        "chatId": chat_id,
        "message": texto
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    return response.json()

# ✅ Datos de prueba
if __name__ == "__main__":
    numero_personal = formatear_chat_id("593984770663")  # Reemplaza si cambia tu número
    mensaje = (
        "📢 *Test de notificación de cita*\n"
        "Este es un mensaje automático de prueba desde DALGORO para confirmar que las alertas internas funcionan correctamente ✅"
    )
    try:
        respuesta = enviar_mensaje(numero_personal, mensaje)
        print("✅ Mensaje enviado con éxito:")
        print(respuesta)
    except Exception as e:
        print("❌ Error al enviar mensaje:", e)
