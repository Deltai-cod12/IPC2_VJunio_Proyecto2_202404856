import os
from graphviz import Source

def graficar_matriz(matriz, nombre_salida="matriz_notas"):
    """
    Genera un archivo .dot y una imagen PNG a partir de una instancia de MatrizDispersa.
    Los archivos se guardan en la carpeta 'salidas/'.
    """
    # Crear carpeta si no existe
    carpeta_salida = os.path.join("salidas")
    os.makedirs(carpeta_salida, exist_ok=True)

    # Generar código DOT
    dot_code = matriz.generar_dot()

    # Rutas de archivo
    ruta_dot = os.path.join(carpeta_salida, f"{nombre_salida}.dot")
    ruta_png = os.path.join(carpeta_salida, f"{nombre_salida}.png")

    # Guardar el archivo .dot
    with open(ruta_dot, "w", encoding="utf-8") as f:
        f.write(dot_code)

    # Usar Graphviz para crear la imagen
    s = Source(dot_code, filename=f"{nombre_salida}.dot", format="png", directory=carpeta_salida)
    s.render(cleanup=True)

    print(f"[✔] Gráfico generado en: {ruta_png}")
    return ruta_png
