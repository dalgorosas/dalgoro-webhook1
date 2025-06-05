import requests

# ✅ Cambia esta URL por la de tu servidor en Render
url = "https://dalgoro-webhook1.onrender.com/reiniciar"

# 👇 Define el chat_id del cliente a reiniciar
chat_id = "593984770663@c.us"

# 👇 Enviar POST
response = requests.post(url, json={"chat_id": chat_id})

# 📋 Mostrar respuesta
print("Código de respuesta:", response.status_code)
print("Respuesta del servidor:", response.json())
