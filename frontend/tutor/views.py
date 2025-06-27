import io
from django.shortcuts import render
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from PIL import Image
import requests
import os
from django.conf import settings

def cargar_horarios(request):
    contenido = ""
    horarios = []
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    nombre_tutor = request.session.get("nombre_tutor", "")
    id_tutor = request.session.get("id_tutor", "")

    if request.method == "POST":
        accion = request.POST.get("accion")

        if accion == "Limpiar":
            contenido = ""
            # Limpiar también horarios guardados en sesión
            if "horarios_tutor" in request.session:
                del request.session["horarios_tutor"]

        elif accion == "Procesar XML":
            # Leer contenido desde archivo si fue subido
            archivo = request.FILES.get("archivo")
            if archivo:
                contenido = archivo.read().decode("utf-8")
            else:
                contenido = request.POST.get("xml_content", "")

            if contenido.strip() != "":
                try:
                    files = {
                        'archivo': ('horarios.xml', contenido.encode('utf-8'), 'application/xml')
                    }
                    data = {
                        'id_tutor': id_tutor
                    }
                    print("[Django] Enviando XML a Flask con id_tutor:", id_tutor)
                    r = requests.post("http://127.0.0.1:5000/api/tutor/cargar_horarios", files=files, data=data)
                    print("[Django] Respuesta de Flask:", r.status_code, r.text)

                    if r.status_code == 200:
                        horarios = r.json()  # Suponemos que Flask retorna lista JSON de horarios
                        # Guardar horarios en sesión para mantener estado
                        request.session["horarios_tutor"] = horarios
                    else:
                        print(f"[Error] Flask respondió con código {r.status_code}: {r.text}")

                except Exception as e:
                    print("Error al conectar con Flask:", e)
            else:
                print("El contenido del XML está vacío, no se procesará.")

    # Si no es POST o no se procesó el XML, pero ya hay horarios en sesión, los usamos
    if not horarios and "horarios_tutor" in request.session:
        horarios = request.session.get("horarios_tutor", [])

    return render(request, 'tutor/cargar_horarios.html', {
        "contenido": contenido,
        "horarios": horarios,
        "dias": dias,
        "nombre_tutor": nombre_tutor
    })


import xml.etree.ElementTree as ET

def cargar_notas(request):
    contenido = ""
    mensaje = ""

    if "imagenes_notas" not in request.session:
        request.session["imagenes_notas"] = []

    if request.method == "POST":
        accion = request.POST.get("accion")

        if accion == "Limpiar Notas":
            contenido = ""
            mensaje = "Área de notas limpiada correctamente."
            request.session["imagenes_notas"] = []

        elif accion == "Procesar Notas":
            # 1. Si subieron archivo, leer contenido desde ahí
            archivo = request.FILES.get("archivo")
            if archivo:
                try:
                    contenido = archivo.read().decode("utf-8")
                except Exception as e:
                    mensaje = f"Error al leer el archivo: {str(e)}"
                    contenido = ""
            else:
                contenido = request.POST.get("xml_content", "")

            if not contenido.strip():
                mensaje = "No se proporcionó contenido XML."
            else:
                try:
                    files = {
                        'archivo': ('notas.xml', contenido.encode('utf-8'), 'application/xml')
                    }

                    data = {
                        'id_tutor': request.session.get('id_tutor', '')
                    }

                    print("[Django] Enviando notas a Flask...")
                    r = requests.post("http://127.0.0.1:5000/api/tutor/cargar_notas", files=files, data=data)

                    if r.status_code == 200:
                        mensaje = "Notas cargadas exitosamente."

                        # Extraer código y nombre del curso del XML
                        try:
                            import xml.etree.ElementTree as ET
                            root = ET.fromstring(contenido)
                            curso = root.find("curso")
                            codigo_curso = curso.attrib.get("codigo", "desconocido") if curso is not None else "desconocido"
                            nombre_curso = curso.attrib.get("nombre", "Curso Desconocido") if curso is not None else "Curso Desconocido"
                        except Exception as e:
                            print(f"[ERROR] No se pudo extraer información del curso: {e}")
                            codigo_curso = "desconocido"
                            nombre_curso = "Curso Desconocido"

                        nombre_archivo = f"matriz_notas_{codigo_curso}.png"
                        imagenes = request.session.get("imagenes_notas", [])

                        nueva = {
                            "curso": f"{codigo_curso} - {nombre_curso}",
                            "ruta": f"/static/img/{nombre_archivo}"
                        }
                        if nueva not in imagenes:
                            imagenes.append(nueva)
                            request.session["imagenes_notas"] = imagenes

                    else:
                        mensaje = f"Error al procesar: {r.status_code} - {r.text}"

                except Exception as e:
                    mensaje = f"Error al conectar con Flask: {str(e)}"

    return render(request, 'tutor/cargar_notas.html', {
        "contenido": contenido,
        "mensaje": mensaje,
        "imagenes_notas": request.session.get("imagenes_notas", [])
    })




def reportes(request):
    cursos = []
    actividades_por_curso = {}
    actividades = []
    imagen_promedio = None
    imagen_top = None
    curso_seleccionado = ""
    actividad_seleccionada = ""
    error = None

    id_tutor = request.session.get("id_tutor", "")

    try:
        r = requests.get("http://127.0.0.1:5000/api/tutor/listar_cursos", params={"id_tutor": id_tutor})
        if r.status_code == 200:
            data = r.json()
            for curso in data:
                cursos.append({
                    "codigo": curso["codigo"],
                    "nombre": curso["nombre"]
                })
                actividades_por_curso[curso["codigo"]] = curso["actividades"]
    except Exception as e:
        print("[ERROR] No se pudo conectar con Flask:", e)
        error = "No se pudo conectar con el servidor backend."

    if request.method == "POST":
        accion = request.POST.get("accion")
        curso_seleccionado = request.POST.get("curso")
        actividad_seleccionada = request.POST.get("actividad")

        # Cargar actividades del curso seleccionado (para renderizar)
        actividades = actividades_por_curso.get(curso_seleccionado, [])

        if accion == "Promedio por Actividad" and curso_seleccionado:
            try:
                r = requests.get("http://127.0.0.1:5000/api/tutor/reporte/promedio", params={"codigo_curso": curso_seleccionado})
                if r.status_code == 200:
                    imagen_promedio = r.json().get("ruta")
                else:
                    error = f"Error al obtener reporte promedio: {r.status_code}"
            except Exception as e:
                error = f"Error al obtener reporte promedio: {e}"

        elif accion == "Top de Notas" and curso_seleccionado and actividad_seleccionada:
            try:
                r = requests.get("http://127.0.0.1:5000/api/tutor/reporte/top", params={
                    "codigo_curso": curso_seleccionado,
                    "actividad": actividad_seleccionada
                })
                if r.status_code == 200:
                    imagen_top = r.json().get("ruta")
                else:
                    error = f"Error al obtener reporte top: {r.status_code}"
            except Exception as e:
                error = f"Error al obtener reporte top: {e}"

        elif accion == "Exportar PDF":
            # Definir qué imagen exportar (prioriza top si está seleccionado)
            imagen_a_exportar = None
            if actividad_seleccionada and curso_seleccionado:
                imagen_a_exportar = f"reporte_top_{curso_seleccionado}_{actividad_seleccionada}.png".replace(" ", "_")
            elif curso_seleccionado:
                imagen_a_exportar = f"promedio_{curso_seleccionado}.png"

            if not imagen_a_exportar:
                error = "No hay imagen seleccionada para exportar PDF."
            else:
                url_pdf = f"http://127.0.0.1:5000/api/tutor/reporte/exportar_pdf?imagen={imagen_a_exportar}"
                try:
                    r = requests.get(url_pdf)
                    if r.status_code == 200:
                        response = HttpResponse(r.content, content_type='application/pdf')
                        response['Content-Disposition'] = f'attachment; filename="{imagen_a_exportar}.pdf"'
                        return response
                    else:
                        error = f"Error al generar PDF: {r.status_code} - {r.text}"
                except Exception as e:
                    error = f"Error conectando con backend para exportar PDF: {e}"

    return render(request, "tutor/reportes.html", {
        "cursos": cursos,
        "actividades": actividades,
        "curso_seleccionado": curso_seleccionado,
        "actividad_seleccionada": actividad_seleccionada,
        "imagen_promedio": imagen_promedio,
        "imagen_top": imagen_top,
        "error": error
    })
    
from reportlab.lib.utils import ImageReader

def exportar_pdf(request):
    imagen_nombre = request.GET.get('imagen')
    if not imagen_nombre:
        return HttpResponse("No se proporcionó el nombre de la imagen.", status=400)

    try:
        # Ruta absoluta: static/reportes/imagen_nombre
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static', 'reportes'))
        ruta_imagen = os.path.join(base_dir, imagen_nombre)

        if not os.path.exists(ruta_imagen):
            return HttpResponse("Imagen no encontrada en el servidor.", status=404)

        # Abrir imagen con PIL
        imagen_pil = Image.open(ruta_imagen).convert("RGB")  # Asegura formato correcto

        # Redimensionar
        width_page, height_page = letter
        max_width = width_page - 100
        max_height = height_page - 100

        img_width, img_height = imagen_pil.size
        ratio = min(max_width / img_width, max_height / img_height, 1)
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)

        imagen_pil = imagen_pil.resize((new_width, new_height), Image.ANTIALIAS)

        # Convertir a ImageReader
        img_reader = ImageReader(imagen_pil)

        # Crear PDF
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)

        x = 50
        y = height_page - new_height - 50

        c.drawImage(img_reader, x, y, width=new_width, height=new_height)
        c.showPage()
        c.save()

        pdf = buffer.getvalue()
        buffer.close()

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{imagen_nombre}.pdf"'
        return response

    except Exception as e:
        return HttpResponse(f"Error al generar PDF: {e}", status=500)
