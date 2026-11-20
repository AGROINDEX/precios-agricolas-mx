"""B15 · la base guarda la ventana declarada rellenada, y no mas.

DOS FALLAS OPUESTAS, UN SOLO GATE. Por arriba, guardar mas profundidad que la
ventana declarada convierte la base en un espejo del acervo, que es justo lo
que el articulo 108 de la LFDA reserva a quien lo elaboro. Por abajo, una
ventana declarada de 90 dias con tres dias dentro hace que la vista historica
dibuje una recta de dos puntos y pretenda que eso es el historico.

El gate falla en los dos sentidos: ninguna fuente puede exceder su ventana, y
la fuente principal tiene que tener profundidad suficiente para que la grafica
diga algo.
"""
import os
import sys
from datetime import date, datetime

import gate_util
from gate_util import exigir

sys.path.insert(0, os.path.join(gate_util.RAIZ, "ingesta"))

from comun import FUENTES, conectar  # noqa: E402

MARCADOR = "historico verificado · ventana rellenada sin exceder la declarada"

# Minimo para que una grafica de linea no sea un adorno. Por debajo de esto la
# vista tiene que decir que no hay historico, no dibujar una recta.
DIAS_UTILES = 20


def verificar():
    detalles = []
    conexion = conectar()
    hoy = date.today()

    filas = conexion.execute(
        "SELECT fuente, mercado, COUNT(DISTINCT fecha_dato), MIN(fecha_dato), MAX(fecha_dato)"
        " FROM precios GROUP BY fuente, mercado"
    ).fetchall()
    exigir(filas, "no hay ninguna fila de precios en la base")

    profundos = 0
    for fuente, mercado, dias, primera, ultima in filas:
        ventana = FUENTES[fuente]["ventana_dias"]
        antiguedad = (hoy - datetime.strptime(primera, "%Y-%m-%d").date()).days
        exigir(
            antiguedad <= ventana,
            f"{mercado} guarda {antiguedad} dias de profundidad y la ventana declarada de "
            f"{fuente} es de {ventana}: eso ya es espejo del acervo",
        )
        exigir(
            dias >= 2 or dias == 1,
            f"{mercado} no tiene ningun dia publicado",
        )
        if dias >= DIAS_UTILES:
            profundos += 1
        detalles.append(f"{mercado}: {dias} dias publicados entre {primera} y {ultima}")

    exigir(
        profundos >= 2,
        f"solo {profundos} plazas llegan a {DIAS_UTILES} dias publicados: la vista historica "
        "no tendria de donde dibujarse",
    )

    # El calculo derivado se conserva aunque la mediana salga de la vista: es lo
    # que sostiene el gate B5 del articulo 108.
    derivados = conexion.execute("SELECT COUNT(*) FROM derivados").fetchone()[0]
    exigir(
        derivados > 0,
        "la tabla de derivados quedo vacia: sin indicador propio la base es solo una copia",
    )
    detalles.append(f"{derivados} derivados propios conservados en la base")
    conexion.close()
    return detalles


if __name__ == "__main__":
    sys.exit(gate_util.correr(verificar, MARCADOR))
