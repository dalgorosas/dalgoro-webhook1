# scheduler.py — prueba controlada del módulo de seguimiento
from follow_up_manager import gestionar_seguimiento
from google_sheets_utils import obtener_contactos_activos

print("🔁 Ejecutando verificación de seguimiento...")

contactos = obtener_contactos_activos()
print(f"📋 Contactos activos encontrados: {len(contactos)}")

for contacto in contactos:
    chat_id = contacto["chat_id"]
    print(f"🟡 Verificando seguimiento para: {chat_id}")
    gestionar_seguimiento(chat_id)

print("✅ Seguimiento ejecutado con éxito.")
