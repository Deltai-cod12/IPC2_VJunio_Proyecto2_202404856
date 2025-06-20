from flask import Blueprint, request, jsonify
from servicios.carga_config import procesar_xml_configuracion

config_bp = Blueprint('config_bp', __name__)

@config_bp.route('/cargar_configuracion', methods=['POST'])
def cargar_configuracion():
    if 'archivo' not in request.files:
        return jsonify({"error": "Archivo XML no encontrado"}), 400

    archivo_xml = request.files['archivo']
    resultado = procesar_xml_configuracion(archivo_xml)
    return jsonify(resultado), 200
