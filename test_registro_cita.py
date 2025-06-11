from google_sheets_utils import registrar_cita_en_hoja
import datetime

# Simulación de datos reales
chat_id = "593984770663@c.us"
fecha = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
hora = "09:30"
modalidad = "Oficina"
ubicacion = "Machala"
observaciones = "Prueba manual desde script"

print("🧪 Iniciando prueba de registro de cita...")
registrar_cita_en_hoja(
    contacto=chat_id,
    fecha_cita=fecha,
    hora=hora,
    modalidad=modalidad,
    lugar=ubicacion,
    observaciones=observaciones
)
print("✅ Prueba finalizada.")
