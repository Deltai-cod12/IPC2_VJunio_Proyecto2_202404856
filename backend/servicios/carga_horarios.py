import xml.etree.ElementTree as ET
import re
from servicios.carga_config import usuarios  # Lista global de usuarios

def procesar_xml_horarios(archivo_xml, id_tutor):
    horarios = []

    # Buscar al tutor
    tutor = next((u for u in usuarios if u.id == id_tutor and u.tipo == "tutor"), None)
    if not tutor:
        print(f"[ERROR] Tutor '{id_tutor}' no encontrado o no válido.")
        return {"error": f"Tutor '{id_tutor}' no encontrado o no es válido."}

    print(f"[INFO] Tutor encontrado: {tutor.id} - Cursos asignados: {getattr(tutor, 'cursos', [])}")

    try:
        tree = ET.parse(archivo_xml)
        root = tree.getroot()

        for curso in root.findall("curso"):
            codigo = curso.attrib.get("codigo", "").strip()
            print(f"[XML] Curso encontrado en XML: {codigo}")

            # Validar que el curso esté asignado al tutor
            if codigo not in tutor.cursos:
                print(f"[IGNORADO] Curso {codigo} no está asignado al tutor {tutor.id}")
                continue

            texto = curso.text or ""

            match_inicio = re.search(r'HorarioI:\s*(\d{2}:\d{2})', texto)
            match_fin = re.search(r'HorarioF:\s*(\d{2}:\d{2})', texto)

            if match_inicio and match_fin:
                horario = {
                    "codigo": codigo,
                    "horario_inicio": match_inicio.group(1),
                    "horario_fin": match_fin.group(1)
                }
                print(f"[OK] Horario válido extraído: {horario}")
                horarios.append(horario)
            else:
                print(f"[ADVERTENCIA] Horario no válido en curso {codigo}: '{texto}'")

    except Exception as e:
        print(f"[ERROR] Excepción al procesar el XML: {e}")
        return {"error": f"Error al procesar XML: {str(e)}"}

    # Guardar directamente en el atributo horarios del tutor
    tutor.horarios = horarios

    print(f"[FINAL] Horarios cargados para {tutor.id}: {horarios}")
    return horarios
