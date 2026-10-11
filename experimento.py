"""Experimento: mide insertar / buscar / listar en Lista, ABB y B+.

Ejecutar:  python experimento.py
Salida:    resultados/mediciones.csv  (una fila por estructura, repetición, N y orden)
           resultados/entorno.txt     (hardware, software y parámetros usados)
Luego:     python graficas.py
"""
import csv
import gc
import os
import platform
import random
import sys
import time
from datetime import datetime

from abb import ABB
from arbol_bmas import ArbolBMas
from estudiante import Estudiante
from lista import Lista

# ----------------------------- Parámetros -----------------------------
TAMANOS = [1000, 2000, 4000, 8000, 16000, 32000]  # N: se duplica en cada paso
REPETICIONES = 10        # corridas independientes por cada (orden, N)
BUSQUEDAS = 2000         # M: mitad IDs que existen, mitad que NO existen
ORDEN_BMAS = 32          # máximo de hijos por nodo del B+
ORDENES = ["aleatorio", "ordenado"]
SEMILLA = 2026           # fija -> el experimento es reproducible
SALIDA = os.path.join("resultados", "mediciones.csv")


def crear_estructuras():
    return {"Lista": Lista(), "ABB": ABB(), "B+": ArbolBMas(ORDEN_BMAS)}


def generar_datos(n, orden, rng):
    """N estudiantes con IDs únicos en [1, 10N) y M IDs a buscar."""
    ids = rng.sample(range(1, 10 * n), n)
    if orden == "ordenado":
        ids.sort()
    estudiantes = [
        Estudiante(i, f"Estudiante{i}", rng.randint(16, 30), round(rng.uniform(0, 5), 2))
        for i in ids
    ]
    existentes = rng.choices(ids, k=BUSQUEDAS // 2)
    # IDs fuera del rango usado -> garantizado que no existen (peor caso de la lista)
    inexistentes = [rng.randrange(10 * n, 20 * n) for _ in range(BUSQUEDAS - BUSQUEDAS // 2)]
    consultas = existentes + inexistentes
    rng.shuffle(consultas)
    return estudiantes, consultas


def cronometrar(funcion):
    gc.collect()
    gc.disable()  # el recolector de basura no interrumpe la medición
    inicio = time.perf_counter()
    funcion()
    fin = time.perf_counter()
    gc.enable()
    return fin - inicio


def medir(estructura, estudiantes, consultas):
    def insertar_todos():
        for e in estudiantes:
            estructura.insertar(e)

    def buscar_todos():
        for i in consultas:
            estructura.buscar(i)

    t_insertar = cronometrar(insertar_todos)
    estructura.comparaciones = 0
    t_buscar = cronometrar(buscar_todos)
    t_listar = cronometrar(estructura.listar)  # se guarda en una lista, no se imprime
    return {
        "t_insertar_s": t_insertar,
        "t_buscar_s": t_buscar,
        "t_listar_s": t_listar,
        "comparaciones_por_busqueda": estructura.comparaciones / len(consultas),
        "altura": estructura.altura(),
    }


def guardar_entorno():
    with open(os.path.join("resultados", "entorno.txt"), "w", encoding="utf-8") as f:
        f.write(f"Fecha: {datetime.now():%Y-%m-%d %H:%M}\n")
        f.write(f"Python: {sys.version}\n")
        f.write(f"Sistema: {platform.platform()}\n")
        f.write(f"Procesador: {platform.processor()}\n")
        f.write(f"TAMANOS={TAMANOS} REPETICIONES={REPETICIONES} BUSQUEDAS={BUSQUEDAS} "
                f"ORDEN_BMAS={ORDEN_BMAS} SEMILLA={SEMILLA}\n")


def main():
    os.makedirs("resultados", exist_ok=True)
    guardar_entorno()

    # Calentamiento: una corrida pequeña que se descarta (carga de módulos, cachés)
    datos = generar_datos(1000, "aleatorio", random.Random(0))
    for estructura in crear_estructuras().values():
        medir(estructura, *datos)

    columnas = ["orden", "n", "m", "repeticion", "estructura", "t_insertar_s", "t_buscar_s",
                "t_listar_s", "comparaciones_por_busqueda", "altura"]
    with open(SALIDA, "w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=columnas)
        escritor.writeheader()
        for orden in ORDENES:
            for n in TAMANOS:
                inicio = time.perf_counter()
                for rep in range(1, REPETICIONES + 1):
                    rng = random.Random(f"{SEMILLA}-{orden}-{n}-{rep}")
                    estudiantes, consultas = generar_datos(n, orden, rng)
                    estructuras = crear_estructuras()
                    nombres = list(estructuras)
                    rng.shuffle(nombres)  # el orden de medición cambia en cada corrida
                    for nombre in nombres:
                        fila = medir(estructuras[nombre], estudiantes, consultas)
                        fila.update(orden=orden, n=n, m=BUSQUEDAS, repeticion=rep, estructura=nombre)
                        escritor.writerow(fila)
                    f.flush()
                print(f"{orden:>9}  N={n:>6}  {REPETICIONES} repeticiones en "
                      f"{time.perf_counter() - inicio:6.1f} s", flush=True)
    print("Listo ->", SALIDA)


if __name__ == "__main__":
    main()
