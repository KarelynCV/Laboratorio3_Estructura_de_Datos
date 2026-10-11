"""Estrategia 3: Árbol B+.

- Todos los estudiantes viven en las hojas; los nodos internos solo guardan
  claves que sirven de guía.
- Las hojas están enlazadas (hoja.siguiente), así listar en orden es recorrerlas.
- Siempre balanceado: todas las hojas están a la misma profundidad, sin importar
  el orden de inserción -> altura O(log n).

- insertar / buscar: O(log n)   (búsqueda binaria dentro de cada nodo)
- listar: O(n)

`orden` = número máximo de hijos de un nodo interno (máximo de claves = orden - 1).
"""


class Hoja:
    __slots__ = ("claves", "valores", "siguiente")

    def __init__(self):
        self.claves = []
        self.valores = []
        self.siguiente = None


class Interno:
    __slots__ = ("claves", "hijos")

    def __init__(self):
        self.claves = []
        self.hijos = []


class ArbolBMas:
    def __init__(self, orden=32):
        if orden < 3:
            raise ValueError("el orden de un B+ debe ser >= 3")
        self.orden = orden
        self.raiz = Hoja()
        self.comparaciones = 0

    # --- búsqueda binaria dentro de un nodo, contando comparaciones ---
    def _posicion(self, claves, clave):
        """Primer índice i tal que clave < claves[i] (como bisect_right)."""
        bajo, alto, comps = 0, len(claves), 0
        while bajo < alto:
            medio = (bajo + alto) // 2
            comps += 1
            if clave < claves[medio]:
                alto = medio
            else:
                bajo = medio + 1
        return bajo, comps

    def buscar(self, id_buscado):
        nodo, total = self.raiz, 0
        while isinstance(nodo, Interno):
            i, c = self._posicion(nodo.claves, id_buscado)
            total += c
            nodo = nodo.hijos[i]
        i, c = self._posicion(nodo.claves, id_buscado)
        total += c + 1  # +1: verificar igualdad en la hoja
        self.comparaciones += total
        if i > 0 and nodo.claves[i - 1] == id_buscado:
            return nodo.valores[i - 1]
        return None

    def insertar(self, estudiante):
        resultado = self._insertar(self.raiz, estudiante.id, estudiante)
        if resultado is None:
            return True
        if resultado is False:
            return False  # ID repetido
        # La raíz se dividió: el árbol crece un nivel hacia arriba
        separador, derecho = resultado
        nueva = Interno()
        nueva.claves = [separador]
        nueva.hijos = [self.raiz, derecho]
        self.raiz = nueva
        return True

    def _insertar(self, nodo, clave, valor):
        """Devuelve None (sin división), False (duplicado) o (separador, nodo_nuevo)."""
        i, _ = self._posicion(nodo.claves, clave)
        if isinstance(nodo, Hoja):
            if i > 0 and nodo.claves[i - 1] == clave:
                return False
            nodo.claves.insert(i, clave)
            nodo.valores.insert(i, valor)
            if len(nodo.claves) < self.orden:
                return None
            # dividir hoja: la mitad derecha pasa a una hoja nueva
            mitad = len(nodo.claves) // 2
            nueva = Hoja()
            nueva.claves, nodo.claves = nodo.claves[mitad:], nodo.claves[:mitad]
            nueva.valores, nodo.valores = nodo.valores[mitad:], nodo.valores[:mitad]
            nueva.siguiente, nodo.siguiente = nodo.siguiente, nueva
            return nueva.claves[0], nueva  # en B+ la clave se COPIA hacia arriba

        resultado = self._insertar(nodo.hijos[i], clave, valor)
        if not resultado:
            return resultado
        separador, derecho = resultado
        nodo.claves.insert(i, separador)
        nodo.hijos.insert(i + 1, derecho)
        if len(nodo.hijos) <= self.orden:
            return None
        # dividir nodo interno: la clave del medio SUBE (no se copia)
        mitad = len(nodo.claves) // 2
        sube = nodo.claves[mitad]
        nuevo = Interno()
        nuevo.claves, nodo.claves = nodo.claves[mitad + 1:], nodo.claves[:mitad]
        nuevo.hijos, nodo.hijos = nodo.hijos[mitad + 1:], nodo.hijos[:mitad + 1]
        return sube, nuevo

    def listar(self):
        nodo = self.raiz
        while isinstance(nodo, Interno):
            nodo = nodo.hijos[0]
        resultado = []
        while nodo is not None:
            resultado.extend(nodo.valores)
            nodo = nodo.siguiente
        return resultado

    def altura(self):
        """Número de niveles (solo una hoja = 1)."""
        h, nodo = 1, self.raiz
        while isinstance(nodo, Interno):
            h += 1
            nodo = nodo.hijos[0]
        return h
