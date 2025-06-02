from flask import Flask
from webhook import app as webhook_app  # Importa la instancia Flask desde webhook.py

# Usa la misma instancia de app definida en webhook.py
app = webhook_app

if __name__ == "__main__":
    app.run()
