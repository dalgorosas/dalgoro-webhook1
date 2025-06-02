import requests

# 🔑 Reemplaza estos valores con los datos de tu cuenta en Green API
INSTANCE_ID = "7105252633"
API_TOKEN = "67c2dece454947aba9d8d44daca573ccfa41c248c0424464a8"

def enviar_mensaje(numero, mensaje):
    url = f"https://api.green-api.com/waInstance{INSTANCE_ID}/sendMessage/{API_TOKEN}"
    datos = {
        "chatId": f"{numero}@c.us",  # Formato internacional: ejemplo 593984770663@c.us
        "message": mensaje
    }
    respuesta = requests.post(url, json=datos)
    print("Resultado:", respuesta.json())

# 🧪 PRUEBA: Enviar mensaje
if __name__ == "__main__":
    numero_destino = "593998829143"  # Reemplaza con tu número de WhatsApp de prueba
    texto = "Hola 👋, te saluda DALGORO SAS. ¿Te gustaría conocer nuestros servicios de regulación ambiental?"
    enviar_mensaje(numero_destino, texto)
