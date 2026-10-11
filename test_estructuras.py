"""Verificación de que las 3 estructuras son correctas. Ejecutar: python test_estructuras.py"""
import random

from abb import ABB
from arbol_bmas import ArbolBMas
from estudiante import Estudiante
from lista import Lista


def verificar(estructura, ids):
    for i in ids:
        estructura.insertar(Estudiante(i, f"E{i}", 20, 4.0))
    esperado = sorted(ids)
    assert [e.id for e in estructura.listar()] == esperado, "listar no está en orden"
    for i in ids:
        assert estructura.buscar(i).id == i, f"no encontró {i}"
    for i in (-1, 0, max(ids) + 1):
        assert estructura.buscar(i) is None, f"encontró {i}, que no existe"


if __name__ == "__main__":
    random.seed(1)
    for n in (1, 2, 10, 1000, 5000):
        ids = random.sample(range(1, n * 10), n)
        for orden in (ids, sorted(ids), sorted(ids, reverse=True)):
            for estructura in (Lista(), ABB(), ArbolBMas(3), ArbolBMas(4), ArbolBMas(32)):
                verificar(estructura, orden)

    # alturas esperadas
    abb = ABB()
    for i in range(1, 501):
        abb.insertar(Estudiante(i, "", 0, 0))
    assert abb.altura() == 500, "ABB con IDs ordenados debe degenerar (altura = n)"
    assert abb.insertar(Estudiante(7, "", 0, 0)) is False, "ABB aceptó un ID repetido"

    bmas = ArbolBMas(4)
    for i in range(1, 10001):
        bmas.insertar(Estudiante(i, "", 0, 0))
    assert bmas.altura() <= 14, "B+ debe quedar balanceado aun con IDs ordenados"
    assert bmas.insertar(Estudiante(7, "", 0, 0)) is False, "B+ aceptó un ID repetido"
    print("OK: Lista, ABB y B+ pasan todas las verificaciones")
