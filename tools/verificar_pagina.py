"""B7 · la pagina declara frescura por fila y avisa cuando una fuente se congelo.

Se construye la pagina dos veces contra bases y reportes distintos, en carpeta
temporal, sin tocar la pagina publicada:

  con reporte real      no debe haber aviso de congelamiento
  con reporte congelado debe haber aviso visible y marca en las filas

La segunda mitad es el control del aviso: sin ella, la ausencia de aviso en la
pagina real no distingue entre fuentes sanas y codigo que nunca avisa.

Uso:
  python tools/verificar_pagina.py --estado-congelado-simulado
"""
import argparse
import os
import re
import sys
import tempfile

import gate_util
from gate_util import exigir, ruta

MARCADOR = "pagina verificada · aviso de congelamiento visible y frescura por fila"
CONTROL = ruta("fixtures", "pista_b", "fetch_report_congelado.json")
REPORTE_REAL = ruta("datos", "pista_b", "_fetch_report.json")


def construir(reporte, destino):
    sys.path.insert(0, ruta("web"))
    import construir as constructor

    import importlib

    importlib.reload(constructor)
    return constructor.construir(None, reporte, destino)


def filas_de(pagina):
    return re.findall(r"<tr[^>]*>(.*?)</tr>", pagina, re.S | re.I)


def verificar(simulado):
    detalles = []
    carpeta = tempfile.mkdtemp(prefix="gate_pagina_")

    destino_real = os.path.join(carpeta, "real.html")
    construir(REPORTE_REAL, destino_real)
    with open(destino_real, encoding="utf-8") as archivo:
        real = archivo.read()

    exigir("Fuente congelada" not in real, "la pagina avisa congelamiento con el reporte real sano")
    exigir(
        "no es precio en finca" in real,
        "la pagina no declara que el mayoreo no es precio en finca",
    )
    exigir("mayoreo" in real, "la pagina no declara el alcance del dato")

    # Atribucion de cada fuente con filas en la pagina.
    import comun

    conexion = comun.conectar()
    atribuciones = dict(
        conexion.execute(
            "SELECT clave, atribucion FROM fuentes WHERE clave IN (SELECT DISTINCT fuente FROM precios)"
        ).fetchall()
    )
    conexion.close()
    for clave, atribucion in atribuciones.items():
        exigir(atribucion in real, f"falta la atribucion de {clave} en la pagina")
    detalles.append(f"atribucion presente para las {len(atribuciones)} fuentes con datos")

    # Frescura por fila: cada fila de datos termina con una fecha ISO visible.
    con_fecha = 0
    sin_fecha = 0
    for fila in filas_de(real):
        celdas = re.findall(r"<td[^>]*>(.*?)</td>", fila, re.S | re.I)
        if not celdas:
            continue
        if re.search(r"\d{4}-\d{2}-\d{2}", celdas[-1]):
            con_fecha += 1
        else:
            sin_fecha += 1
    exigir(con_fecha > 0, "la pagina no tiene ninguna fila de datos con fecha")
    exigir(sin_fecha == 0, f"{sin_fecha} filas de datos sin fecha visible")
    detalles.append(f"filas con fecha propia visible: {con_fecha} de {con_fecha + sin_fecha}")

    if simulado:
        destino_congelado = os.path.join(carpeta, "congelado.html")
        _ruta, _bloques, congeladas = construir(CONTROL, destino_congelado)
        with open(destino_congelado, encoding="utf-8") as archivo:
            congelado = archivo.read()
        exigir(congeladas, "el constructor no reconocio ninguna fuente congelada del control")
        exigir("Fuente congelada" not in real, "contaminacion entre las dos construcciones")
        exigir(
            congelado.count("Fuente congelada") >= len(congeladas),
            "falta un aviso visible por cada fuente congelada",
        )
        exigir(
            "no es de hoy" in congelado,
            "la pagina no dice que el corte mostrado no es de hoy",
        )
        exigir("dato detenido" in congelado, "las filas de una fuente congelada no quedan marcadas")
        exigir(
            "rancia" in congelado,
            "las filas de una fuente congelada no reciben el estilo que las atenua",
        )
        detalles.append(
            f"con estado congelado simulado: {congelado.count('Fuente congelada')} avisos "
            f"para {len(congeladas)} fuentes, filas marcadas como dato detenido"
        )

    return detalles


if __name__ == "__main__":
    lector = argparse.ArgumentParser(description="Verifica la pagina de hoy")
    lector.add_argument("--estado-congelado-simulado", action="store_true")
    argumentos = lector.parse_args()
    sys.exit(gate_util.correr(lambda: verificar(argumentos.estado_congelado_simulado), MARCADOR))
