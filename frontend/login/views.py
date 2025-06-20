from django.shortcuts import render, redirect
import requests

def login_view(request):
    mensaje_error = ""

    if request.method == "POST":
        usuario = request.POST.get("usuario")
        contrasenia = request.POST.get("contrasenia")

        # Enviar al backend Flask
        try:
            response = requests.post("http://localhost:5000/api/login", json={
                "usuario": usuario,
                "contrasenia": contrasenia
            })
            data = response.json()

            if response.status_code == 200:
                tipo = data.get("tipo")
                if tipo == "estudiante":
                    return redirect('/estudiante')
                elif tipo == "tutor":
                    return redirect('/tutor')
                elif tipo == "admin":
                    return redirect('/admin')
            else:
                mensaje_error = data.get("error", "Credenciales incorrectas.")
        except:
            mensaje_error = "No se pudo conectar al servidor."

    return render(request, 'login/login.html', {"mensaje_error": mensaje_error})
