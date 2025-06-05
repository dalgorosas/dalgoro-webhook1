import sys
import os

# Asegura que Python encuentre los módulos del proyecto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gestor_conversacion import reiniciar_conversacion

# 👉 Reemplaza con tu número de prueba en formato Green API
chat_id = "593984770663@c.us"

# Reinicia el estado de conversación
resultado = reiniciar_conversacion(chat_id)
print(f"🧹 Estado de conversación reiniciado: {resultado}")

# Elimina historial de mensajes procesados
try:
    os.remove("mensajes_recientes.json")
    print("🗑️ Historial de mensajes recientes eliminado.")
except FileNotFoundError:
    print("⚠️ No existía historial de mensajes.")
