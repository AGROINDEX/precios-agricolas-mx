"""B22 · la ingesta pide un rango y lee la fecha de cada fila.

POR QUE IMPORTA. Llenar la ventana de 90 dias con una peticion por dia serian
90 por 42 plazas, o sea 3,780 peticiones. Por rango son 42. Y leer por rango
obliga a leer la fecha de cada fila en vez de asumir la del dia pedido, que es
mejor por si solo: si la fuente publica tarde, la fila llega con su fecha
correcta en vez de con la de hoy.

QUE SE COMPRUEBA, sobre una base temporal y con UNA sola plaza:

1. Una peticion de rango trae VARIOS dias distintos. Si trajera uno, el rango
   no estaria funcionando y no nos habriamos enterado.
2. Las fechas guardadas son las de las filas, no la del extremo del rango. Se
   comprueba exigiendo que exista al menos una fila con fecha ANTERIOR a
   `hasta`, que es imposible si se estuviera asumiendo la fecha pedida.
3. Idempotencia: la segunda corrida del mismo rango inserta cero filas.
4. El parser entiende las dos formas de la tabla. Se le da un fragmento de
   control con columna Fecha y otro sin ella, y tiene que leer las dos.
5. La ventana declarada se respeta: pedir mas dias que la ventana se rechaza.

Uso:
  python tools/verificar_ingesta_rango.py
"""
import os
import subprocess
import sys
import tempfile
from datetime import date, timedelta

import gate_util
from gate_util import exigir, ruta

MARCADOR = "ingesta por rango verificada · fecha leida por fila y segunda corrida sin inserciones"

PLAZA = "100"  # Iztapalapa, la plaza mas estable de la fuente
DIAS = 12

TABLA_CON_FECHA = """
<table><tr><td>Fecha</td><td>Producto</td><td>Calidad</td><td>Presentación</td><td>Origen</td>
<td>Precio Mín</td><td>Precio Max</td><td>Precio Frec</td><td>Obs.</td></tr>
<tr><td>18/11/2026</td><td>Control con fecha</td><td>Primera</td><td>Kilogramo</td>
<td>Puebla</td><td>10.00</td><td>12.00</td><td>11.00</td><td></td></tr></table>
"""

TABLA_SIN_FECHA = """
<table><tr><td>Producto</td><td>Calidad</td><td>Presentación</td><td>Origen</td>
<td>Precio Mín</td><td>Precio Max</td><td>Precio Frec</td><td>Obs.</td></tr>
<tr><td>Control sin fecha</td><td>Primera</td><td>Kilogramo</td><td>Puebla</td>
<td>20.00</td><td>22.00</td><td>21.00</td><td></td></tr></table>
"""


def verificar():
    sys.path.insert(0, ruta("ingesta"))
    import sniim
    from comun import FUENTES

    detalles = []
    hasta = date.today()
    desde = hasta - timedelta(days=DIAS)

    # 4. El parser entiende las dos formas, y se prueba antes de gastar red.
    con_fecha = sniim.extraer(TABLA_CON_FECHA, hasta, "Plaza de control", "u", "c")
    exigir(len(con_fecha) == 1, f"la tabla con columna Fecha dio {len(con_fecha)} filas")
    exigir(
        con_fecha[0]["fecha_dato"] == "2026-11-18",
        f"la fila con fecha propia quedo con fecha {con_fecha[0]['fecha_dato']}:"
        " el parser esta asumiendo la fecha en vez de leerla",
    )
    exigir(
        con_fecha[0]["producto"] == "Control con fecha",
        f"con columna Fecha el parser leyo el producto corrido: {con_fecha[0]['producto']}",
    )
    sin_fecha = sniim.extraer(TABLA_SIN_FECHA, hasta, "Plaza de control", "u", "c")
    exigir(len(sin_fecha) == 1, f"la tabla sin columna Fecha dio {len(sin_fecha)} filas")
    exigir(
        sin_fecha[0]["fecha_dato"] == hasta.isoformat(),
        "sin columna Fecha la fila deberia tomar el dia pedido",
    )
    exigir(
        sin_fecha[0]["producto"] == "Control sin fecha",
        f"sin columna Fecha el parser leyo el producto corrido: {sin_fecha[0]['producto']}",
    )
    detalles.append("el parser lee las dos formas de la tabla, con y sin columna Fecha")

    # 1, 2 y 3 contra la fuente, en base temporal.
    carpeta = tempfile.mkdtemp(prefix="gate_rango_")
    base = os.path.join(carpeta, "rango.db")
    reporte = os.path.join(carpeta, "reporte.json")

    codigo = sniim.correr(desde, hasta, [PLAZA], base, reporte)
    exigir(codigo == 0, "la ingesta por rango fallo en su primera corrida")

    import sqlite3

    conexion = sqlite3.connect(base)
    fechas = [
        fila[0]
        for fila in conexion.execute(
            "SELECT DISTINCT fecha_dato FROM precios ORDER BY fecha_dato"
        )
    ]
    filas_totales = conexion.execute("SELECT COUNT(*) FROM precios").fetchone()[0]
    conexion.close()

    exigir(
        len(fechas) >= 3,
        f"una peticion de rango de {DIAS} dias trajo solo {len(fechas)} dias distintos:"
        " el rango no esta funcionando",
    )
    exigir(
        any(fecha < hasta.isoformat() for fecha in fechas),
        f"todas las filas quedaron con fecha {hasta.isoformat()}: la fecha se esta"
        " asumiendo en vez de leerse de la fila",
    )
    exigir(
        all(desde.isoformat() <= fecha <= hasta.isoformat() for fecha in fechas),
        f"llegaron fechas fuera del rango pedido: {fechas}",
    )
    detalles.append(
        f"una peticion trajo {filas_totales} filas en {len(fechas)} dias distintos,"
        f" de {fechas[0]} a {fechas[-1]}"
    )

    conexion = sqlite3.connect(base)
    antes = conexion.execute("SELECT COUNT(*) FROM precios").fetchone()[0]
    conexion.close()
    sniim.correr(desde, hasta, [PLAZA], base, reporte)
    conexion = sqlite3.connect(base)
    despues = conexion.execute("SELECT COUNT(*) FROM precios").fetchone()[0]
    conexion.close()
    exigir(
        antes == despues,
        f"la segunda corrida del mismo rango cambio el conteo de {antes} a {despues}",
    )
    detalles.append(f"segunda corrida del mismo rango: {despues} filas, cero inserciones")

    # 5. La ventana declarada se respeta.
    ventana = FUENTES["SNIIM_FYH"]["ventana_dias"]
    corrida = subprocess.run(
        [
            sys.executable,
            ruta("ingesta", "sniim.py"),
            "--dias",
            str(ventana + 1),
            "--plazas",
            PLAZA,
            "--base",
            base,
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    exigir(
        corrida.returncode != 0,
        f"pedir {ventana + 1} dias no fue rechazado y la ventana declarada es de {ventana}",
    )
    exigir(
        "excede la ventana declarada" in (corrida.stdout + corrida.stderr),
        "el rechazo no explica que se excedio la ventana declarada",
    )
    detalles.append(f"pedir {ventana + 1} dias se rechaza: la ventana declarada es {ventana}")
    return detalles


if __name__ == "__main__":
    sys.exit(gate_util.correr(verificar, MARCADOR))
