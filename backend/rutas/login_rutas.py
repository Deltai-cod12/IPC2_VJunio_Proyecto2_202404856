from flask import Blueprint, request, jsonify
from servicios.carga_config import usuarios

login_bp = Blueprint('login_bp', __name__)

@login_bp.route('/', methods=['POST'])
def login():
    datos = request.get_json()
    user = datos.get("usuario")
    contra = datos.get("contrasenia")

    # Usuario administrador fijo
    if user == "AdminIPC2" and contra == "AdminIPC2771":
        return jsonify({"tipo": "admin"}), 200

    # Recorre usuarios cargados desde XML
    for u in usuarios:
        if u.id == user and u.contrasenia == contra:
            return jsonify({"tipo": u.tipo}), 200

    return jsonify({"error": "Credenciales incorrectas"}), 401
