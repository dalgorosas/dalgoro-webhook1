
from datetime import datetime
from gestor_conversacion import manejar_conversacion, reiniciar_conversacion
from estado_storage import obtener_estado
from google_sheets_utils import conectar_hoja

# Número simulado para pruebas
chat_id = "593999111222@c.us"

# 1. Reiniciar conversación
print("🔄 Reiniciando conversación...")
print(reiniciar_conversacion(chat_id))

# 2. Secuencia simulada de mensajes
mensajes = [
    "Hola buenos días",
    "Somos una bananera en Los Ríos",
    "Sí, ya tenemos permiso ambiental",
    "Queremos una evaluación gratuita",
    "Podría ser el lunes a las 10:00 en nuestra finca en Vinces"
]

fecha = datetime.now()

print("\n🚀 Simulación de conversación:")
for texto in mensajes:
    respuesta = manejar_conversacion(chat_id, texto, None, fecha)
    print(f"\n📩 Usuario: {texto}")
    print(f"🤖 Bot: {respuesta}")

# 3. Validación del estado en memoria y en Sheets
print("\n🔍 Validando estado final:")
estado = obtener_estado(chat_id)
for k, v in estado.items():
    print(f"{k}: {v}")

# 4. Validación en hoja de cálculo "Citas"
try:
    hoja = conectar_hoja("Citas")
    registros = hoja.get_all_records()
    print("\n📋 Últimas citas registradas:")
    for fila in registros[-5:]:  # Muestra solo las 5 últimas
        if fila["ID_Contacto"] == chat_id:
            print(fila)
except Exception as e:
    print(f"❌ Error accediendo a hoja Citas: {e}")
