import xml.etree.ElementTree as ET
from servicios.carga_config import usuarios, cursos
from MatrizDispersa.MatrizDispersa import MatrizDispersa  # Ruta correcta según tu estructura

def buscar_usuario_por_carnet(carnet):
    for usuario in usuarios:
        if usuario.id == carnet and usuario.tipo == "estudiante":
            return usuario
    return None

def buscar_curso_por_codigo(codigo):
    for curso in cursos:
        if curso.codigo == codigo:
            return curso
    return None

def parse_notas_xml(ruta_archivo):
    tree = ET.parse(ruta_archivo)
    root = tree.getroot()

    # Obtener el nodo <curso> dentro de <notas>
    curso_nodo = root.find("curso")
    if curso_nodo is None:
        raise ValueError("No se encontró el nodo <curso> dentro de <notas>.")

    codigo_curso = curso_nodo.attrib.get("codigo", "Desconocido")
    nombre_curso = curso_nodo.text.strip() if curso_nodo.text else ""

    curso_obj = buscar_curso_por_codigo(codigo_curso)
    if not curso_obj:
        raise ValueError(f"Curso con código {codigo_curso} no encontrado.")

    notas_validas = []

    for actividad in root.findall("actividad"):
        nombre_actividad = actividad.attrib.get("nombre")
        carnet = actividad.attrib.get("carnet")

        try:
            nota = int(actividad.text.strip())
        except (ValueError, AttributeError):
            continue

        if nota < 0 or nota > 100:
            continue

        usuario = buscar_usuario_por_carnet(carnet)
        if usuario is None:
            continue

        notas_validas.append((nombre_actividad, carnet, nota))

    return {
        "codigo_curso": codigo_curso,
        "nombre_curso": nombre_curso,
        "notas": notas_validas,
        "curso_obj": curso_obj
    }

def cargar_notas_en_matriz(resultado):
    """
    Carga las notas válidas en una matriz dispersa y la guarda dentro del objeto Curso.
    """
    curso = resultado['curso_obj']
    matriz = MatrizDispersa(capa=0)

    for actividad, carnet, nota in resultado['notas']:
        matriz.insertar(nota, actividad, carnet)

    curso.matriz_notas = matriz  # ← Aquí se asocia directamente al curso
    return matriz
