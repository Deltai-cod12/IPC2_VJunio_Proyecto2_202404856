from flask import Blueprint, request, jsonify, abort
from servicios.carga_config import cursos

estudiante_bp = Blueprint('estudiante', __name__, url_prefix='/api/estudiante')

@estudiante_bp.route('/cursos', methods=['GET'])
def obtener_cursos_estudiante():
    carnet = request.args.get('id_estudiante')
    if not carnet:
        return abort(400, "Falta el parámetro 'id_estudiante'")

    cursos_asignados = []

    for curso in cursos:
        matriz = curso.matriz_notas
        if matriz is None:
            continue

        nodo_col = matriz.columnas.getEncabezado(carnet)
        if nodo_col and nodo_col.acceso:
            cursos_asignados.append({
                "codigo": curso.codigo,
                "nombre": curso.nombre
            })

    return jsonify(cursos_asignados)

@estudiante_bp.route('/notas', methods=['GET'])
def obtener_notas_estudiante():
    carnet = request.args.get('id_estudiante')
    codigo_curso = request.args.get('codigo_curso')

    if not carnet or not codigo_curso:
        return abort(400, "Faltan parámetros requeridos.")

    curso_encontrado = next((c for c in cursos if c.codigo == codigo_curso), None)
    if not curso_encontrado:
        return abort(404, "Curso no encontrado.")

    matriz = curso_encontrado.matriz_notas
    if matriz is None:
        return jsonify({"notas": [], "promedio": 0})

    nodo_col = matriz.columnas.getEncabezado(carnet)
    if not nodo_col or not nodo_col.acceso:
        return jsonify({"notas": [], "promedio": 0})

    actual = nodo_col.acceso
    notas = []
    suma = 0
    contador = 0

    while actual:
        notas.append({
            "actividad": actual.x,
            "nota": actual.valor
        })
        suma += actual.valor
        contador += 1
        actual = actual.abajo

    promedio = round(suma / contador, 2) if contador > 0 else 0

    return jsonify({
        "notas": notas,
        "promedio": promedio
    })
