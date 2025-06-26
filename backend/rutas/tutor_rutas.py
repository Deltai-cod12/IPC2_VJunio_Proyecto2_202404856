from flask import Blueprint, request, jsonify
import io
import os
from servicios.carga_config import cursos, usuarios
from servicios.carga_horarios import procesar_xml_horarios
from servicios.carga_notas import parse_notas_xml, cargar_notas_en_matriz
from servicios.graficador_matriz import graficar_matriz 
from MatrizDispersa.MatrizDispersa import MatrizDispersa
import plotly.graph_objects as go

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


@tutor_bp.route('/listar_cursos', methods=['GET'])
def listar_cursos():
    id_tutor = request.args.get('id_tutor')

    if not id_tutor:
        return jsonify({"error": "Falta el id_tutor"}), 400

    # Buscar al tutor
    tutor = next((u for u in usuarios if u.id == id_tutor and u.tipo == "tutor"), None)

    if not tutor:
        return jsonify({"error": "Tutor no encontrado"}), 404

    cursos_asignados = []

    for codigo in tutor.cursos:
        curso = next((c for c in cursos if c.codigo == codigo), None)
        if curso:
            actividades = []
            if curso.matriz_notas:
                try:
                    actividades = curso.matriz_notas.obtener_actividades()
                except Exception as e:
                    print(f"[ERROR] Al obtener actividades del curso {curso.codigo}: {e}")

            cursos_asignados.append({
                "codigo": curso.codigo,
                "nombre": curso.nombre,
                "actividades": actividades
            })

    return jsonify(cursos_asignados), 200

@tutor_bp.route('/reporte/promedio', methods=['GET'])
def reporte_promedio_actividad():
    codigo_curso = request.args.get("codigo_curso")

    curso = next((c for c in cursos if c.codigo == codigo_curso), None)
    if not curso or not curso.matriz_notas:
        return jsonify({"error": "Curso no encontrado o sin notas"}), 404

    matriz = curso.matriz_notas
    actividades = []
    promedios = []

    actual_fila = matriz.filas.primero
    while actual_fila:
        actividad = actual_fila.id
        total = 0
        cantidad = 0

        actual_nota = actual_fila.acceso
        while actual_nota:
            total += float(actual_nota.valor)
            cantidad += 1
            actual_nota = actual_nota.siguiente

        if cantidad > 0:
            promedio = round(total / cantidad, 2)
            actividades.append(str(actividad))
            promedios.append(promedio)

        actual_fila = actual_fila.siguiente

    if not actividades:
        return jsonify({"error": "No hay actividades con notas"}), 400

    # Crear gráfica
    fig = go.Figure(go.Bar(
        x=promedios,
        y=actividades,
        orientation='h',
        marker=dict(color='skyblue')
    ))
    fig.update_layout(title='Promedio de Notas por Actividad', xaxis_title='Promedio', yaxis_title='Actividad')

    # Guardar imagen (crear carpeta si no existe)
    if not os.path.exists("static/reportes"):
        os.makedirs("static/reportes")

    ruta_imagen = f"static/reportes/promedio_{codigo_curso}.png"
    fig.write_image(ruta_imagen)

    return jsonify({
        "mensaje": "Gráfico generado exitosamente",
        "ruta": ruta_imagen
    }), 200
    
    

@tutor_bp.route('/reporte/top', methods=['GET'])
def reporte_top():
    import plotly.graph_objects as go
    import os

    codigo_curso = request.args.get("codigo_curso")
    nombre_actividad = request.args.get("actividad")

    if not codigo_curso or not nombre_actividad:
        return jsonify({"error": "Faltan datos"}), 400

    curso = next((c for c in cursos if c.codigo == codigo_curso), None)

    if not curso or not curso.matriz_notas:
        return jsonify({"error": "Curso no encontrado o sin matriz"}), 404

    nodo_fila = curso.matriz_notas.filas.getEncabezado(nombre_actividad)

    if not nodo_fila or not nodo_fila.acceso:
        return jsonify({"error": "Actividad no encontrada"}), 404

    notas = []
    actual = nodo_fila.acceso
    while actual:
        try:
            notas.append((actual.y, float(actual.valor)))
        except:
            pass
        actual = actual.siguiente

    notas.sort(key=lambda x: x[1], reverse=True)

    labels = [n[0] for n in notas]
    values = [n[1] for n in notas]

    fig = go.Figure(data=[
        go.Bar(x=labels, y=values, marker_color='indigo')
    ])

    fig.update_layout(
        title=f"TOP Notas - {nombre_actividad}",
        xaxis_title="Carnet",
        yaxis_title="Nota",
        height=400
    )

    # Ruta correcta dentro de backend/static/reportes
    nombre_archivo = f"reporte_top_{codigo_curso}_{nombre_actividad}.png".replace(" ", "_")
    ruta = os.path.join("static", "reportes", nombre_archivo)
    ruta_completa = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ruta))

    os.makedirs(os.path.dirname(ruta_completa), exist_ok=True)
    fig.write_image(ruta_completa)

    return jsonify({"ruta": ruta})
