"""B4 · toda fila de precio lleva procedencia completa.

Procedencia = de donde salio y cuando. Sin los cuatro campos, un precio es un
rumor con formato de tabla.
"""
import sys

import gate_util
from gate_util import exigir

MARCADOR = "procedencia verificada · sin filas incompletas"

OBLIGATORIOS = (
    "fuente",
    "consulta_url",
    "fecha_dato",
    "capturado_en",
    "alcance",
    "mercado",
    "moneda",
    # Sin la base del precio, un 310 y un 34.44 del mismo aguacate parecen
    # precios distintos y son el mismo.
    "base_precio",
)


def verificar():
    import comun

    detalles = []
    conexion = comun.conectar()
    total = conexion.execute("SELECT COUNT(*) FROM precios").fetchone()[0]
    exigir(total > 0, "la base no tiene filas: un verde aqui no probaria nada")
    detalles.append(f"filas evaluadas: {total}")

    for campo in OBLIGATORIOS:
        huecos = conexion.execute(
            f"SELECT COUNT(*) FROM precios WHERE {campo} IS NULL OR TRIM({campo}) = ''"
        ).fetchone()[0]
        exigir(huecos == 0, f"{huecos} filas sin {campo}")
    detalles.append(f"los {len(OBLIGATORIOS)} campos de procedencia estan completos en todas las filas")

    # La url de consulta tiene que apuntar a la fuente declarada, no a cualquier
    # cosa: una url inventada pasaria un chequeo de no vacio.
    for clave, url_base in conexion.execute("SELECT clave, url_base FROM fuentes"):
        desalineadas = conexion.execute(
            "SELECT COUNT(*) FROM precios WHERE fuente = ? AND consulta_url NOT LIKE ?",
            (clave, url_base.split("?")[0] + "%"),
        ).fetchone()[0]
        exigir(desalineadas == 0, f"{desalineadas} filas de {clave} citan una url ajena a su fuente")
    detalles.append("cada url de consulta apunta a la fuente declarada de su fila")

    # Un precio sin ningun valor numerico es una fila que no dice nada.
    vacias = conexion.execute(
        "SELECT COUNT(*) FROM precios WHERE precio_min IS NULL AND precio_max IS NULL"
        " AND precio_frec IS NULL"
    ).fetchone()[0]
    exigir(vacias == 0, f"{vacias} filas sin ningun precio")

    # La captura no puede ser anterior al dato que dice haber capturado.
    imposibles = conexion.execute(
        "SELECT COUNT(*) FROM precios WHERE SUBSTR(capturado_en, 1, 10) < fecha_dato"
    ).fetchone()[0]
    exigir(imposibles == 0, f"{imposibles} filas capturadas antes de la fecha de su dato")
    detalles.append("sin filas sin precio ni capturas anteriores a su propio dato")

    conexion.close()
    return detalles


if __name__ == "__main__":
    sys.exit(gate_util.correr(verificar, MARCADOR))
