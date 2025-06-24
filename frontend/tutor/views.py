from django.shortcuts import render
import requests

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

    

def cargar_notas(request):
    contenido = ""
    mensaje = ""

    if request.method == "POST":
        accion = request.POST.get("accion")

        if accion == "Limpiar Notas":
            contenido = ""
            mensaje = "Área de notas limpiada correctamente."

        elif accion == "Procesar Notas":
            contenido = request.POST.get("xml_content", "")
            if not contenido.strip():
                mensaje = "⚠️ No se proporcionó contenido XML."
            else:
                try:
                    # Enviar contenido XML a Flask
                    files = {
                        'archivo': ('notas.xml', contenido.encode('utf-8'), 'application/xml')
                    }

                    # Puedes enviar también el ID del tutor si lo necesitas en Flask
                    data = {
                        'id_tutor': request.session.get('id_tutor', '')
                    }

                    print("[Django] Enviando notas a Flask...")
                    r = requests.post("http://127.0.0.1:5000/api/tutor/cargar_notas", files=files, data=data)

                    if r.status_code == 200:
                        mensaje = "Notas cargadas exitosamente."
                    else:
                        mensaje = f"Error al procesar: {r.status_code} - {r.text}"

                except Exception as e:
                    mensaje = f"Error al conectar con Flask: {str(e)}"

    return render(request, 'tutor/cargar_notas.html', {
        "contenido": contenido,
        "mensaje": mensaje
    })
