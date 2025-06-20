import xml.etree.ElementTree as ET
from modelos.usuario import Usuario
from modelos.curso import Curso

usuarios = []
cursos = []
asignaciones = {
    "tutores": [],
    "estudiantes": []
}

def procesar_xml_configuracion(archivo_xml):
    tree = ET.parse(archivo_xml)
    root = tree.getroot()

    # Cargar cursos
    for curso in root.find('cursos'):
        codigo = curso.get('codigo')
        nombre = curso.text.strip()
        cursos.append(Curso(codigo, nombre))

    # Cargar tutores
    for tutor in root.find('tutores'):
        rp = tutor.get('registro_personal')
        contrasenia = tutor.get('contrasenia')
        nombre = tutor.text.strip()
        usuarios.append(Usuario(rp, contrasenia, nombre, "tutor"))

    # Cargar estudiantes
    for estudiante in root.find('estudiantes'):
        carnet = estudiante.get('carnet')
        contrasenia = estudiante.get('contrasenia')
        nombre = estudiante.text.strip()
        usuarios.append(Usuario(carnet, contrasenia, nombre, "estudiante"))

    # Asignaciones
    c_tutores = root.find('./asignaciones/c_tutores')
    if c_tutores is not None:
        for asignacion in c_tutores:
            asignaciones["tutores"].append((asignacion.get('codigo'), asignacion.text.strip()))

    c_estudiantes = root.find('./asignaciones/c_estudiante')
    if c_estudiantes is not None:
        for asignacion in c_estudiantes:
            asignaciones["estudiantes"].append((asignacion.get('codigo'), asignacion.text.strip()))

    # Retorno resumido por ahora
    return {
        "mensaje": "Archivo procesado correctamente",
        "cursos_cargados": len(cursos),
        "usuarios_cargados": len(usuarios),
        "asignaciones_tutores": len(asignaciones["tutores"]),
        "asignaciones_estudiantes": len(asignaciones["estudiantes"])
    }
