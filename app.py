from flask import Flask
from webhook import webhook_blueprint

app = Flask(__name__)
app.register_blueprint(webhook_blueprint)

@app.route("/")
def index():
    return "¡DALGORO Webhook funcionando!"

if __name__ == "__main__":
    app.run()
