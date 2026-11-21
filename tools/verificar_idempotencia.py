"""B2 y B3 · la ingesta corre sobre un dia y la segunda corrida no inserta nada.

COMO SE MIDE. No se le cree al contador que imprime la ingesta: se corre dos
veces contra una base temporal vacia y se cuentan las filas EN LA BASE despues
de cada corrida, mas un sello de las filas para detectar modificaciones que no
cambien el conteo. Medicion independiente del artefacto que se evalua.

Uso:
  python tools/verificar_idempotencia.py --fuente sniim
  python tools/verificar_idempotencia.py --fuente ficeda
"""
import argparse
import hashlib
import os
import sqlite3
import sys
import tempfile
from datetime import date, timedelta

import gate_util
from gate_util import exigir


def sello(base):
    conexion = sqlite3.connect(base)
    filas = conexion.execute(
        "SELECT fuente, fecha_dato, producto, calidad, presentacion, origen, mercado,"
        " observaciones, precio_min, precio_max, precio_frec FROM precios"
        " ORDER BY fuente, fecha_dato, producto, presentacion, origen, mercado, observaciones"
    ).fetchall()
    conexion.close()
    digestor = hashlib.sha256()
    for fila in filas:
        digestor.update(repr(fila).encode("utf-8"))
    return len(filas), digestor.hexdigest()[:16]


def verificar_sniim(base, reporte):
    import sniim

    # La ingesta pide un RANGO, una peticion por plaza. Se mide sobre una
    # ventana corta y reciente: si trae filas, el rango sirve para la prueba.
    hasta = date.today()
    desde = hasta - timedelta(days=7)
    sniim.correr(desde, hasta, ["100"], base, reporte)
    filas, _ = sello(base)
    exigir(filas, "la ventana de los ultimos ocho dias no trajo filas del SNIIM")
    return (
        lambda: sniim.correr(desde, hasta, ["100"], base, reporte),
        f"rango medido: {desde.isoformat()} a {hasta.isoformat()}, {filas} filas",
    )


def verificar_ficeda(base, reporte):
    import ficeda

    ficeda.correr(base, reporte)
    return lambda: ficeda.correr(base, reporte), "corte vigente del visor"


def verificar(nombre_fuente):
    detalles = []
    carpeta = tempfile.mkdtemp(prefix=f"gate_idem_{nombre_fuente}_")
    base = os.path.join(carpeta, "prueba.db")
    reporte = os.path.join(carpeta, "_fetch_report.json")

    if nombre_fuente == "sniim":
        repetir, nota = verificar_sniim(base, reporte)
    else:
        repetir, nota = verificar_ficeda(base, reporte)

    primera_cuenta, primer_sello = sello(base)
    exigir(primera_cuenta > 0, "la primera corrida no dejo ninguna fila: no hay nada que probar")
    detalles.append(f"{nota} · primera corrida: {primera_cuenta} filas · sello {primer_sello}")

    repetir()
    segunda_cuenta, segundo_sello = sello(base)
    exigir(
        segunda_cuenta == primera_cuenta,
        f"la segunda corrida cambio el conteo: {primera_cuenta} a {segunda_cuenta}",
    )
    exigir(
        segundo_sello == primer_sello,
        "la segunda corrida modifico filas existentes sin cambiar el conteo",
    )
    detalles.append(f"segunda corrida: {segunda_cuenta} filas · sello {segundo_sello} · cero inserciones")
    return detalles


if __name__ == "__main__":
    lector = argparse.ArgumentParser(description="Verifica idempotencia de una ingesta")
    lector.add_argument("--fuente", required=True, choices=["sniim", "ficeda"])
    argumentos = lector.parse_args()
    marcador = f"idempotencia {argumentos.fuente} verificada · segunda corrida con cero inserciones"
    sys.exit(gate_util.correr(lambda: verificar(argumentos.fuente), marcador))
