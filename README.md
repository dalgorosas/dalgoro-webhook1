# DALGORO Webhook

Servidor Flask para responder mensajes de WhatsApp mediante Green API y registrar contactos/mensajes en Google Sheets.

## Instalación y puesta en marcha

1. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```
2. **Configurar variables de entorno**
   - `GREEN_API_TOKEN`: token de acceso para la API.
   - `GREENAPI_INSTANCE_ID` y `GREENAPI_API_TOKEN`: credenciales utilizadas por `bot.py` (opcional).
   - `GOOGLE_CREDENTIALS_JSON`: JSON con credenciales de servicio para Google Sheets.
3. **Ejecutar la aplicación**
   - En desarrollo: `python app.py`
   - En producción (ejemplo del `Procfile`): `gunicorn webhook:app`

## Scripts de prueba

- `test_alerta_manual.py`: envía manualmente una alerta al personal simulando datos ambiguos del cliente.
- `test_detectar_cita.py`: verifica la detección y registro automático de una cita a partir de un mensaje.
- `test_estado_hibrido.py`: elimina el estado local y procesa un mensaje para probar la recuperación desde Google Sheets.
- `test_gestor.py`: ejecuta varios escenarios de conversación para probar todo el flujo del gestor.
- `test_registro_cita.py`: registra una cita en Google Sheets utilizando datos ficticios.
- `test_reiniciar_completo.py`: limpia archivos locales y hojas de cálculo para reiniciar por completo el sistema.
- `test_sistema_integrado.py`: realiza una simulación integral con diferentes usuarios y mensajes.
