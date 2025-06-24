from flask import Blueprint, request, jsonify
from servicios.carga_config import usuarios, procesar_xml_configuracion

config_bp = Blueprint('config_bp', __name__)

# Ruta para obtener usuarios (usada por Django)
@config_bp.route('/usuarios', methods=['GET'])
def obtener_usuarios():
    lista = []
    for u in usuarios:
        lista.append({
            "id": u.id,
            "usuario": u.nombre,
            "contrasenia": u.contrasenia,
            "tipo": u.tipo
        })
    return jsonify(lista), 200

# Ruta que procesa el XML desde Django
@config_bp.route('/cargar_configuracion', methods=['POST'])
def cargar_configuracion():
    if 'archivo' not in request.files:
        return jsonify({"error": "Archivo XML no encontrado"}), 400

    archivo_xml = request.files['archivo']
    resultado = procesar_xml_configuracion(archivo_xml)
    return jsonify(resultado), 200
