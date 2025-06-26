import os
from graphviz import Source

def graficar_matriz(matriz, nombre_salida="matriz_notas"):
    """
    Genera un archivo .dot y una imagen PNG a partir de una instancia de MatrizDispersa.
    Los archivos se guardan en '../frontend/static/img/' desde /backend/servicios/.
    """
    # Ruta absoluta del archivo actual (graficador_matriz.py)
    directorio_actual = os.path.dirname(os.path.abspath(__file__))

    # Subir dos niveles: /backend/servicios → / → luego entrar a frontend/static/img
    carpeta_salida = os.path.abspath(
        os.path.join(directorio_actual, '..', '..', 'frontend', 'static', 'img')
    )
    os.makedirs(carpeta_salida, exist_ok=True)

    ruta_dot = os.path.join(carpeta_salida, f"{nombre_salida}.dot")
    ruta_png = os.path.join(carpeta_salida, f"{nombre_salida}.png")

    # Generar código DOT desde la matriz
    dot_code = matriz.generar_dot()

    # Guardar .dot
    with open(ruta_dot, "w", encoding="utf-8") as f:
        f.write(dot_code)

    # Renderizar PNG usando Graphviz
    s = Source(dot_code, filename=nombre_salida, format="png", directory=carpeta_salida)
    s.render(cleanup=True)

    print(f"[✔] Gráfico generado en: {ruta_png}")
    return ruta_png
