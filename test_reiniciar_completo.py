import sys
import os
import json

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gestor_conversacion import reiniciar_conversacion
from mensaje_ids import guardar_ids

chat_id = "593984770663@c.us"

# Reinicia conversación
resultado = reiniciar_conversacion(chat_id)
print(f"🧹 Estado de conversación reiniciado: {resultado}")

# Elimina archivo de historial de mensajes
try:
    os.remove("mensajes_recientes.json")
    print("🗑️ Archivo mensajes_recientes.json eliminado.")
except FileNotFoundError:
    print("⚠️ No existía archivo mensajes_recientes.json.")

# Reinicia memoria reciente
guardar_ids(set())
print("♻️ memoria reciente de mensajes vaciada.")