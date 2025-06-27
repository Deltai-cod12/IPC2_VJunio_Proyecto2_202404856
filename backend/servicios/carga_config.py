import xml.etree.ElementTree as ET
from modelos.usuario import Usuario
from modelos.curso import Curso

usuarios = []
cursos = []
asignaciones = {
    "tutores": [],
    "estudiantes": []
}

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
    global usuarios, cursos, asignaciones

    try:
        tree = ET.parse(archivo_xml)
        root = tree.getroot()

        # Reiniciar listas (evita duplicados en múltiples ejecuciones)
        usuarios.clear()
        cursos.clear()
        asignaciones["tutores"].clear()
        asignaciones["estudiantes"].clear()

        #  Cargar cursos 
        cursos_xml = root.find('cursos')
        if cursos_xml is not None:
            for curso in cursos_xml.findall('curso'):
                codigo = curso.get('codigo')
                nombre = curso.text.strip() if curso.text else ""
                if codigo and nombre and not any(c.codigo == codigo for c in cursos):
                    cursos.append(Curso(codigo, nombre))

        #  Cargar tutores 
        tutores_xml = root.find('tutores')
        if tutores_xml is not None:
            for tutor in tutores_xml.findall('tutor'):
                rp = tutor.get('registro_personal')
                contrasenia = tutor.get('contrasenia')
                nombre = tutor.text.strip() if tutor.text else ""
                if rp and contrasenia and nombre and not any(u.id == rp for u in usuarios):
                    usuarios.append(Usuario(rp, contrasenia, nombre, "tutor"))

        #  Cargar estudiantes 
        estudiantes_xml = root.find('estudiantes')
        if estudiantes_xml is not None:
            for estudiante in estudiantes_xml.findall('estudiante'):
                carnet = estudiante.get('carnet')
                contrasenia = estudiante.get('contrasenia')
                nombre = estudiante.text.strip() if estudiante.text else ""
                if carnet and contrasenia and nombre and not any(u.id == carnet for u in usuarios):
                    usuarios.append(Usuario(carnet, contrasenia, nombre, "estudiante"))

        #  Procesar asignaciones 
        asignaciones_xml = root.find('asignaciones')
        if asignaciones_xml is not None:
            # Asignaciones de tutores (elementos <tutor_curso>)
            c_tutores = asignaciones_xml.find('c_tutores')
            if c_tutores is not None:
                for tutor_curso in c_tutores.findall('tutor_curso'):
                    codigo = tutor_curso.get('codigo')
                    id_tutor = tutor_curso.text.strip() if tutor_curso.text else ""
                    if codigo and id_tutor:
                        if (codigo, id_tutor) not in asignaciones["tutores"]:
                            asignaciones["tutores"].append((codigo, id_tutor))
                        # Vincular curso al tutor
                        tutor = next((u for u in usuarios if u.id == id_tutor and u.tipo == "tutor"), None)
                        if tutor and codigo not in tutor.cursos:
                            tutor.cursos.append(codigo)

            # Asignaciones de estudiantes (elementos <estudiante_curso>)
            c_estudiantes = asignaciones_xml.find('c_estudiante')
            if c_estudiantes is not None:
                for estudiante_curso in c_estudiantes.findall('estudiante_curso'):
                    codigo = estudiante_curso.get('codigo')
                    id_estudiante = estudiante_curso.text.strip() if estudiante_curso.text else ""
                    if codigo and id_estudiante:
                        if (codigo, id_estudiante) not in asignaciones["estudiantes"]:
                            asignaciones["estudiantes"].append((codigo, id_estudiante))
                        # Vincular curso al estudiante
                        estudiante = next((u for u in usuarios if u.id == id_estudiante and u.tipo == "estudiante"), None)
                        if estudiante and codigo not in estudiante.cursos:
                            estudiante.cursos.append(codigo)

        #  Generar XML de resultado 
        return generar_xml_resultado()

    except ET.ParseError as e:
        return f"<?xml version='1.0'?><error>Error al parsear XML: {str(e)}</error>"
    except Exception as e:
        return f"<?xml version='1.0'?><error>Error inesperado: {str(e)}</error>"

def generar_xml_resultado():
    root = ET.Element("configuraciones_aplicadas")

    # Contar tutores y estudiantes
    total_tutores = sum(1 for u in usuarios if u.tipo == "tutor")
    total_estudiantes = sum(1 for u in usuarios if u.tipo == "estudiante")

    ET.SubElement(root, "tutores_cargados").text = str(total_tutores)
    ET.SubElement(root, "estudiantes_cargados").text = str(total_estudiantes)

    # Asignaciones (tutores y estudiantes)
    asignaciones_elem = ET.SubElement(root, "asignaciones")

    # Tutores
    tutores_elem = ET.SubElement(asignaciones_elem, "tutores")
    total_asignaciones_tutores = len(asignaciones["tutores"])
    correctas_tutores = sum(
        1 for codigo, id_tutor in asignaciones["tutores"]
        if any(u.id == id_tutor and u.tipo == "tutor" for u in usuarios)
        and any(c.codigo == codigo for c in cursos)
    )
    incorrectas_tutores = total_asignaciones_tutores - correctas_tutores

    ET.SubElement(tutores_elem, "total").text = str(total_asignaciones_tutores)
    ET.SubElement(tutores_elem, "correcto").text = str(correctas_tutores)
    ET.SubElement(tutores_elem, "incorrecto").text = str(incorrectas_tutores)

    # Estudiantes
    estudiantes_elem = ET.SubElement(asignaciones_elem, "estudiantes")
    total_asignaciones_estudiantes = len(asignaciones["estudiantes"])
    correctas_estudiantes = sum(
        1 for codigo, id_estudiante in asignaciones["estudiantes"]
        if any(u.id == id_estudiante and u.tipo == "estudiante" for u in usuarios)
        and any(c.codigo == codigo for c in cursos)
    )
    incorrectas_estudiantes = total_asignaciones_estudiantes - correctas_estudiantes

    ET.SubElement(estudiantes_elem, "total").text = str(total_asignaciones_estudiantes)
    ET.SubElement(estudiantes_elem, "correcto").text = str(correctas_estudiantes)
    ET.SubElement(estudiantes_elem, "incorrecto").text = str(incorrectas_estudiantes)

    # Convertir a string con declaración XML
    xml_str = ET.tostring(root, encoding='unicode')
    return f"<?xml version='1.0'?>\n{xml_str}"

def generar_xml_resultado():
    root = ET.Element("configuraciones_aplicadas")

    # Contar tutores y estudiantes
    total_tutores = sum(1 for u in usuarios if u.tipo == "tutor")
    total_estudiantes = sum(1 for u in usuarios if u.tipo == "estudiante")

    ET.SubElement(root, "tutores_cargados").text = str(total_tutores)
    ET.SubElement(root, "estudiantes_cargados").text = str(total_estudiantes)

    # Asignaciones (tutores y estudiantes)
    asignaciones_elem = ET.SubElement(root, "asignaciones")

    # Tutores
    tutores_elem = ET.SubElement(asignaciones_elem, "tutores")
    total_asignaciones_tutores = len(asignaciones["tutores"])
    correctas_tutores = sum(
        1 for codigo, id_tutor in asignaciones["tutores"]
        if any(u.id == id_tutor and u.tipo == "tutor" for u in usuarios)
        and any(c.codigo == codigo for c in cursos)
    )
    incorrectas_tutores = total_asignaciones_tutores - correctas_tutores

    ET.SubElement(tutores_elem, "total").text = str(total_asignaciones_tutores)
    ET.SubElement(tutores_elem, "correcto").text = str(correctas_tutores)
    ET.SubElement(tutores_elem, "incorrecto").text = str(incorrectas_tutores)

    # Estudiantes (similar a tutores)
    estudiantes_elem = ET.SubElement(asignaciones_elem, "estudiantes")
    total_asignaciones_estudiantes = len(asignaciones["estudiantes"])
    correctas_estudiantes = sum(
        1 for codigo, id_estudiante in asignaciones["estudiantes"]
        if any(u.id == id_estudiante and u.tipo == "estudiante" for u in usuarios)
        and any(c.codigo == codigo for c in cursos)
    )
    incorrectas_estudiantes = total_asignaciones_estudiantes - correctas_estudiantes

    ET.SubElement(estudiantes_elem, "total").text = str(total_asignaciones_estudiantes)
    ET.SubElement(estudiantes_elem, "correcto").text = str(correctas_estudiantes)
    ET.SubElement(estudiantes_elem, "incorrecto").text = str(incorrectas_estudiantes)

    # Convertir a string con declaración XML
    xml_str = ET.tostring(root, encoding='unicode')
    return f"<?xml version='1.0'?>\n{xml_str}"