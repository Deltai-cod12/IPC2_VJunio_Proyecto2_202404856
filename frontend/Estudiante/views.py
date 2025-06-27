import requests
from django.shortcuts import render
from django.http import HttpResponse

def ver_notas_estudiante(request):
    id_estudiante = request.session.get("id_usuario")  # 👈 usa esto, ya que así lo guardaste
    print(f"[DEBUG] ID estudiante desde sesión: {id_estudiante}")  # Verifica id estudiante

    if not id_estudiante:
        return HttpResponse("No has iniciado sesión como estudiante.", status=403)

    cursos = []
    notas = []
    promedio = None
    curso_seleccionado = request.GET.get("curso")
    print(f"[DEBUG] Curso seleccionado: {curso_seleccionado}")

    # Obtener cursos asignados al estudiante
    try:
        r = requests.get("http://127.0.0.1:5000/api/estudiante/cursos", params={"id_estudiante": id_estudiante})
        print(f"[DEBUG] Respuesta backend cursos: status {r.status_code}, content: {r.text}")
        if r.status_code == 200:
            cursos = r.json()
            print("[DEBUG] Cursos recibidos del backend Flask:", cursos)
    except Exception as e:
        print(f"[ERROR] Excepción al conectar al backend: {e}")
        return HttpResponse(f"Error conectando al backend: {e}", status=500)

    # Si el estudiante seleccionó un curso, obtener sus notas
    if curso_seleccionado:
        try:
            r = requests.get("http://127.0.0.1:5000/api/estudiante/notas", params={
                "id_estudiante": id_estudiante,
                "codigo_curso": curso_seleccionado
            })
            print(f"[DEBUG] Respuesta backend notas: status {r.status_code}, content: {r.text}")
            if r.status_code == 200:
                data = r.json()
                notas = data.get("notas", [])
                promedio = data.get("promedio", 0)
                print(f"[DEBUG] Notas recibidas: {notas}, Promedio: {promedio}")
        except Exception as e:
            print(f"[ERROR] Excepción al obtener notas: {e}")
            return HttpResponse(f"Error obteniendo notas: {e}", status=500)

    print("[DEBUG] Datos para renderizar:")
    print({
        "cursos": cursos,
        "notas": notas,
        "promedio": promedio,
        "curso_seleccionado": curso_seleccionado,
        "nombre_estudiante": request.session.get("nombre_usuario", id_estudiante)
    })

    return render(request, "estudiante/notas_estudiante.html", {
        "cursos": cursos,
        "notas": notas,
        "promedio": promedio,
        "curso_seleccionado": curso_seleccionado,
        "nombre_estudiante": request.session.get("nombre_usuario", id_estudiante)
    })
