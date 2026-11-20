"""A1 · el boletin del dia trae procedencia y alcance completos.

Mide el archivo, no la intencion: cada cifra que el boletin publica tiene que
venir de una fila real y el texto tiene que declarar la fecha del corte, la
plaza, la base del precio, la atribucion y el alcance del dato.

Uso:
  python tools/verificar_boletin.py --dia hoy
  python tools/verificar_boletin.py --dia 2026-11-20 --boletin boletin/ultimo.md
"""
import argparse
import json
import os
import re
import sys
from datetime import date

import gate_util
from gate_util import exigir, ruta

MARCADOR = "boletin verificado · procedencia y alcance completos en todas las filas"


def cargar(camino):
    exigir(os.path.exists(camino), f"no existe el boletin en {camino}")
    with open(camino, encoding="utf-8") as archivo:
        return archivo.read()


def trazas_de(texto):
    encontrado = re.search(r"<!--\s*trazas:\s*(\[.*?\])\s*-->", texto, re.S)
    exigir(encontrado, "el boletin no trae bloque de trazas")
    return json.loads(encontrado.group(1))


def verificar(dia, camino):
    import comun

    detalles = []
    texto = cargar(camino)
    objetivo = date.today().isoformat() if dia == "hoy" else dia

    # El boletin es del dia pedido, aunque el corte de la fuente sea anterior.
    exigir(
        re.search(r"Boletin del \d{1,2} de \w+ de \d{4}", texto),
        "el boletin no declara su propia fecha",
    )
    exigir(
        objetivo.split("-")[2].lstrip("0") in texto,
        f"el boletin no parece ser del dia pedido ({objetivo})",
    )

    trazas = trazas_de(texto)
    exigir(trazas, "el bloque de trazas esta vacio")

    conexion = comun.conectar()
    atribuciones = dict(conexion.execute("SELECT clave, atribucion FROM fuentes").fetchall())
    for traza in trazas:
        fila = conexion.execute(
            "SELECT fecha_dato, precio_frec, base_precio, alcance, consulta_url, mercado, fuente"
            " FROM precios WHERE id = ?",
            (traza["id"],),
        ).fetchone()
        exigir(fila is not None, f"la traza {traza['id']} no corresponde a ninguna fila de la base")
        fecha, frecuente, base, alcance, consulta, mercado, fuente = fila
        exigir(fecha == traza["fecha_dato"], f"la traza {traza['id']} miente sobre la fecha")
        exigir(
            abs((frecuente or 0) - (traza["precio_frec"] or 0)) < 0.005,
            f"la traza {traza['id']} miente sobre el precio",
        )
        exigir(consulta == traza["consulta_url"], f"la traza {traza['id']} miente sobre la consulta")
        exigir(base in ("kilogramo", "presentacion"), f"la fila {traza['id']} no declara base de precio")
        exigir(alcance == "mayoreo", f"la fila {traza['id']} no es mayoreo y el boletin dice que si")
        exigir(
            f"{frecuente:,.2f}" in texto,
            f"el precio {frecuente} de la fila {traza['id']} no aparece en el texto del boletin",
        )
        exigir(
            atribuciones[fuente].rstrip(".") in texto,
            f"falta la atribucion de {fuente} en el boletin",
        )
        detalles.append(
            f"traza {traza['id']}: {fuente} · {mercado} · corte {fecha} · {frecuente:,.2f} · base {base}"
        )
    conexion.close()

    # Alcance declarado junto al numero, no en una nota al pie.
    exigir("Mayoreo en" in texto, "el boletin no declara el alcance del dato")
    exigir(
        re.search(r"precio por kilogramo|precio por presentacion comercial", texto),
        "el boletin no declara la base del precio",
    )
    exigir("no es precio en finca" in texto, "el boletin no declara que no es precio en finca")
    exigir("Consulta de origen:" in texto, "el boletin no cita la consulta de origen")

    # Si el corte no es del dia, tiene que decirlo en el cuerpo y no esconderlo.
    cortes = {traza["fecha_dato"] for traza in trazas}
    if cortes != {objetivo}:
        exigir(
            "no de hoy" in texto or "dias distintos" in texto,
            "el corte no es de hoy y el boletin no lo advierte",
        )
        detalles.append(f"cortes usados: {sorted(cortes)} · advertencia presente")

    detalles.append(f"trazas verificadas contra la base: {len(trazas)}")
    return detalles


if __name__ == "__main__":
    lector = argparse.ArgumentParser(description="Verifica el boletin del dia")
    lector.add_argument("--dia", default="hoy")
    lector.add_argument("--boletin", default=ruta("boletin", "ultimo.md"))
    argumentos = lector.parse_args()
    sys.exit(gate_util.correr(lambda: verificar(argumentos.dia, argumentos.boletin), MARCADOR))
