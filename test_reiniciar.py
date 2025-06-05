import sys
import os

# 🛠️ Asegura que Python encuentre todos los archivos del proyecto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gestor_conversacion import reiniciar_conversacion

# 👇 Escribe aquí el número de WhatsApp del cliente que quieres reiniciar
# IMPORTANTE: debe ser el chat_id completo como lo recibe Green API, por ejemplo: "593987654321@c.us"
chat_id = "593984770663@c.us"

# Ejecuta el reinicio
resultado = reiniciar_conversacion(chat_id)

# Muestra el resultado
print(resultado)
