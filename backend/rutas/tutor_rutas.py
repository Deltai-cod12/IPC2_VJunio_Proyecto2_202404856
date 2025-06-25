from flask import Blueprint, request, jsonify
import io
from servicios.carga_horarios import procesar_xml_horarios
from servicios.carga_notas import parse_notas_xml, cargar_notas_en_matriz
from servicios.graficador_matriz import graficar_matriz  # Asegúrate de importar esta función

tutor_bp = Blueprint('tutor_bp', __name__)

@tutor_bp.route('/cargar_horarios', methods=['POST'])
def cargar_horarios():
    if 'archivo' not in request.files or 'id_tutor' not in request.form:
        return jsonify({"error": "Datos incompletos"}), 400

    archivo = request.files['archivo']
    id_tutor = request.form['id_tutor']

    resultado = procesar_xml_horarios(archivo, id_tutor)
    return jsonify(resultado), 200


@tutor_bp.route('/cargar_notas', methods=['POST'])
def cargar_notas():
    if 'archivo' not in request.files:
        return "Archivo XML no proporcionado", 400

    archivo = request.files['archivo']

    try:
        # Leer el contenido del archivo XML
        contenido_xml = archivo.read().decode('utf-8')
        archivo_io = io.StringIO(contenido_xml)

        # Procesar notas
        resultado = parse_notas_xml(archivo_io)
        matriz = cargar_notas_en_matriz(resultado)

        # Generar gráfico .dot y .png
        graficar_matriz(matriz, nombre_salida=f"matriz_notas_{resultado['codigo_curso']}")

        return "Notas procesadas y graficadas correctamente", 200

    except Exception as e:
        return f"Error procesando notas: {str(e)}", 500
