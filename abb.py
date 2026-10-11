"""Estrategia 2: Árbol Binario de Búsqueda (ABB) sin balanceo.

- insertar / buscar: O(h), donde h = altura del árbol
    * IDs aleatorios -> h ~ O(log n)
    * IDs ordenados  -> h = n (el árbol degenera en una lista)
- listar: recorrido inorden -> O(n)

Todo es iterativo para no chocar con el límite de recursión de Python
cuando el árbol degenera (altura = n).
"""


class Nodo:
    __slots__ = ("estudiante", "izq", "der")

    def __init__(self, estudiante):
        self.estudiante = estudiante
        self.izq = None
        self.der = None


class ABB:
    def __init__(self):
        self.raiz = None
        self.comparaciones = 0

    def insertar(self, estudiante):
        nuevo = Nodo(estudiante)
        if self.raiz is None:
            self.raiz = nuevo
            return True
        actual = self.raiz
        clave = estudiante.id
        while True:
            if clave < actual.estudiante.id:
                if actual.izq is None:
                    actual.izq = nuevo
                    return True
                actual = actual.izq
            elif clave > actual.estudiante.id:
                if actual.der is None:
                    actual.der = nuevo
                    return True
                actual = actual.der
            else:
                return False  # ID repetido: no se inserta

    def buscar(self, id_buscado):
        actual = self.raiz
        visitados = 0
        while actual is not None:
            visitados += 1
            if id_buscado == actual.estudiante.id:
                self.comparaciones += visitados
                return actual.estudiante
            actual = actual.izq if id_buscado < actual.estudiante.id else actual.der
        self.comparaciones += visitados
        return None

    def listar(self):
        resultado, pila, actual = [], [], self.raiz
        while pila or actual is not None:
            while actual is not None:
                pila.append(actual)
                actual = actual.izq
            actual = pila.pop()
            resultado.append(actual.estudiante)
            actual = actual.der
        return resultado

    def altura(self):
        """Número de niveles (árbol vacío = 0, solo raíz = 1)."""
        if self.raiz is None:
            return 0
        h, nivel = 0, [self.raiz]
        while nivel:
            h += 1
            nivel = [hijo for n in nivel for hijo in (n.izq, n.der) if hijo is not None]
        return h
