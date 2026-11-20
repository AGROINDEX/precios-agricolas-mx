"""Indicadores propios sobre la ventana declarada.

POR QUE EXISTEN. El articulo 108 de la LFDA protege la base no original de
quien la elaboro. Republicar la tabla del SNIIM seria eso. Estos tres
indicadores no estan en ninguna fuente: se calculan aqui sobre la ventana corta
y son lo unico que el producto publica como propio, con el dato puntual citado y
atribuido al lado.

  mediana_frec_7d   mediana del precio frecuente de los ultimos siete dias con
                    publicacion, por producto y plaza. Mediana y no promedio
                    porque una sola plaza con presentacion distinta mueve la
                    media y deja de describir el mercado.
  variacion_pct_1d  cambio contra el dia publicado anterior, no contra ayer de
                    calendario: el SNIIM no publica sabados, domingos ni dias
                    festivos, y comparar contra un hueco inventa saltos.
  amplitud_rel      (max - min) / frecuente del dia. Es la medida honesta de
                    cuanto NO sabemos: donde la amplitud es ancha, el numero
                    unico miente mas.

Uso:
  python ingesta/derivados.py
  python ingesta/derivados.py --base otra.db
"""
import argparse
import statistics
import sys

import comun_bootstrap  # noqa: F401
from comun import ahora, conectar


def calcular(conexion):
    filas = conexion.execute(
        """
        SELECT fuente, producto, mercado, fecha_dato,
               AVG(precio_frec) AS frec,
               AVG(precio_min) AS minimo,
               AVG(precio_max) AS maximo,
               COUNT(*) AS n
        FROM precios
        WHERE precio_frec IS NOT NULL
        GROUP BY fuente, producto, mercado, fecha_dato
        ORDER BY fuente, producto, mercado, fecha_dato
        """
    ).fetchall()

    series = {}
    for fuente, producto, mercado, fecha, frec, minimo, maximo, n in filas:
        series.setdefault((fuente, producto, mercado), []).append((fecha, frec, minimo, maximo, n))

    calculado_en = ahora()
    escritas = 0
    for (fuente, producto, mercado), puntos in series.items():
        for indice, (fecha, frec, minimo, maximo, _n) in enumerate(puntos):
            ventana = [p[1] for p in puntos[max(0, indice - 6) : indice + 1]]
            mediana = statistics.median(ventana)
            previo = puntos[indice - 1][1] if indice > 0 else None
            variacion = None
            if previo:
                variacion = round((frec - previo) / previo * 100, 2)
            amplitud = None
            if frec and minimo is not None and maximo is not None:
                amplitud = round((maximo - minimo) / frec, 4)
            conexion.execute(
                """
                INSERT INTO derivados (fuente, producto, mercado, fecha_dato, mediana_frec_7d,
                                       variacion_pct_1d, amplitud_rel, n_obs_7d, calculado_en)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (fuente, producto, mercado, fecha_dato) DO UPDATE SET
                    mediana_frec_7d = excluded.mediana_frec_7d,
                    variacion_pct_1d = excluded.variacion_pct_1d,
                    amplitud_rel = excluded.amplitud_rel,
                    n_obs_7d = excluded.n_obs_7d,
                    calculado_en = excluded.calculado_en
                """,
                (
                    fuente,
                    producto,
                    mercado,
                    fecha,
                    round(mediana, 2),
                    variacion,
                    amplitud,
                    len(ventana),
                    calculado_en,
                ),
            )
            escritas += 1
    conexion.commit()
    return escritas


if __name__ == "__main__":
    lector = argparse.ArgumentParser(description="Calcula los indicadores propios")
    lector.add_argument("--base")
    argumentos = lector.parse_args()
    conexion_abierta = conectar(argumentos.base)
    total = calcular(conexion_abierta)
    conexion_abierta.close()
    print(f"derivados calculados: {total}")
    sys.exit(0 if total else 1)
