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
            return re.sub(r'\W', '_', str(s))

        dot = [
            'digraph G {',
            '    node [shape=box, style=filled, fontname="Helvetica"];',
            '    edge [fontname="Helvetica"];',
            '    rankdir=TB;',
            '    label="Matriz Dispersa de Notas";',
            '    fontsize=20;',
            '    compound=true;',
            '    nodesep=0.5;',
            '    ranksep=0.5;',
            '    newrank=true;',
            '',
            '    /* ESTILOS */',
            '    node [fillcolor="#e6f3ff"];',
            '',
            '    /* ENCABEZADOS DE COLUMNAS (CARNETS) */',
            '    subgraph cluster_header {',
            '        label="";',
            '        style=invis;',
            '        rank=same;',
            '        node [width=0.8, height=0.8, fillcolor="#cce0ff"];',
        ]

        # 1. ENCABEZADOS DE COLUMNAS
        carnets = []
        actual_col = self.columnas.primero
        while actual_col:
            carnet_id = f'col_{sanitize_id(actual_col.id)}'
            dot.append(f'        {carnet_id} [label="{actual_col.id}", group="col_{actual_col.id}"];')
            carnets.append(carnet_id)
            actual_col = actual_col.siguiente

        dot.extend([
            '    }',
            '',
            '    /* ESTRUCTURA PRINCIPAL */',
            '    node [fillcolor="#ffebcc"];',
        ])

        # 2. FILAS (TAREAS) Y NOTAS
        actual_fila = self.filas.primero
        while actual_fila:
            tarea_id = f'tarea_{sanitize_id(actual_fila.id)}'
            dot.append(f'    {tarea_id} [label="{actual_fila.id}", group="tareas"];')

            same_rank = [tarea_id]
            horizontal_chain = [tarea_id]

            actual_col = self.columnas.primero
            while actual_col:
                nota_encontrada = None
                actual_nota = actual_fila.acceso
                while actual_nota:
                    if actual_nota.y == actual_col.id:
                        nota_encontrada = actual_nota
                        break
                    actual_nota = actual_nota.siguiente

                if nota_encontrada:
                    nota_id = f'nota_{sanitize_id(nota_encontrada.x)}_{sanitize_id(nota_encontrada.y)}'
                    dot.append(f'    {nota_id} [label="{nota_encontrada.valor}", fillcolor="white", group="col_{actual_col.id}"];')
                    same_rank.append(nota_id)
                    horizontal_chain.append(nota_id)
                else:
                    empty_id = f'empty_{sanitize_id(actual_fila.id)}_{sanitize_id(actual_col.id)}'
                    dot.append(f'    {empty_id} [label="", width=0.6, height=0.6, style=invis, group="col_{actual_col.id}"];')
                    same_rank.append(empty_id)
                    horizontal_chain.append(empty_id)

                # Conexión horizontal continua
                if len(horizontal_chain) > 1:
                    dot.append(f'    {horizontal_chain[-2]} -> {horizontal_chain[-1]} [dir=both, color=gray];')

                actual_col = actual_col.siguiente

            dot.append(f'    {{rank=same; {" ".join(same_rank)}}};')

            # Conexión vertical invisible entre tareas
            if actual_fila.siguiente:
                next_tarea = f'tarea_{sanitize_id(actual_fila.siguiente.id)}'
                dot.append(f'    {tarea_id} -> {next_tarea} [style=invis, weight=10];')

            actual_fila = actual_fila.siguiente

        # 3. CONEXIONES VERTICALES ENTRE COLUMNAS
        actual_col = self.columnas.primero
        while actual_col:
            carnet_id = f'col_{sanitize_id(actual_col.id)}'
            vertical_chain = [carnet_id]

            actual_fila = self.filas.primero
            while actual_fila:
                nodo_id = None
                actual_nota = actual_fila.acceso
                while actual_nota:
                    if actual_nota.y == actual_col.id:
                        nodo_id = f'nota_{sanitize_id(actual_nota.x)}_{sanitize_id(actual_nota.y)}'
                        break
                    actual_nota = actual_nota.siguiente

                if nodo_id is None:
                    nodo_id = f'empty_{sanitize_id(actual_fila.id)}_{sanitize_id(actual_col.id)}'

                vertical_chain.append(nodo_id)

                actual_fila = actual_fila.siguiente

            for i in range(len(vertical_chain) - 1):
                dot.append(f'    {vertical_chain[i]} -> {vertical_chain[i + 1]} [dir=both, color=gray];')

            actual_col = actual_col.siguiente

        dot.append('}')
        return '\n'.join(dot)
