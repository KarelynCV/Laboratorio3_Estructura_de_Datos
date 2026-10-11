# Laboratorio 3: Sistema de búsqueda de estudiantes

| | |
|---|---|
| Estudiante | Karelyn Caicedo Velez |

Este laboratorio es un estudio experimental de cómo escalan tres estrategias de almacenamiento y 
búsqueda (**Lista**, **Árbol Binario de Búsqueda (ABB)** y **Árbol B+**) cuando crece el número de
estudiantes N, y de cómo el **orden de inserción** de los IDs (aleatorio o creciente) cambia el 
resultado. Realizado con código en lenguaje de programación python.

> Todos los números de este documento salen de `resultados/mediciones.csv` (datos crudos) y
> `resultados/resumen.md` (tabla resumen). Las gráficas están en `graficas/` y se pueden
> regenerar sin volver a correr el experimento.

---

## 1. Problema y objetivo

Cada estudiante tiene `id` (matrícula única), `nombre`, `edad` y `promedio`. El sistema debe:

1. **Buscar** un estudiante por ID.
2. **Insertar** un estudiante nuevo.
3. **Listar** todos los estudiantes en orden ascendente de ID.

**Objetivo:** medir el tiempo de ejecución de las tres operaciones en las tres estructuras para
varios tamaños N, y verificar si el crecimiento observado corresponde a la complejidad teórica.

## 2. Estructuras implementadas

| Archivo | Estructura | Insertar | Buscar | Listar en orden |
|---|---|---|---|---|
| [lista.py](lista.py) | Lista de Python **no ordenada** (`append`) | O(1) | O(N), recorrido secuencial | O(N log N), ordena una copia con `sorted` |
| [abb.py](abb.py) | ABB **sin balanceo** (iterativo) | O(h) | O(h) | O(N), recorrido inorden |
| [arbol_bmas.py](arbol_bmas.py) | Árbol B+ de orden 32, hojas enlazadas | O(log N) | O(log N) | O(N), recorrido de las hojas |

h = altura del ABB: **≈ log N con IDs aleatorios**, pero **h = N con IDs ordenados** (el árbol
degenera en una lista). El B+ siempre queda balanceado (todas las hojas a la misma profundidad).

Decisiones de diseño:

- **Lista no ordenada:** es la versión "ingenua" que se compara contra los árboles. No revisa
  IDs duplicados al insertar (eso haría la inserción O(N)); el ABB y el B+ sí rechazan duplicados.
- **ABB iterativo:** con IDs ordenados la altura llega a 32.000 niveles; una versión recursiva
  superaría el límite de recursión de Python.
- **B+ de orden 32:** máximo 32 hijos por nodo interno y 31 claves por hoja. Dentro de cada nodo
  se hace búsqueda binaria escrita a mano para poder contar comparaciones.
- Cada estructura cuenta las **comparaciones de claves** que hace `buscar()` y reporta su **altura**.

La corrección de las tres estructuras se verifica con [test_estructuras.py](test_estructuras.py)
(inserción en orden aleatorio, creciente y decreciente; búsquedas exitosas y fallidas; listado
ordenado; duplicados; alturas esperadas).

## 3. Metodología experimental

### 3.1 Parámetros

| Parámetro | Valor | Justificación |
|---|---|---|
| Tamaños N | 1.000, 2.000, 4.000, 8.000, 16.000, 32.000 | Se **duplica** N en cada paso: si el tiempo se duplica es O(N), si se multiplica por 4 es O(N²) y si casi no cambia es O(log N). |
| Repeticiones | 10 por cada (orden, N) | Permite calcular media y desviación estándar. |
| Búsquedas M | 2.000 por repetición | 1.000 IDs que existen y 1.000 que **no** existen (peor caso de la lista). |
| Orden de inserción | aleatorio y creciente | El orden creciente es el peor caso del ABB. |
| Orden del B+ | 32 | Valor típico para un B+ en memoria. |
| Semilla | 2026 | Hace que el experimento sea reproducible. |

**¿Por qué N llega solo hasta 32.000?** Se eligió el rango para que los casos lentos queden entre
**1 segundo y 5 minutos**: con N = 32.000 las 2.000 búsquedas en la lista tardan 1,7–2,0 s, en el
ABB degenerado 3,0 s, y construir el ABB con IDs ordenados tarda 25 s. Duplicar otra vez N
(64.000) llevaría la construcción del ABB ordenado a ≈ 110 s *por repetición* (crece como N²),
unos 18 minutos solo para ese punto. Los árboles balanceados se quedan en milisegundos en todo el
rango, y ese es justamente el resultado que se quiere mostrar.

**¿Por qué M = 2.000 búsquedas y no 100?** Con M = 100, buscar en la lista con N = 32.000 tardaría
solo ≈ 0,08–0,10 s, por debajo del objetivo de 1 s, y las 100 búsquedas en el ABB aleatorio
tardarían ≈ 0,09 ms, una medida tan corta que la dominaría el ruido del sistema operativo. Con
M = 2.000 la lista pasa de 1 s y los árboles quedan en milisegundos medibles. M se mantuvo fijo
porque cada búsqueda es independiente de las demás: el tiempo total crece proporcional a M
(M veces el costo de una búsqueda), así que cambiar M solo multiplica todas las curvas por la
misma constante y no cambia las pendientes ni la comparación entre estructuras.

### 3.2 Generación de datos y de búsquedas

- IDs únicos tomados al azar de [1, 10N) con `random.sample`. En el caso "ordenado" la misma
  muestra se ordena de forma creciente.
- Edad aleatoria entre 16 y 30, promedio aleatorio entre 0 y 5, nombre `"Estudiante<ID>"`.
- Búsquedas: 1.000 IDs elegidos entre los existentes y 1.000 IDs en [10N, 20N) (no existen), mezclados.
- **Las tres estructuras reciben exactamente los mismos estudiantes, en el mismo orden, y las
  mismas búsquedas** dentro de cada repetición. El orden en que se miden las tres estructuras se
  cambia al azar en cada repetición para que ninguna tenga siempre la ventaja (o desventaja) de ir primero.
- Cada repetición usa una semilla propia (`"2026-<orden>-<N>-<rep>"`), así que todo se puede reproducir.

### 3.3 Medición de los tiempos

- Reloj: `time.perf_counter()` (reloj de alta resolución, monotónico).
- Se mide **solo la operación**: la generación de datos queda fuera del cronómetro y el listado
  se guarda en una lista (no se imprime, porque imprimir dominaría el tiempo).
- Se cronometra el **bloque completo** (insertar los N, hacer las M búsquedas, un listado) y no
  cada operación por separado, para que la resolución del reloj no afecte las medidas cortas.
- El recolector de basura (`gc`) se desactiva durante cada medición y se ejecuta antes de ella.
- Una corrida de calentamiento (N = 1.000) se hace al inicio y se descarta.
- Además del tiempo se registran las **comparaciones por búsqueda** y la **altura**, que no
  dependen del computador.

### 3.4 Estadísticas y valores atípicos

- Por cada (orden, estructura, N): **media**, **desviación estándar muestral**, **mediana** y
  **coeficiente de variación** (CV = desviación / media) de las 10 repeticiones ([resultados/resumen.csv](resultados/resumen.csv)).
- **Pendiente log-log:** regresión lineal de log(tiempo medio) sobre log(N). Si tiempo ∝ N^b,
  entonces b ≈ 1 indica O(N) y b ≈ 2 indica O(N²). Para O(log N) la pendiente no es exactamente 0: en este rango (N de 1.000 a 32.000) se espera b ≈ 0,12, y para O(N log N), b ≈ 1,12.
- **Valores atípicos:** **no se eliminó ningún dato.** Con solo 10 repeticiones, quitar puntos
  cambiaría mucho la media. En su lugar se reporta la mediana junto a la media y se muestra la
  distribución completa en el boxplot (gráfica 6). Las medidas largas (> 0,1 s) tienen CV de 1–5 % en general (máximo 16 %);
  las de menos de 0,1 s tienen un CV típico de 4–26 % (mediana 8 %), y en tres listados de menos
  de 0,4 ms llega a 60–76 %, porque cualquier interrupción del sistema operativo pesa más en una
  medida corta.

- **Ejemplo de valor atípico:** en la búsqueda de la lista con N = 32.000 e IDs aleatorios, la
  repetición 10 tardó **2,44 s**, mientras que las otras nueve quedaron entre 1,52 y 1,63 s. Con ese
  punto la media es 1,67 ± 0,27 s (CV 16 %); sin él sería 1,58 ± 0,04 s, y la mediana (1,60 s)
  casi no cambia. Por eso la barra de error de ese punto es grande en la gráfica 1, y el punto
  aparece aislado arriba en el boxplot (gráfica 6). Se dejó en los datos porque no hay evidencia de un
  error del programa: en esa misma repetición el ABB (1,81 ms) y el B+ (2,64 ms) quedaron dentro o
  muy cerca del rango de las demás repeticiones, así que lo más probable es una interrupción del
  sistema operativo mientras se medía la lista. Tampoco cambia la conclusión:
  la pendiente log-log de la búsqueda en la lista es 1,07 con el punto y 1,06 sin él.

### 3.5 Hardware y software

| | |
|---|---|
| Procesador | Intel Core i7-1255U (12.ª gen.), 10 núcleos / 12 hilos, 1,7 GHz base |
| Memoria | 16 GB RAM |
| Sistema operativo | Windows 11 Home Single Language (10.0.26200) |
| Python | 3.13.3 (CPython, 64 bits), un solo hilo |
| Librerías | `matplotlib` 3.11.2 (solo para las gráficas); el experimento usa únicamente la biblioteca estándar |
| Fecha de ejecución | 2026-10-11 |
| Duración total | ≈ 7,6 minutos (5,1 de ellos en N = 32.000 con IDs ordenados) |
| Modo de energía | Windows en **"Máximo rendimiento"**, conectado a la corriente |

Es un portátil: se ejecutó conectado a la corriente, en modo "Máximo rendimiento", con OneDrive,
pgAdmin y las demás aplicaciones cerradas, y sin usar Colab ni notebooks. Se usó "Máximo rendimiento"
porque en un portátil los modos de ahorro de energía bajan la frecuencia del procesador y alteran
los tiempos.

## 4. Resultados

Tabla completa: [resultados/resumen.md](resultados/resumen.md). Valores para el N más grande
(N = 32.000, media ± desviación de 10 repeticiones):

| Orden | Estructura | Insertar N | Buscar M = 2.000 | Listar | Comparaciones / búsqueda | Altura |
|---|---|---|---|---|---:|---:|
| aleatorio | Lista | 0,0011 ± 0,0001 s | **1,67 ± 0,27 s** | 5,8 ± 0,4 ms | 23.975 | — |
| aleatorio | ABB | 0,031 ± 0,001 s | 1,7 ± 0,2 ms | 2,8 ± 0,8 ms | 15,7 | 35 |
| aleatorio | B+ | 0,048 ± 0,002 s | 2,4 ± 0,2 ms | 0,54 ± 0,09 ms | 15,4 | 4 |
| creciente | Lista | 0,0011 ± 0,0001 s | **2,04 ± 0,06 s** | 2,6 ± 0,6 ms | 24.082 | — |
| creciente | ABB | **25,3 ± 0,6 s** | **3,02 ± 0,04 s** | 2,1 ± 0,1 ms | 24.082 | **32.000** |
| creciente | B+ | 0,049 ± 0,003 s | 2,9 ± 0,1 ms | 0,42 ± 0,09 ms | 16,1 | 4 |

Pendientes log-log (exponente b en tiempo ∝ N^b):

| Orden | Estructura | Insertar N | Buscar M | Listar |
|---|---|---:|---:|---:|
| aleatorio | Lista | 0,92 | **1,07** | 1,08 |
| aleatorio | ABB | 1,18 | **0,16** | 1,03 |
| aleatorio | B+ | 1,12 | **0,10** | 0,96 |
| creciente | Lista | 0,89 | **1,11** | 1,11 |
| creciente | ABB | **2,09** | **1,11** | 0,94 |
| creciente | B+ | 1,11 | **0,11** | 0,85 |

### Gráficas

Cada punto es el promedio de 10 repeticiones y las barras son ± 1 desviación estándar.
Colores fijos en todas las gráficas: **Lista = azul (●)**, **ABB = naranja (■)**, **B+ = verde (▲)**.

| # | Gráfica | Qué muestra |
|---|---|---|
| 1 | [1_busqueda.png](graficas/1_busqueda.png) | Tiempo de 2.000 búsquedas vs N, aleatorio y creciente |
| 2 | [2_insercion.png](graficas/2_insercion.png) | Tiempo de construir la estructura con N estudiantes |
| 3 | [3_listado.png](graficas/3_listado.png) | Tiempo de listar en orden de ID |
| 4 | [4_altura.png](graficas/4_altura.png) | Altura del ABB y del B+ vs N, con log₂(N) como referencia |
| 5 | [5_comparaciones.png](graficas/5_comparaciones.png) | Comparaciones por búsqueda (no depende del computador) |
| 6 | [6_boxplot_busqueda.png](graficas/6_boxplot_busqueda.png) | Distribución de las 10 repeticiones para N = 32.000 |
| 7 | [7_loglog_busqueda.png](graficas/7_loglog_busqueda.png) | Búsqueda en escala log-log con la pendiente de cada curva |

![Búsqueda](graficas/1_busqueda.png)
![Inserción](graficas/2_insercion.png)
![Listado](graficas/3_listado.png)
![Altura](graficas/4_altura.png)
![Comparaciones](graficas/5_comparaciones.png)
![Boxplot](graficas/6_boxplot_busqueda.png)
![Log-log](graficas/7_loglog_busqueda.png)

## 5. Análisis

**¿Los resultados se comportan como predice la complejidad teórica?** Sí, en todos los casos:

- *Búsqueda en la lista:* pendiente 1,07 (aleatorio) y 1,11 (creciente); cada vez que N se
  duplica, el tiempo casi se duplica → O(N). Las comparaciones promedio son ≈ 0,75·N, lo que se
  espera con 50 % de búsquedas exitosas (≈ N/2 comparaciones) y 50 % fallidas (N comparaciones).
- *Búsqueda en ABB (aleatorio) y B+:* pendientes 0,10–0,16. Al pasar de N = 1.000 a 32.000
  (32 veces más datos) las comparaciones solo suben de ≈ 10 a ≈ 16, es decir, aumentan en
  log₂(32) = 5 → O(log N).
- *Inserción:* la lista es O(1) por elemento (construirla es O(N), pendiente 0,89–0,92). La pendiente sale algo menor que 1 porque con N pequeño el
  tiempo total es de apenas ≈ 0,04 ms y pesan los costos fijos de la medición (llamar la función,
  leer el reloj, reservar memoria): el costo por estudiante baja de ≈ 43–55 ns con N = 1.000 a
  ≈ 33–35 ns con N = 32.000, donde ya se estabiliza. Es un efecto de costo constante, no un
  crecimiento sublineal. En los árboles
  balanceados la pendiente es 1,11–1,18, compatible con O(N log N) para construir el árbol.
  El ABB con IDs crecientes tiene pendiente **2,09** → O(N²): construir con 32.000 estudiantes
  tarda 25,3 s contra 0,031 s con IDs aleatorios (≈ 800 veces más).
- *Listado:* las tres estructuras tienen pendiente cercana a 1 (0,85–1,11). La diferencia entre O(N log N) (`sorted`)
  y O(N) no se alcanza a ver en este rango, porque log N casi no cambia entre 1.000 y 32.000.
  Con IDs crecientes la lista lista ≈ 2 veces más rápido (2,6 ms vs 5,8 ms) porque el algoritmo de
  ordenamiento de Python (Timsort) detecta que los datos ya vienen ordenados y trabaja en O(N).

**¿En qué situaciones el ABB deja de comportarse como O(log N)?** Cuando los IDs llegan
ordenados (crecientes, y lo mismo pasaría con decrecientes o casi ordenados). Cada nuevo
estudiante queda como hijo derecho del anterior, la altura pasa a ser N (gráfica 4) y la búsqueda
se vuelve O(N): la pendiente pasa de 0,16 a 1,11 (gráfica 7).

**¿Qué relación existe entre la altura y el tiempo de búsqueda?** La búsqueda baja un nivel por
comparación, así que las comparaciones están acotadas por la altura, y el tiempo es proporcional a
las comparaciones. En la tabla resumen el costo por comparación se mantiene casi constante dentro de
cada estructura (≈ 30 ns en la lista, ≈ 50 ns en el ABB aleatorio, ≈ 80 ns en el B+). Con IDs
crecientes, el ABB tiene altura 32.000 y hace las **mismas** 24.082 comparaciones promedio que la lista.

**¿Qué ocurre cuando los datos se insertan ordenadamente?**
- El ABB degenera: su inserción pasa a O(N²) y su búsqueda a O(N). Con N = 32.000 la búsqueda
  es incluso **más lenta que la lista** (3,02 s vs 2,04 s) con el mismo número de comparaciones,
  porque seguir punteros entre nodos dispersos en memoria cuesta más (≈ 63 ns por comparación)
  que recorrer un arreglo contiguo (≈ 42 ns).
- El B+ no cambia: su altura sigue en 3–4 niveles y sus tiempos son prácticamente los mismos.
  Esto justifica por qué existen los árboles balanceados.
- La lista casi no cambia, porque no depende del orden (solo su listado se vuelve más rápido).

**¿Qué diferencias hay entre los casos aleatorio y creciente?** Solo el ABB cambia de forma
importante (gráficas 1, 2 y 4). La lista y el B+ dan resultados muy parecidos en ambos casos.

**¿A partir de qué N se ven claramente las diferencias?**
- Lista vs. árboles: ya con N = 1.000 la lista es ≈ 24–44 veces más lenta en búsqueda
  (39 ms vs 0,9–1,6 ms), y con N = 32.000 es ≈ 680–970 veces más lenta.
- ABB aleatorio vs. creciente: ya con N = 1.000 la búsqueda es ≈ 77 veces más lenta en el ABB
  degenerado. En segundos absolutos se hace visible a partir de N ≈ 8.000 (0,62 s de búsqueda y
  1,3 s de construcción).
- ABB aleatorio vs. B+: **no** se separan en este rango; los dos son O(log N).

**¿Hay costos constantes que igualen algoritmos de distinta complejidad para N pequeños?** Sí:
- El ABB aleatorio es algo más rápido que el B+ (1,7 ms vs 2,4 ms con N = 32.000) aunque hacen
  casi las mismas comparaciones (15,7 vs 15,4). El B+ paga más por comparación (≈ 80 ns vs 50 ns)
  por la búsqueda binaria dentro de cada nodo y las divisiones de nodos. La ventaja real del B+ es
  que **garantiza** O(log N) sin importar el orden, y que su altura (4) es mucho menor, lo que en
  disco significa muchos menos accesos.
- La inserción en la lista (`append`) es más rápida que en los árboles, que crean un nodo y lo
  recorren: ≈ 12–23 veces con N = 1.000 y ≈ 30–45 veces con N = 32.000 (IDs aleatorios). Para N pequeños y pocas búsquedas, la lista puede ser suficiente.
- Con N = 1.000 el ABB degenerado y la lista tardan lo mismo en orden de magnitud (68 ms vs 46 ms)
  aunque sus estructuras son muy distintas.

## 6. Conclusiones

1. La lista escala linealmente en búsqueda; los árboles balanceados, de forma logarítmica. La
   diferencia es de ~24–44× con 1.000 estudiantes y de ~680–970× con 32.000.
2. El rendimiento del ABB depende del orden de los datos. Con IDs ordenados se comporta como una
   lista (altura = N), pero con un costo constante mayor, y construirlo cuesta O(N²).
3. El B+ mantiene altura 3–4 y tiempos de milisegundos en todos los casos: es la opción más
   robusta, y además es la más rápida para listar gracias a las hojas enlazadas.
4. La altura del árbol explica el tiempo de búsqueda: comparaciones ≈ profundidad recorrida, y
   tiempo ≈ comparaciones × costo constante de cada estructura.

## 7. Limitaciones

- Se midió en Python: los costos constantes (≈ 25–100 ns por comparación) son mucho mayores que en
  C o Java. Las **pendientes** sí son comparables; los tiempos absolutos no.
- Las búsquedas inexistentes usan IDs mayores que todos los existentes. En el ABB esto recorre la
  rama derecha (más corta que el promedio), así que las búsquedas fallidas del ABB aleatorio salen
  algo más baratas que con IDs "en los huecos". Para la lista da igual: recorre todo.
- N máximo de 32.000 por el costo O(N²) del ABB degenerado. Con N más grande se distinguiría mejor
  O(N log N) de O(N) en el listado.
- 10 repeticiones dan una estimación razonable de la media, pero no alcanzan para pruebas de
  hipótesis finas. Las medidas de menos de 0,1 s son más ruidosas (CV típico de 4–26 %, y hasta
  76 % en tres listados de menos de 0,4 ms); en esos puntos ruidosos solo se puede confiar en el
  orden de magnitud.
- Se ejecutó en un portátil con Windows: la frecuencia del procesador varía (turbo y modos de
  ahorro de energía) y hay procesos en segundo plano que no se pueden controlar del todo. Por eso
  los tiempos absolutos dependen del equipo y de su configuración, y los resultados se comparan
  sobre todo por sus **pendientes**, que no dependen de la velocidad del equipo.
- No se probaron inserciones "casi ordenadas" ni IDs decrecientes en el experimento (sí en las pruebas de corrección).

## 8. Cómo reproducir

Requiere Python 3.10 o superior (`graficas.py` usa `statistics.linear_regression`; el experimento se corrió con Python 3.13.3). En Windows, si tiene varias versiones de Python instaladas, puede usar `py -3.13` en lugar de `python` (por ejemplo, `py -3.13 -m pip install -r requirements.txt` y `py -3.13 experimento.py`).

```bash
pip install -r requirements.txt
python test_estructuras.py   # verifica que las 3 estructuras son correctas (~5–10 s)
python experimento.py        # corre el experimento (~8 min) -> resultados/mediciones.csv
python graficas.py           # genera graficas/*.png y resultados/resumen.md (~10 s)
```

`graficas.py` solo lee el CSV, así que las gráficas se pueden regenerar sin repetir el experimento.
Para cambiar N, M, repeticiones u orden del B+, edite las constantes al inicio de `experimento.py`.
Con la misma semilla se obtienen los mismos datos y búsquedas; los tiempos variarán según el equipo.

## 9. Estructura del repositorio

```
estudiante.py          clase Estudiante (id, nombre, edad, promedio)
lista.py               estrategia 1: lista
abb.py                 estrategia 2: árbol binario de búsqueda
arbol_bmas.py          estrategia 3: árbol B+
test_estructuras.py    pruebas de corrección
experimento.py         experimento -> resultados/mediciones.csv, resultados/entorno.txt
graficas.py            gráficas y tabla resumen a partir del CSV
graficas/              7 gráficas PNG
resultados/            datos crudos, resumen y entorno de ejecución
README.md              documentación y material de apoyo para la sustentación
INFORME.md             informe del laboratorio
CODIGO_DE_HONOR.md     código de honor y declaración de uso de IA
```
