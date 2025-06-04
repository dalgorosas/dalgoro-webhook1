
# test_detectar_cita.py

from interpretador_citas import procesar_y_registrar_cita

# Simulación de un mensaje del cliente con fecha y hora
chat_id = "593999000222"
mensaje_cliente = "Podría ser el próximo martes a las 10 de la mañana, si está bien para ustedes."

resultado = procesar_y_registrar_cita(chat_id, mensaje_cliente)

if resultado:
    print("✅ Cita detectada y registrada correctamente.")
else:
    print("⚠️ No se detectó una fecha y hora válida en el mensaje.")
