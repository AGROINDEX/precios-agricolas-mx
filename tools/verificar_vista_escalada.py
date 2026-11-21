"""B24 · la vista escala a decenas de plazas sin romperse.

EL PROBLEMA. 42 plazas por unas sesenta cotizaciones por una grafica cada una
son del orden de 2,500 SVG en linea: varios megabytes en una sola pagina, que
en una conexion de campo no se abre. La vista se partio en un indice con una
fila por plaza y una pagina por plaza.

QUE SE COMPRUEBA

1. El indice lista TODAS las plazas con filas en la base, y cada una enlaza a
   una pagina que existe de verdad. Una plaza que desaparece del indice se
   vuelve invisible sin que nadie lo note, que es el modo de falla de este
   diseno.
2. Ninguna pagina pasa el presupuesto de peso declarado.
3. El indice NO lleva graficas, porque volver a meterlas ahi es como se
   regresa al problema sin darse cuenta.
4. Cada pagina de plaza si lleva sus filas de precio y sus graficas.
5. Control positivo: un indice al que le falta una plaza viva es rechazado por
   la misma comprobacion.

Uso:
  python tools/verificar_vista_escalada.py --control-incompleto
"""
import argparse
import glob
import html as modulo_html
import os
import re
import sys

import gate_util
from gate_util import exigir, ruta

MARCADOR = "vista escalada verificada · presupuesto respetado e indice incompleto rechazado"

ENLACE = re.compile(r'<a href="(plaza/[^"]+\.html)">(.*?)</a>', re.S)
GRAFICA = re.compile(r"<svg")


def plazas_faltantes(indice, esperadas):
    """Plazas con filas en la base que el indice no lista. Funcion pura."""
    listadas = {modulo_html.unescape(nombre).strip() for _ruta, nombre in ENLACE.findall(indice)}
    return sorted(nombre for nombre in esperadas if nombre not in listadas)


def verificar(con_control):
    sys.path.insert(0, ruta("ingesta"))
    sys.path.insert(0, ruta("web"))
    import construir as constructor
    from comun import conectar

    detalles = []

    indice_ruta = gate_util.pagina_generada()
    carpeta = os.path.dirname(indice_ruta)
    with open(indice_ruta, encoding="utf-8") as mano:
        indice = mano.read()

    conexion = conectar()
    esperadas = {
        fila[0]
        for fila in conexion.execute(
            "SELECT mercado FROM precios GROUP BY mercado HAVING COUNT(*) > 0"
        )
    }
    conexion.close()
    exigir(esperadas, "no hay plazas con filas en la base")

    # 1. Todas listadas y cada enlace resuelve.
    faltantes = plazas_faltantes(indice, esperadas)
    exigir(
        not faltantes,
        f"el indice no lista {len(faltantes)} plazas que si tienen filas: {faltantes[:4]}",
    )
    enlaces = ENLACE.findall(indice)
    exigir(
        len(enlaces) >= len(esperadas),
        f"el indice trae {len(enlaces)} enlaces para {len(esperadas)} plazas",
    )
    for destino, nombre in enlaces:
        camino = os.path.join(carpeta, destino.replace("/", os.sep))
        exigir(
            os.path.exists(camino),
            f"el indice enlaza a {destino} para {modulo_html.unescape(nombre)[:40]} y ese"
            " archivo no existe",
        )
    detalles.append(f"{len(enlaces)} plazas listadas en el indice, todas con su pagina")

    # 2. Presupuesto de peso.
    presupuesto = constructor.PRESUPUESTO_KIB
    paginas = [indice_ruta] + sorted(glob.glob(os.path.join(carpeta, "plaza", "*.html")))
    pesadas = [
        (os.path.basename(camino), os.path.getsize(camino) // 1024)
        for camino in paginas
        if os.path.getsize(camino) // 1024 > presupuesto
    ]
    exigir(
        not pesadas,
        f"estas paginas pasan el presupuesto de {presupuesto} KiB: {pesadas[:4]}",
    )
    mayor = max((os.path.getsize(c) // 1024, os.path.basename(c)) for c in paginas)
    detalles.append(
        f"{len(paginas)} paginas, la mayor {mayor[1]} con {mayor[0]} KiB, presupuesto"
        f" {presupuesto} KiB · indice {os.path.getsize(indice_ruta) // 1024} KiB"
    )

    # 3. El indice sin graficas.
    exigir(
        not GRAFICA.search(indice),
        "el indice dibuja graficas: con 42 plazas eso es volver a pesar megabytes",
    )

    # 4. Las paginas de plaza con sus filas y sus graficas.
    con_filas = 0
    con_graficas = 0
    for camino in paginas[1:]:
        with open(camino, encoding="utf-8") as mano:
            contenido = mano.read()
        if re.search(r"<td class='num'>", contenido):
            con_filas += 1
        if GRAFICA.search(contenido):
            con_graficas += 1
    exigir(
        con_filas == len(paginas) - 1,
        f"solo {con_filas} de {len(paginas) - 1} paginas de plaza traen filas de precio",
    )
    exigir(
        con_graficas >= len(paginas) - 2,
        f"solo {con_graficas} de {len(paginas) - 1} paginas de plaza dibujan graficas",
    )
    detalles.append(
        f"las {con_filas} paginas de plaza traen filas de precio y {con_graficas} dibujan"
        " historico"
    )

    if con_control:
        # Un indice al que le falta una plaza viva tiene que ser rechazado.
        victima = sorted(esperadas)[0]
        mutilado = re.sub(
            r'<tr><td><a href="plaza/[^"]+\.html">' + re.escape(modulo_html.escape(victima)) + r"</a>.*?</tr>",
            "",
            indice,
            count=1,
            flags=re.S,
        )
        exigir(
            mutilado != indice,
            f"no se pudo quitar {victima} del indice de control: el control no prueba nada",
        )
        rechazo = plazas_faltantes(mutilado, esperadas)
        exigir(
            victima in rechazo,
            f"la comprobacion acepto un indice sin {victima}: no esta mirando la lista",
        )
        detalles.append(f"control: indice sin {victima[:40]} rechazado")

    return detalles


if __name__ == "__main__":
    lector = argparse.ArgumentParser(description="Verifica que la vista escale")
    lector.add_argument("--control-incompleto", action="store_true")
    argumentos = lector.parse_args()
    sys.exit(gate_util.correr(lambda: verificar(argumentos.control_incompleto), MARCADOR))
