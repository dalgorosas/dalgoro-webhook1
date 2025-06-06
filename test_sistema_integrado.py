import os
from datetime import datetime
from zoneinfo import ZoneInfo

# Importar componentes principales
from gestor_conversacion import manejar_conversacion, reiniciar_conversacion
from mensaje_ids import guardar_ids, cargar_ids

# Simulación de una base de datos en memoria para Sheets
contactos_sheet = []
mensajes_sheet = []
citas_sheet = []

# Datos simulados
chat_id = "593984770663@c.us"
actividad_simulada = "bananera"
ahora = datetime.now(ZoneInfo("America/Guayaquil"))

# Paso 1: Reinicio previo
print("\n--- Reiniciando sistema antes de la prueba ---")
print(reiniciar_conversacion(chat_id))
guardar_ids(set())  # Limpia mensajes recientes

# Paso 2: Simular primer mensaje (inicial)
print("\n--- Enviando mensaje inicial ---")
mensaje1 = "Hola, soy de una finca bananera."
respuesta1 = manejar_conversacion(chat_id, mensaje1, actividad_simulada, None)
print(f"🟢 Bot responde: {respuesta1}")
mensajes_sheet.append((chat_id, mensaje1, respuesta1, ahora))
contactos_sheet.append((chat_id, "nuevo contacto", actividad_simulada))

# Paso 3: Simular segundo mensaje (tengo permiso)
mensaje2 = "Sí, ya tengo permiso ambiental."
respuesta2 = manejar_conversacion(chat_id, mensaje2, actividad_simulada, ahora)
print(f"🟢 Bot responde: {respuesta2}")
mensajes_sheet.append((chat_id, mensaje2, respuesta2, ahora))

# Paso 4: Simular cita
mensaje3 = "Quiero agendar una cita para el lunes a las 14:00 en mi finca."
respuesta3 = manejar_conversacion(chat_id, mensaje3, actividad_simulada, ahora)
print(f"🟢 Bot responde: {respuesta3}")
mensajes_sheet.append((chat_id, mensaje3, respuesta3, ahora))
citas_sheet.append((chat_id, "Lunes", "14:00", "finca"))

# Paso 5: Validar que no se duplicó el mensaje inicial
print("\n--- Verificación de duplicidad ---")
respuesta_repetida = manejar_conversacion(chat_id, "Hola, otra vez", actividad_simulada, ahora)
if respuesta_repetida == respuesta1:
    print("❌ RESPUESTA_INICIAL fue enviada nuevamente. ⚠️ Error de duplicado.")
else:
    print("✅ RESPUESTA_INICIAL NO fue reenviada. Todo correcto.")

# Paso 6: Simular reinicio y nuevo mensaje
print("\n--- Reinicio completo ---")
print(reiniciar_conversacion(chat_id))
guardar_ids(set())

mensaje4 = "Buenas, soy de bananera otra vez."
respuesta4 = manejar_conversacion(chat_id, mensaje4, actividad_simulada, None)
print(f"🟢 Bot responde tras reinicio: {respuesta4}")
mensajes_sheet.append((chat_id, mensaje4, respuesta4, datetime.now(ZoneInfo("America/Guayaquil"))))

# Mostrar simulación final
print("\n--- Simulación de hojas de Sheets ---")
print("📋 Contactos:", contactos_sheet)
print("📋 Mensajes:", mensajes_sheet)
print("📋 Citas:", citas_sheet)
