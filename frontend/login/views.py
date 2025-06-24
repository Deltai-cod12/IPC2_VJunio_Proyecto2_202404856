from django.shortcuts import render, redirect
import requests

def login_view(request):
    mensaje_error = ""

    if request.method == "POST":
        usuario = request.POST.get("usuario")
        contrasenia = request.POST.get("contrasenia")

        try:
            response = requests.post("http://127.0.0.1:5000/api/login", json={
                "usuario": usuario,
                "contrasenia": contrasenia
            })

            print("Respuesta de Flask:", response.status_code, response.text)

            data = response.json()

            if response.status_code == 200:
                tipo = data.get("tipo")
                if tipo == "admin":
                    return redirect('/pagina-admin')
                elif tipo == "tutor":
                    request.session['id_tutor'] = usuario       # ✅ ID del tutor
                    request.session['nombre_tutor'] = usuario   # ✅ Nombre para mostrar
                    return redirect('/pagina-tutor')
                elif tipo == "estudiante":
                    return redirect('/estudiante')
            else:
                mensaje_error = data.get("error", "Credenciales incorrectas.")
        except Exception as e:
            mensaje_error = f"No se pudo conectar al servidor Flask. Detalle: {e}"

    return render(request, 'login/login.html', {"mensaje_error": mensaje_error})
