from google_sheets_utils import sheets_manager

telefono_prueba = "593984770663"  # Número en formato internacional sin espacios
mensaje_prueba = "Hola, DALGORO"

sheets_manager.update_contact(telefono_prueba)
sheets_manager.log_message(telefono_prueba, mensaje_prueba, "Recibido", "Test")
print("✔ Mensaje de prueba registrado en Google Sheets")
