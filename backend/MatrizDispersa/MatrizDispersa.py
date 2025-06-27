from .NodoInterno import NodoInterno
from .ListaEncabezado import ListaEncabezado
from .NodoCabecera import NodoCabecera
import re

class MatrizDispersa():
    def __init__(self, capa):
        self.capa = capa
        self.filas = ListaEncabezado('fila')
        self.columnas = ListaEncabezado('columna')

    def insertar(self, valor, fila, columna):
        print(f"[INSERTAR] Fila: {fila}, Columna: {columna}, Valor: {valor}")
        nuevo = NodoInterno(fila, columna, valor)

        nodoFila, nodoColumna = self.revisarCabeceras(fila, columna)

        if nodoFila.acceso is None:
            nodoFila.acceso = nuevo
        else:
            if nuevo.y < nodoFila.acceso.y:
                nuevo.siguiente = nodoFila.acceso
                nodoFila.acceso.anterior = nuevo
                nodoFila.acceso = nuevo
            else:
                actual = nodoFila.acceso
                while actual is not None:
                    if nuevo.y < actual.y:
                        nuevo.siguiente = actual
                        nuevo.anterior = actual.anterior
                        actual.anterior.siguiente = nuevo
                        actual.anterior = nuevo
                        break
                    elif nuevo.x == actual.x and nuevo.y == actual.y:
                        return
                    else:
                        if actual.siguiente is None:
                            actual.siguiente = nuevo
                            nuevo.anterior = actual
                            break
                        actual = actual.siguiente

        if nodoColumna.acceso is None:
            nodoColumna.acceso = nuevo
        else:
            if nuevo.x < nodoColumna.acceso.x:
                nuevo.abajo = nodoColumna.acceso
                nodoColumna.acceso.arriba = nuevo
                nodoColumna.acceso = nuevo
            else:
                actual = nodoColumna.acceso
                while actual is not None:
                    if nuevo.x < actual.x:
                        nuevo.abajo = actual
                        nuevo.arriba = actual.arriba
                        actual.arriba.abajo = nuevo
                        actual.arriba = nuevo
                        break
                    elif nuevo.x == actual.x and nuevo.y == actual.y:
                        return
                    else:
                        if actual.abajo is None:
                            actual.abajo = nuevo
                            nuevo.arriba = actual
                            break
                        actual = actual.abajo

    def revisarCabeceras(self, fila, columna):
        nodoFila = self.filas.getEncabezado(fila)
        nodoColumna = self.columnas.getEncabezado(columna)

        if nodoFila is None:
            nodoFila = NodoCabecera(fila)
            self.filas.insertarNodoCabecera(nodoFila)

        if nodoColumna is None:
            nodoColumna = NodoCabecera(columna)
            self.columnas.insertarNodoCabecera(nodoColumna)

        return nodoFila, nodoColumna

    def generar_dot(self):
        def sanitize_id(s):
            # Reemplazar todos los caracteres no alfanuméricos con _
            return re.sub(r'[^a-zA-Z0-9_]', '_', str(s))

        dot = 'digraph G {\n'
        dot += '    node [shape=box, style=filled, fontname="Helvetica"];\n'
        dot += '    edge [fontname="Helvetica"];\n'
        dot += '    rankdir=TB;\n'
        dot += '    label="Matriz Dispersa de Notas";\n'
        dot += '    fontsize=20;\n'
        dot += '    compound=true;\n'
        dot += '    nodesep=0.5;\n'
        dot += '    ranksep=0.5;\n'
        dot += '    newrank=true;\n\n'
        dot += '    /* ESTILOS */\n'
        dot += '    node [fillcolor="#e6f3ff"];\n\n'
        dot += '    /* ENCABEZADOS DE COLUMNAS */\n'
        dot += '    subgraph cluster_header {\n'
        dot += '        label="";\n'
        dot += '        style=invis;\n'
        dot += '        rank=same;\n'
        dot += '        node [width=0.8, height=0.8, fillcolor="#cce0ff"];\n'

        # Encabezados de columnas
        actual_col = self.columnas.primero
        while actual_col:
            col_id = sanitize_id(actual_col.id)
            dot += f'        col_{col_id} [label="{actual_col.id}", group="col_{col_id}"];\n'
            actual_col = actual_col.siguiente

        dot += '    }\n\n'
        dot += '    /* ESTRUCTURA PRINCIPAL */\n'
        dot += '    node [fillcolor="#ffebcc"];\n'

        # Filas y nodos internos
        actual_fila = self.filas.primero
        while actual_fila:
            fila_id = sanitize_id(actual_fila.id)
            dot += f'    tarea_{fila_id} [label="{actual_fila.id}", group="tareas"];\n'

            # Construir cadena same_rank
            same_rank = f'    {{rank=same; tarea_{fila_id}'
            prev_node = f'tarea_{fila_id}'

            actual_col = self.columnas.primero
            while actual_col:
                col_id = sanitize_id(actual_col.id)
                nota_encontrada = None
                actual_nota = actual_fila.acceso
                while actual_nota:
                    if actual_nota.y == actual_col.id:
                        nota_encontrada = actual_nota
                        break
                    actual_nota = actual_nota.siguiente

                if nota_encontrada:
                    nota_id = f'nota_{sanitize_id(nota_encontrada.x)}_{col_id}'
                    dot += f'    {nota_id} [label="{nota_encontrada.valor}", fillcolor="white", group="col_{col_id}"];\n'
                    same_rank += f' {nota_id}'
                    dot += f'    {prev_node} -> {nota_id} [dir=both, color=gray];\n'
                    prev_node = nota_id
                else:
                    empty_id = f'empty_{fila_id}_{col_id}'
                    dot += f'    {empty_id} [label="", width=0.6, height=0.6, style=invis, group="col_{col_id}"];\n'
                    same_rank += f' {empty_id}'
                    dot += f'    {prev_node} -> {empty_id} [dir=both, color=gray];\n'
                    prev_node = empty_id

                actual_col = actual_col.siguiente

            dot += same_rank + '};\n'

            # Conexión vertical entre filas
            if actual_fila.siguiente:
                next_fila_id = sanitize_id(actual_fila.siguiente.id)
                dot += f'    tarea_{fila_id} -> tarea_{next_fila_id} [style=invis, weight=10];\n'

            actual_fila = actual_fila.siguiente

        # Conexiones verticales entre columnas
        actual_col = self.columnas.primero
        while actual_col:
            col_id = sanitize_id(actual_col.id)
            prev_node = f'col_{col_id}'

            actual_fila = self.filas.primero
            while actual_fila:
                fila_id = sanitize_id(actual_fila.id)
                nodo_id = None
                actual_nota = actual_fila.acceso
                while actual_nota:
                    if actual_nota.y == actual_col.id:
                        nodo_id = f'nota_{sanitize_id(actual_nota.x)}_{col_id}'
                        break
                    actual_nota = actual_nota.siguiente

                if nodo_id is None:
                    nodo_id = f'empty_{fila_id}_{col_id}'

                dot += f'    {prev_node} -> {nodo_id} [dir=both, color=gray];\n'
                prev_node = nodo_id

                actual_fila = actual_fila.siguiente

            actual_col = actual_col.siguiente

        dot += '}\n'
        return dot
    
    def obtener_actividades(self):
        actividades = []
        actual = self.filas.primero
        while actual is not None:
            actividades.append(actual.id) 
            actual = actual.siguiente
        return actividades


    def obtener_carnets(self):
        carnets = []
        actual = self.columnas.primero
        while actual:
            carnets.append(actual.identificador)
            actual = actual.siguiente
        return carnets
