from django.shortcuts import render, redirect
import xml.etree.ElementTree as ET
import requests

import requests
from django.shortcuts import render

def dashboard_admin(request):
    resultado = ""
    contenido = ""

    if request.method == "POST":
        accion = request.POST.get("accion")

        if accion == "cargar":
            archivo_subido = request.FILES.get("archivo")
            if archivo_subido:
                contenido = archivo_subido.read().decode("utf-8")
                resultado = " Archivo cargado en el área de texto."
            else:
                resultado = " No se seleccionó ningún archivo XML."

        elif accion == "procesar":
            contenido = request.POST.get("xml_content", "")
            if contenido.strip():
                try:
                    files = {
                        'archivo': ('entrada.xml', contenido.encode('utf-8'), 'application/xml')
                    }
                    r = requests.post("http://127.0.0.1:5000/api/config/cargar_configuracion", files=files)
                    resultado = r.text
                except Exception as e:
                    resultado = f" Error al conectar con Flask: {e}"
            else:
                resultado = " El área de texto está vacía."

        elif accion == "limpiar":
            contenido = ""
            resultado = ""

    return render(request, 'administrador/dashboard.html', {
        "contenido": contenido,
        "resultado": resultado
    })



    
def ver_usuarios(request):
    usuarios = []
    try:
        response = requests.get("http://127.0.0.1:5000/api/config/usuarios")
        if response.status_code == 200:
            usuarios = response.json()
    except Exception as e:
        print("Error al obtener usuarios desde Flask:", e)

    return render(request, 'administrador/ver_usuarios.html', {
        "usuarios": usuarios
    })

def informacion(request):
    return render(request, 'administrador/informacion.html')

def cerrar_sesion(request):
    return redirect('/')