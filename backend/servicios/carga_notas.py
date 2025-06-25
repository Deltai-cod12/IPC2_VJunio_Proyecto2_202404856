import xml.etree.ElementTree as ET
from servicios.carga_config import usuarios, cursos
from MatrizDispersa.MatrizDispersa import MatrizDispersa  # Ruta correcta según tu estructura
from modelos.curso import Curso

def buscar_usuario_por_carnet(carnet):
    for usuario in usuarios:
        if usuario.id == carnet and usuario.tipo == "estudiante":
            print(f"[MATCH] Carnet encontrado: {carnet}")
            return usuario
    print(f"[NO MATCH] Carnet no encontrado: {carnet}")
    return None


def buscar_curso_por_codigo(codigo):
    for curso in cursos:
        if curso.codigo == codigo:
            return curso
    return None

def parse_notas_xml(ruta_archivo):
    import xml.etree.ElementTree as ET
    from servicios.carga_config import usuarios, cursos

    tree = ET.parse(ruta_archivo)
    root = tree.getroot()

    curso_nodo = root.find("curso")
    if curso_nodo is None:
        raise ValueError("No se encontró el nodo <curso> dentro de <notas>.")

    codigo_curso = curso_nodo.attrib.get("codigo", "Desconocido")
    nombre_curso = curso_nodo.attrib.get("nombre", "")

    curso_encontrado = None
    for curso in cursos:
        if curso.codigo == codigo_curso:
            curso_encontrado = curso
            break
    if not curso_encontrado:
        raise ValueError(f"Curso con código {codigo_curso} no encontrado.")

    notas_validas = []

    for actividad in curso_nodo.findall("actividad"):
        nombre_actividad = actividad.attrib.get("nombre")
        carnet = actividad.attrib.get("carnet")

        try:
            nota = int(actividad.text.strip())
        except (ValueError, AttributeError):
            continue

        if nota < 0 or nota > 100:
            continue

        usuario = next((u for u in usuarios if u.id == carnet and u.tipo == "estudiante"), None)
        if usuario is None:
            continue

        notas_validas.append((nombre_actividad, carnet, nota))

    print(f"[PARSE XML] Curso: {codigo_curso} - Notas válidas: {len(notas_validas)}")
    for act in notas_validas:
        print(f"   - Actividad: {act[0]}, Carnet: {act[1]}, Nota: {act[2]}")

    return {
        "codigo_curso": codigo_curso,
        "nombre_curso": nombre_curso,
        "curso_obj": curso_encontrado,
        "notas": notas_validas
    }


def cargar_notas_en_matriz(resultado):
    curso = resultado['curso_obj']
    matriz = MatrizDispersa(capa=0)

    print(f"\n[CARGA DE NOTAS] Curso: {resultado['codigo_curso']} - {resultado['nombre_curso']}")
    for actividad, carnet, nota in resultado['notas']:
        print(f"Ingresando: actividad={actividad}, carnet={carnet}, nota={nota}")
        matriz.insertar(nota, actividad, carnet)

    curso.matriz_notas = matriz 
    return matriz
