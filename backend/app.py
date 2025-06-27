from flask import Flask
from rutas.config_rutas import config_bp
from rutas.login_rutas import login_bp
from rutas.tutor_rutas import tutor_bp
from rutas.estudiante_rutas import estudiante_bp

app = Flask(__name__)

# Registro de Blueprints
app.register_blueprint(config_bp, url_prefix='/api/config')
app.register_blueprint(login_bp, url_prefix='/api/login')
app.register_blueprint(tutor_bp, url_prefix='/api/tutor')
app.register_blueprint(estudiante_bp, url_prefix='/api/estudiante')  

@app.route('/')
def home():
    return {"mensaje": "IPC2-AcadNet Backend funcionando correctamente"}

if __name__ == '__main__':
    app.run(debug=True)
