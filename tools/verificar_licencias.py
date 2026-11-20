"""B9 · toda fuente integrada tiene ficha con veredicto y cita legal.

Es la regla de la casa hecha gate: licencia verificada por fuente antes de
integrar, con la cita del texto que lo respalda, y ninguna fuente en rojo
escribiendo en la base.
"""
import os
import re
import sys

import gate_util
from gate_util import exigir, ruta

MARCADOR = "licencias verificadas · sin fuente integrada en rojo ni sin ficha"

CITA = re.compile(r"art[íi]culo\s+\d+|LFDA|Ley Federal del Derecho de Autor|CC[- ]BY", re.I)


def verificar():
    import comun

    detalles = []
    conexion = comun.conectar()
    integradas = [fila[0] for fila in conexion.execute("SELECT DISTINCT fuente FROM precios")]
    exigir(integradas, "no hay ninguna fuente integrada: un verde aqui no probaria nada")

    catalogo = {
        fila[0]: {"veredicto": fila[1], "ficha": fila[2], "atribucion": fila[3]}
        for fila in conexion.execute(
            "SELECT clave, licencia_veredicto, licencia_ficha, atribucion FROM fuentes"
        )
    }
    conexion.close()

    for clave in integradas:
        exigir(clave in catalogo, f"{clave} escribe en la base y no esta en el catalogo de fuentes")
        datos = catalogo[clave]
        exigir(
            datos["veredicto"] != "rojo",
            f"{clave} esta en rojo y tiene filas en la base: eso es exactamente lo que la regla prohibe",
        )
        camino = ruta(*datos["ficha"].split("/"))
        exigir(os.path.exists(camino), f"falta la ficha de licencia de {clave} en {datos['ficha']}")
        with open(camino, encoding="utf-8") as archivo:
            ficha = archivo.read()
        exigir(
            re.search(rf"veredicto:\*\*\s*{datos['veredicto']}", ficha, re.I)
            or re.search(rf"veredicto\s*:?\s*\*?\*?\s*{datos['veredicto']}", ficha, re.I),
            f"la ficha de {clave} no declara el veredicto {datos['veredicto']} que usa la ingesta",
        )
        exigir(CITA.search(ficha), f"la ficha de {clave} no cita ningun texto legal")
        exigir(
            datos["atribucion"] in ficha,
            f"la ficha de {clave} no registra la atribucion exacta que publica la pagina",
        )
        exigir(
            re.search(r"fecha de la verificacion|fecha de la verificaci[óo]n", ficha, re.I),
            f"la ficha de {clave} no tiene fecha de verificacion",
        )
        detalles.append(
            f"{clave}: veredicto {datos['veredicto']} · ficha {datos['ficha']} con cita legal y atribucion"
        )

    # Las fuentes prohibidas del expediente no deben estar ni en el catalogo.
    prohibidas = ("GCMA", "FACEBOOK", "WHATSAPP_GRUPO")
    for prohibida in prohibidas:
        exigir(
            prohibida not in catalogo,
            f"{prohibida} esta en el catalogo de fuentes y su veredicto investigado es rojo",
        )
    detalles.append("ninguna de las fuentes en rojo del expediente esta en el catalogo")
    return detalles


if __name__ == "__main__":
    sys.exit(gate_util.correr(verificar, MARCADOR))
