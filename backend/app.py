from flask import Flask
from rutas.config_rutas import config_bp


app = Flask(__name__)

# Registro de Blueprints
app.register_blueprint(config_bp, url_prefix='/api/config')

@app.route('/')
def home():
    return {"mensaje": "IPC2-AcadNet Backend funcionando correctamente"}

if __name__ == '__main__':
    app.run(debug=True)
