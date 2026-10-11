"""Estrategia 1: lista de Python NO ordenada.

- insertar: append al final            -> O(1)
- buscar:   recorrido secuencial       -> O(n)  (peor caso: ID inexistente)
- listar:   ordenar una copia por ID   -> O(n log n)

No verifica IDs duplicados al insertar (eso volvería la inserción O(n));
se asume que quien inserta garantiza IDs únicos.
"""


class Lista:
    def __init__(self):
        self.datos = []
        self.comparaciones = 0  # acumulado de comparaciones hechas por buscar()

    def insertar(self, estudiante):
        self.datos.append(estudiante)

    def buscar(self, id_buscado):
        for i, e in enumerate(self.datos):
            if e.id == id_buscado:
                self.comparaciones += i + 1
                return e
        self.comparaciones += len(self.datos)
        return None

    def listar(self):
        return sorted(self.datos, key=lambda e: e.id)

    def altura(self):
        return len(self.datos)  # una lista se recorre como un "camino" de n nodos
