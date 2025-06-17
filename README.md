# DALGORO Webhook

Servidor Flask para responder mensajes de WhatsApp mediante Green API y registrar contactos/mensajes en Google Sheets.

## Instalación y puesta en marcha

1. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```
2. **Configurar variables de entorno**
   - `GREENAPI_INSTANCE_ID` y `GREENAPI_API_TOKEN`: credenciales para la API de Green API.
   - `GOOGLE_CREDENTIALS_JSON`: ruta al archivo JSON de la cuenta de servicio de Google o el JSON en formato de cadena.

   En plataformas como **Render**, estas variables se definen en el apartado **Environment** de la configuración del servicio.
3. **Ejecutar la aplicación**
   - En desarrollo: `python app.py`
   - En producción: `gunicorn webhook:app`
   
   El repositorio incluye un `Procfile` con dicho comando. Render lo detecta automáticamente al desplegar la aplicación.

## Configurar credenciales de Google

1. Desde la consola de Google Cloud crea un proyecto y habilita las API de Google Sheets y Drive.
2. Crea una cuenta de servicio, descarga su archivo JSON y comparte tu hoja de cálculo con el correo de dicha cuenta.
3. Guarda el archivo en la raíz del proyecto con el nombre `dalgoro-api-ea1fa305d0ca.json` **o**
   define la variable `GOOGLE_CREDENTIALS_JSON` con la ruta al archivo o con el JSON completo.

## Scripts de prueba

- `test_alerta_manual.py`: envía manualmente una alerta al personal simulando datos ambiguos del cliente.
- `test_detectar_cita.py`: verifica la detección y registro automático de una cita a partir de un mensaje.
- `test_estado_hibrido.py`: elimina el estado local y procesa un mensaje para probar la recuperación desde Google Sheets.
- `test_gestor.py`: ejecuta varios escenarios de conversación para probar todo el flujo del gestor.
- `test_registro_cita.py`: registra una cita en Google Sheets utilizando datos ficticios.
- `test_reiniciar_completo.py`: limpia archivos locales y hojas de cálculo para reiniciar por completo el sistema.
- `test_sistema_integrado.py`: realiza una simulación integral con diferentes usuarios y mensajes.
