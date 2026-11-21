"""Carga de datos compartida por las propuestas de diseno.

Las tres propuestas se dibujan sobre la MISMA base real, no sobre datos de
relleno. Una maqueta con numeros inventados miente sobre lo dificil: cuantos
productos hay, que tan largos son los nombres, cuantos valores faltan. Aqui no
hay ni un numero escrito a mano.
"""
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "ingesta"))

from comun import conectar, frase_cadencia  # noqa: E402
from frescura_real import VEREDICTOS, frase, medir  # noqa: E402

# Toda la ventana declarada. La grafica no se recorta a mano: si la base guarda
# 90 dias, la vista los muestra, y si guarda 10 la vista lo dice con las fechas
# de los extremos.
HISTORIA = 400


def cargar(ruta_base=None):
    conexion = conectar(ruta_base)

    fuentes = {
        fila[0]: {
            "clave": fila[0],
            "nombre": fila[1],
            "atribucion": fila[2],
            "url": fila[3],
            "ventana": fila[4],
        }
        for fila in conexion.execute(
            "SELECT clave, nombre, atribucion, url_base, ventana_dias FROM fuentes"
        )
    }

    movimiento = medir(conexion)
    bloques = []

    for clave in sorted(fuentes):
        for mercado, ultima in conexion.execute(
            "SELECT mercado, MAX(fecha_dato) FROM precios WHERE fuente = ?"
            " GROUP BY mercado ORDER BY mercado",
            (clave,),
        ).fetchall():
            if not ultima:
                continue
            filas = []
            for fila in conexion.execute(
                """
                SELECT p.producto, p.calidad, p.presentacion, p.origen, p.precio_min,
                       p.precio_max, p.precio_frec, p.fecha_dato, p.base_precio,
                       d.mediana_frec_7d, d.variacion_pct_1d, d.amplitud_rel
                FROM precios p
                LEFT JOIN derivados d
                  ON d.fuente = p.fuente AND d.producto = p.producto
                 AND d.mercado = p.mercado AND d.fecha_dato = p.fecha_dato
                WHERE p.fuente = ? AND p.fecha_dato = ? AND p.mercado = ?
                ORDER BY p.producto, p.presentacion
                """,
                (clave, ultima, mercado),
            ):
                registro = {
                    "producto": fila[0],
                    "calidad": fila[1],
                    "presentacion": fila[2],
                    "origen": fila[3],
                    "min": fila[4],
                    "max": fila[5],
                    "frec": fila[6],
                    "fecha": fila[7],
                    "base": fila[8],
                    "mediana": fila[9],
                    "variacion": fila[10],
                    "amplitud": fila[11],
                }
                registro["serie"] = serie(conexion, clave, mercado, fila[0], fila[2])
                filas.append(registro)
            bloques.append(
                {
                    "fuente": fuentes[clave],
                    "mercado": mercado,
                    "fecha": ultima,
                    "filas": filas,
                    "pulso": movimiento.get(clave, {}).get(mercado),
                    # La cadencia viaja con el bloque: una maqueta que no la
                    # diga presenta como rota a la plaza que publica los lunes.
                    "cadencia": frase_cadencia(mercado),
                }
            )

    conexion.close()
    # El corte mas fresco arriba. Una plaza que publico hoy manda sobre una que
    # publico ayer, y el usuario no tiene que buscar cual es cual.
    bloques.sort(key=lambda bloque: (bloque["fecha"], len(bloque["filas"])), reverse=True)
    return fuentes, bloques


def serie(conexion, clave, mercado, producto, presentacion):
    """Historico crudo del producto en esa plaza, de mas viejo a mas nuevo.

    Un punto por dia PUBLICADO. Los dias sin publicacion no se rellenan con el
    valor anterior: inventar la meseta del domingo es exactamente la mentira
    que la medida de frescura real existe para detectar.
    """
    filas = conexion.execute(
        "SELECT fecha_dato, precio_min, precio_max, precio_frec FROM precios"
        " WHERE fuente = ? AND mercado = ? AND producto = ? AND presentacion = ?"
        " AND precio_frec IS NOT NULL ORDER BY fecha_dato DESC LIMIT ?",
        (clave, mercado, producto, presentacion, HISTORIA),
    ).fetchall()
    return [
        {"fecha": fila[0], "min": fila[1], "max": fila[2], "frec": fila[3]}
        for fila in reversed(filas)
    ]


def etiqueta_base(filas):
    bases = {fila["base"] for fila in filas}
    if bases == {"kilogramo"}:
        return "por kilogramo, calculado por la fuente"
    if bases == {"presentacion"}:
        return "por presentacion comercial completa, no por kilogramo"
    return "cuidado: esta plaza mezcla bases de precio distintas"


__all__ = ["cargar", "etiqueta_base", "VEREDICTOS", "frase", "frase_cadencia", "HISTORIA"]
