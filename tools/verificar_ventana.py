"""B5 · ventana declarada respetada y derivado propio calculado, no copiado.

Este es el gate del articulo 108. Dos mitades:

1. Ninguna fuente guarda mas profundidad que su ventana declarada. Si la base
   creciera sin limite seria un espejo del acervo ajeno, que es exactamente lo
   que la ley protege para quien lo elaboro.
2. Existe al menos un indicador propio, y su valor se recalcula aqui desde las
   filas crudas. Si el derivado fuera una copia de un campo de la fuente, el
   recalculo no coincidiria con la definicion que el proyecto declara.
"""
import statistics
import sys
from datetime import date, datetime

import gate_util
from gate_util import exigir

MARCADOR = "ventana verificada · sin espejo del acervo y con derivado propio"


def verificar():
    import comun

    detalles = []
    conexion = comun.conectar()

    fuentes = conexion.execute(
        "SELECT clave, ventana_dias FROM fuentes WHERE clave IN (SELECT DISTINCT fuente FROM precios)"
    ).fetchall()
    exigir(fuentes, "ninguna fuente tiene filas en la base")

    for clave, ventana in fuentes:
        minima, maxima, cuenta = conexion.execute(
            "SELECT MIN(fecha_dato), MAX(fecha_dato), COUNT(*) FROM precios WHERE fuente = ?",
            (clave,),
        ).fetchone()
        profundidad = (date.today() - datetime.strptime(minima, "%Y-%m-%d").date()).days
        exigir(
            profundidad <= ventana,
            f"{clave} guarda {profundidad} dias de profundidad y su ventana declarada es {ventana}",
        )
        detalles.append(
            f"{clave}: {cuenta} filas · del {minima} al {maxima} · profundidad {profundidad} de {ventana} dias"
        )

    derivados = conexion.execute("SELECT COUNT(*) FROM derivados").fetchone()[0]
    exigir(derivados > 0, "no hay ningun indicador derivado calculado")
    detalles.append(f"indicadores propios en la base: {derivados}")

    # Recalculo independiente de la mediana de siete dias de una serie real.
    objetivo = conexion.execute(
        """
        SELECT fuente, producto, mercado, fecha_dato, mediana_frec_7d
        FROM derivados
        WHERE mediana_frec_7d IS NOT NULL AND n_obs_7d >= 3
        ORDER BY n_obs_7d DESC, fecha_dato DESC
        LIMIT 1
        """
    ).fetchone()
    exigir(objetivo is not None, "ningun derivado tiene al menos tres observaciones para recalcular")
    fuente, producto, mercado, fecha, guardada = objetivo

    serie = conexion.execute(
        """
        SELECT fecha_dato, AVG(precio_frec)
        FROM precios
        WHERE fuente = ? AND producto = ? AND mercado = ? AND fecha_dato <= ?
          AND precio_frec IS NOT NULL
        GROUP BY fecha_dato
        ORDER BY fecha_dato DESC
        LIMIT 7
        """,
        (fuente, producto, mercado, fecha),
    ).fetchall()
    recalculada = round(statistics.median([valor for _f, valor in serie]), 2)
    exigir(
        abs(recalculada - guardada) <= 0.01,
        f"la mediana guardada ({guardada}) no coincide con el recalculo ({recalculada})"
        f" para {producto} en {mercado} al {fecha}",
    )
    detalles.append(
        f"recalculo independiente: {producto} en {mercado} al {fecha} · "
        f"mediana 7d guardada {guardada} y recalculada {recalculada} sobre {len(serie)} dias"
    )

    # El derivado no puede ser una copia disfrazada del precio del dia.
    iguales = conexion.execute(
        """
        SELECT COUNT(*) FROM derivados d
        JOIN (SELECT fuente, producto, mercado, fecha_dato, AVG(precio_frec) AS frec
              FROM precios GROUP BY fuente, producto, mercado, fecha_dato) p
          ON p.fuente = d.fuente AND p.producto = d.producto
         AND p.mercado = d.mercado AND p.fecha_dato = d.fecha_dato
        WHERE d.n_obs_7d >= 3 AND ABS(COALESCE(d.mediana_frec_7d, -1) - COALESCE(p.frec, -2)) < 0.005
        """
    ).fetchone()[0]
    con_historia = conexion.execute("SELECT COUNT(*) FROM derivados WHERE n_obs_7d >= 3").fetchone()[0]
    exigir(
        con_historia > 0 and iguales < con_historia,
        "todas las medianas coinciden exactamente con el precio del dia: el derivado no agrega nada",
    )
    detalles.append(
        f"de {con_historia} derivados con historia, {con_historia - iguales} difieren del precio del dia"
    )

    conexion.close()
    return detalles


if __name__ == "__main__":
    sys.exit(gate_util.correr(verificar, MARCADOR))
