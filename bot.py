import requests
import os

# Usa variables de entorno si es posible
INSTANCE_ID = os.getenv("GREENAPI_INSTANCE_ID", "7105252633")
API_TOKEN = os.getenv("GREENAPI_API_TOKEN", "d2bde5d93868489e97bda6a22e40ddd9659b990c25c8422bb2")

def enviar_mensaje(numero, mensaje):
    url = f"https://api.green-api.com/waInstance{INSTANCE_ID}/sendMessage/{API_TOKEN}"
    datos = {
        "chatId": f"{numero}@c.us",
        "message": mensaje
    }

    try:
        respuesta = requests.post(url, json=datos)
        respuesta.raise_for_status()  # Lanza excepción si el código no es 2xx

        try:
            data = respuesta.json()
            print(f"✅ Mensaje enviado a {numero}: {data}")
            return data
        except ValueError:
            print(f"⚠️ Respuesta no era JSON. Código: {respuesta.status_code}")
            print(f"Texto recibido: {respuesta.text}")
            return None

    except requests.RequestException as e:
        print(f"❌ Error al enviar mensaje a {numero}: {e}")
        return None

# 🧪 PRUEBA: Enviar mensaje
if __name__ == "__main__":
    numero_destino = "593998829143"
    texto = "Hola 👋, te saluda DALGORO SAS. ¿Te gustaría conocer nuestros servicios de regulación ambiental?"
    enviar_mensaje(numero_destino, texto)
