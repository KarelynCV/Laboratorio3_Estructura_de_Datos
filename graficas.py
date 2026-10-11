"""Genera las gráficas y la tabla resumen a partir de resultados/mediciones.csv.

Ejecutar:  python graficas.py   (no necesita volver a correr el experimento)
Salida:    graficas/*.png, resultados/resumen.csv, resultados/resumen.md
"""
import csv
import math
import os
import statistics
from collections import defaultdict

import matplotlib.pyplot as plt

ENTRADA = os.path.join("resultados", "mediciones.csv")
ESTRUCTURAS = ["Lista", "ABB", "B+"]
ORDENES = ["aleatorio", "ordenado"]
SUBTITULO = {"aleatorio": "IDs insertados en orden aleatorio",
             "ordenado": "IDs insertados en orden creciente"}
COLORES = {"Lista": "#2a78d6", "ABB": "#eb6834", "B+": "#1baf7a"}
MARCADORES = {"Lista": "o", "ABB": "s", "B+": "^"}
TINTA, TINTA_SUAVE = "#0b0b0b", "#52514e"

plt.rcParams.update({
    "figure.dpi": 150, "savefig.bbox": "tight", "font.size": 10,
    "axes.edgecolor": "#b5b4ad", "axes.labelcolor": TINTA, "text.color": TINTA,
    "xtick.color": TINTA_SUAVE, "ytick.color": TINTA_SUAVE,
    "axes.grid": True, "grid.color": "#e4e3dd", "grid.linewidth": 0.8,
    "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
    "lines.linewidth": 2, "lines.markersize": 6,
})


def leer():
    """datos[(orden, estructura, n)][columna] = lista de valores (una por repetición)."""
    datos = defaultdict(lambda: defaultdict(list))
    with open(ENTRADA, encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            clave = (fila["orden"], fila["estructura"], int(fila["n"]))
            for col in ("t_insertar_s", "t_buscar_s", "t_listar_s",
                        "comparaciones_por_busqueda", "altura"):
                datos[clave][col].append(float(fila[col]))
            datos[clave]["m"] = int(fila["m"])
    return datos


DATOS = leer()
TAMANOS = sorted({n for (_, _, n) in DATOS})
M = next(iter(DATOS.values()))["m"]
TICKS_LINEALES = list(range(0, TAMANOS[-1] + 1, TAMANOS[-1] // 4))
REPS = len(next(iter(DATOS.values()))["t_buscar_s"])


def serie(orden, estructura, col, escala=1.0):
    medias = [statistics.mean(DATOS[(orden, estructura, n)][col]) * escala for n in TAMANOS]
    desv = [statistics.stdev(DATOS[(orden, estructura, n)][col]) * escala for n in TAMANOS]
    return medias, desv


def pendiente_loglog(orden, estructura, col):
    """Pendiente b de log(t) = a + b·log(N): ~1 lineal, ~2 cuadrática, ~0 logarítmica."""
    medias, _ = serie(orden, estructura, col)
    return statistics.linear_regression([math.log(n) for n in TAMANOS],
                                        [math.log(t) for t in medias]).slope


def nota(fig, texto):
    fig.text(0.01, -0.02, texto, ha="left", va="top", fontsize=8.5, color=TINTA_SUAVE, wrap=True)


def grafica_tiempo(col, archivo, titulo, unidad, escala, descripcion):
    fig, ejes = plt.subplots(1, 2, figsize=(11, 4.3), sharey=True)
    for ax, orden in zip(ejes, ORDENES):
        for e in ESTRUCTURAS:
            medias, desv = serie(orden, e, col, escala)
            ax.errorbar(TAMANOS, medias, yerr=desv, color=COLORES[e], marker=MARCADORES[e],
                        capsize=3, label=e)
        ax.set_title(SUBTITULO[orden])
        ax.set_xlabel("Número de estudiantes N")
        ax.set_xticks(TICKS_LINEALES, [f"{n // 1000}k" for n in TICKS_LINEALES])
    ejes[0].set_ylabel(f"Tiempo ({unidad})")
    ejes[0].legend(title="Estructura")
    fig.suptitle(titulo, fontweight="bold")
    nota(fig, descripcion + f" Cada punto = promedio de {REPS} repeticiones; "
              "barras = ± 1 desviación estándar.")
    fig.savefig(os.path.join("graficas", archivo))
    plt.close(fig)


def grafica_altura():
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for e in ("ABB", "B+"):
        for orden, estilo in (("aleatorio", "-"), ("ordenado", "--")):
            medias, _ = serie(orden, e, "altura")
            ax.plot(TAMANOS, medias, estilo, color=COLORES[e], marker=MARCADORES[e],
                    label=f"{e}, IDs {orden}s")
    ax.plot(TAMANOS, [math.log2(n) for n in TAMANOS], ":", color=TINTA_SUAVE,
            label="Referencia log₂(N)")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xticks(TAMANOS, [f"{n // 1000}k" for n in TAMANOS])
    ax.minorticks_off()
    ax.set_xlabel("Número de estudiantes N (escala log)")
    ax.set_ylabel("Altura (niveles, escala log)")
    ax.set_title("Altura del árbol vs N", fontweight="bold")
    ax.legend()
    nota(fig, "Altura = número de niveles del árbol. ABB con IDs ordenados: altura = N "
              "(degenera en lista).\nB+ (orden 32) queda balanceado en ambos casos.")
    fig.savefig(os.path.join("graficas", "4_altura.png"))
    plt.close(fig)


def grafica_comparaciones():
    fig, ejes = plt.subplots(1, 2, figsize=(11, 4.3), sharey=True)
    for ax, orden in zip(ejes, ORDENES):
        for e in ESTRUCTURAS:
            medias, _ = serie(orden, e, "comparaciones_por_busqueda")
            ax.plot(TAMANOS, medias, color=COLORES[e], marker=MARCADORES[e], label=e)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_title(SUBTITULO[orden])
        ax.set_xlabel("Número de estudiantes N (escala log)")
        ax.set_xticks(TAMANOS, [f"{n // 1000}k" for n in TAMANOS])
        ax.minorticks_off()
    ejes[0].set_ylabel("Comparaciones promedio por búsqueda\n(escala log)")
    ejes[0].legend(title="Estructura")
    fig.suptitle("Comparaciones de claves por búsqueda vs N", fontweight="bold")
    nota(fig, f"Promedio sobre las {M} búsquedas y las {REPS} repeticiones. "
              "No depende del computador: cuenta trabajo, no segundos.\n"
              "Con IDs crecientes la Lista y el ABB hacen exactamente las mismas comparaciones "
              "(la línea azul queda oculta bajo la naranja).")
    fig.savefig(os.path.join("graficas", "5_comparaciones.png"))
    plt.close(fig)


def grafica_boxplot():
    n_max = TAMANOS[-1]
    fig, ejes = plt.subplots(1, 3, figsize=(10, 4))
    for ax, e in zip(ejes, ESTRUCTURAS):
        valores = [t * 1000 for t in DATOS[("aleatorio", e, n_max)]["t_buscar_s"]]
        caja = ax.boxplot(valores, widths=0.5, patch_artist=True, showfliers=False,
                          medianprops={"color": TINTA, "linewidth": 2})
        caja["boxes"][0].set(facecolor=COLORES[e], alpha=0.35, edgecolor=COLORES[e])
        ax.scatter([1] * len(valores), valores, color=COLORES[e], s=14, zorder=3)
        ax.set_xticks([1], [e])
        ax.set_ylabel("Tiempo (ms)")
    fig.suptitle(f"Distribución del tiempo de {M} búsquedas (N = {n_max:_}, IDs aleatorios)".replace("_", "."),
                 fontweight="bold")
    nota(fig, f"Cada punto es una de las {REPS} repeticiones. Cada panel tiene su propia escala "
              "porque la lista es entre ~680 y ~970 veces más lenta.")
    plt.tight_layout()
    fig.savefig(os.path.join("graficas", "6_boxplot_busqueda.png"))
    plt.close(fig)


def grafica_loglog():
    fig, ejes = plt.subplots(1, 2, figsize=(11, 4.3), sharey=True)
    for ax, orden in zip(ejes, ORDENES):
        for e in ESTRUCTURAS:
            medias, _ = serie(orden, e, "t_buscar_s", 1000)
            b = pendiente_loglog(orden, e, "t_buscar_s")
            ax.plot(TAMANOS, medias, color=COLORES[e], marker=MARCADORES[e],
                    label=f"{e}  (pendiente = {b:.2f})".replace(".", ","))
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xticks(TAMANOS, [f"{n // 1000}k" for n in TAMANOS])
        ax.minorticks_off()
        ax.set_title(SUBTITULO[orden])
        ax.set_xlabel("Número de estudiantes N (escala log)")
        ax.legend()
    ejes[0].set_ylabel(f"Tiempo de {M} búsquedas (ms, escala log)")
    fig.suptitle("Búsqueda en escala log-log: la pendiente indica el orden de crecimiento",
                 fontweight="bold")
    nota(fig, "Pendiente ≈ 1 → O(N) (lineal);  pendiente ≈ 0,12 → O(log N) en este rango de N (casi plana).\n"
              "Pendiente = regresión lineal de log(tiempo) sobre log(N).")
    fig.savefig(os.path.join("graficas", "7_loglog_busqueda.png"))
    plt.close(fig)


def tabla_resumen():
    filas = []
    for orden in ORDENES:
        for e in ESTRUCTURAS:
            for n in TAMANOS:
                d = DATOS[(orden, e, n)]
                fila = {"orden": orden, "estructura": e, "n": n, "m": M, "repeticiones": REPS}
                for col in ("t_insertar_s", "t_buscar_s", "t_listar_s"):
                    media, desv = statistics.mean(d[col]), statistics.stdev(d[col])
                    fila[col + "_media"] = media
                    fila[col + "_desv"] = desv
                    fila[col + "_cv_%"] = 100 * desv / media
                    fila[col + "_mediana"] = statistics.median(d[col])
                fila["comparaciones_por_busqueda"] = statistics.mean(d["comparaciones_por_busqueda"])
                fila["altura"] = statistics.mean(d["altura"])
                fila["ns_por_comparacion"] = 1e9 * fila["t_buscar_s_media"] / (
                    M * fila["comparaciones_por_busqueda"])
                filas.append(fila)
    with open(os.path.join("resultados", "resumen.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(filas[0]))
        w.writeheader()
        w.writerows(filas)

    lineas = [f"# Resumen de resultados ({REPS} repeticiones por punto, M = {M} búsquedas)\n",
              "Tiempos en segundos: media ± desviación estándar (coeficiente de variación).\n"]
    for orden in ORDENES:
        lineas += [f"\n## IDs {orden}s\n",
                   "| Estructura | N | Insertar N (s) | Buscar M (s) | Listar (s) | Comparaciones/búsqueda | Altura | ns/comparación |",
                   "|---|---:|---|---|---|---:|---:|---:|"]
        for f_ in filas:
            if f_["orden"] != orden:
                continue
            celdas = [f"{f_[c + '_media']:.4g} ± {f_[c + '_desv']:.2g} ({f_[c + '_cv_%']:.0f}%)"
                      for c in ("t_insertar_s", "t_buscar_s", "t_listar_s")]
            lineas.append(f"| {f_['estructura']} | {f_['n']:,} | " + " | ".join(celdas) +
                          f" | {f_['comparaciones_por_busqueda']:.1f} | {f_['altura']:.0f} |"
                          f" {f_['ns_por_comparacion']:.0f} |")
    lineas += ["\n## Pendientes log-log (exponente empírico b en tiempo ∝ N^b)\n",
               "| Orden | Estructura | Insertar N | Buscar M | Listar |", "|---|---|---:|---:|---:|"]
    for orden in ORDENES:
        for e in ESTRUCTURAS:
            b = [pendiente_loglog(orden, e, c) for c in ("t_insertar_s", "t_buscar_s", "t_listar_s")]
            lineas.append(f"| {orden} | {e} | " + " | ".join(f"{x:.2f}" for x in b) + " |")
    with open(os.path.join("resultados", "resumen.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")


if __name__ == "__main__":
    os.makedirs("graficas", exist_ok=True)
    grafica_tiempo("t_buscar_s", "1_busqueda.png", f"Tiempo de {M} búsquedas vs N", "s", 1,
                   f"M = {M} búsquedas (50% IDs existentes, 50% inexistentes).\n"
                   "ABB y B+ balanceados tardan 1–3 ms y quedan pegados al eje (detalle en la gráfica 7).")
    grafica_tiempo("t_insertar_s", "2_insercion.png", "Tiempo de insertar los N estudiantes vs N",
                   "s", 1, "Tiempo total de construir la estructura desde vacía. Con IDs aleatorios las tres "
                         "tardan < 0,05 s (valores en resultados/resumen.md).")
    grafica_tiempo("t_listar_s", "3_listado.png", "Tiempo de listar en orden de ID vs N", "ms",
                   1000, "Lista: ordena una copia (sorted). ABB: recorrido inorden. "
                         "B+: recorre las hojas enlazadas.")
    grafica_altura()
    grafica_comparaciones()
    grafica_boxplot()
    grafica_loglog()
    tabla_resumen()
    print("Gráficas en graficas/ y resumen en resultados/resumen.md")
