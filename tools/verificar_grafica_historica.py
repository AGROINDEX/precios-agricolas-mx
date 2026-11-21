"""B16 · la grafica historica es la serie de la base, no un adorno.

QUE SE COMPRUEBA. Para cada producto dibujado se recalcula la serie cruda desde
`precios` y se compara contra los puntos del `<polyline>` de la pagina. La
comparacion es afin, no literal: la grafica escala y mueve los valores para
caber en su caja, asi que lo que tiene que coincidir es la FORMA. Si existe una
sola recta que lleve todos los valores recalculados a todas las coordenadas
dibujadas, la grafica es esa serie. Si no existe, la grafica es otra cosa.

POR QUE ASI Y NO COMPARANDO CADENAS. Comparar el texto del polyline contra uno
regenerado aqui solo probaria que dos copias del mismo codigo coinciden. La
prueba afin parte de las filas crudas y no usa el dibujante.

CONTROL NEGATIVO OBLIGATORIO. Con --control-desfasado se repite la prueba con
la serie corrida un dia. Si la pagina siguiera pasando, la comprobacion no
estaria mirando los datos, y el gate lo dice.

Uso:
  python tools/verificar_grafica_historica.py --control-desfasado
"""
import argparse
import os
import re
import sys

import gate_util
from gate_util import exigir, ruta

sys.path.insert(0, os.path.join(gate_util.RAIZ, "ingesta"))

from comun import conectar  # noqa: E402

MARCADOR = "grafica historica verificada · recalculo coincide y control desfasado rechazado"

TOLERANCIA = 0.25  # pixeles de holgura por punto, sobre cajas de 40 a 100 px de alto

PAGINA_A = ruta("diseno", "propuesta_a_terminal.html")

# Las maquetas son artefacto generado, igual que la pagina publicada: no se
# versionan. En un clon recien hecho no existen, y un gate que fallara por eso
# estaria midiendo el orden de los comandos y no el producto.
MODULOS = {
    "A terminal": "propuesta_a_terminal",
    "B mercado": "propuesta_b_mercado",
    "C la brecha": "propuesta_c_brecha",
}


def asegurar(nombre, camino):
    if os.path.exists(camino):
        return camino
    if nombre == "publicada":
        gate_util.pagina_generada()
        return camino
    sys.path.insert(0, ruta("diseno"))
    modulo = __import__(MODULOS[nombre])
    return modulo.construir()

# La vista publicada son el indice y una pagina por plaza. El indice no dibuja
# series a proposito: las graficas viven en la pagina de cada plaza, y exigirle
# al indice que dibuje seria pedirle volver a pesar varios megabytes.
PAGINAS = {
    "publicada": ruta("web", "plaza"),
    "A terminal": PAGINA_A,
    "B mercado": ruta("diseno", "propuesta_b_mercado.html"),
    "C la brecha": ruta("diseno", "propuesta_c_brecha.html"),
}

SECCION = re.compile(r"<h2>(.*?)</h2>(.*?)(?=<h2>|<footer)", re.S)
FILA = re.compile(
    r'<tr><td class="prod">(.*?)</td>'
    r'<td class="sec">(.*?)</td>'
    r'<td class="sec">(.*?)</td>'
    r'<td class="historia">(.*?)</td>',
    re.S,
)
PUNTOS = re.compile(r'<polyline class="linea" points="([^"]+)"')


def desescapar(texto):
    import html

    return html.unescape(texto).strip()


def serie_cruda(conexion, mercado, producto, presentacion):
    return [
        fila[0]
        for fila in conexion.execute(
            "SELECT precio_frec FROM precios WHERE mercado = ? AND producto = ?"
            " AND presentacion = ? AND precio_frec IS NOT NULL ORDER BY fecha_dato",
            (mercado, producto, presentacion),
        )
    ]


def coincide(valores, coordenadas):
    """Hay una sola recta que lleve cada valor a su coordenada dibujada."""
    if len(valores) != len(coordenadas):
        return False, f"{len(valores)} valores contra {len(coordenadas)} puntos dibujados"

    distintos = sorted({valor for valor in valores})
    if len(distintos) == 1:
        alturas = {round(y, 1) for y in coordenadas}
        if len(alturas) > 1:
            return False, "la serie no cambia y la grafica si"
        return True, "serie plana dibujada plana"

    # Dos puntos extremos definen la recta; el resto tiene que caer sobre ella.
    bajo, alto = distintos[0], distintos[-1]
    indice_bajo = valores.index(bajo)
    indice_alto = valores.index(alto)
    y_bajo, y_alto = coordenadas[indice_bajo], coordenadas[indice_alto]
    if y_bajo == y_alto:
        return False, "valores distintos dibujados a la misma altura"
    pendiente = (y_alto - y_bajo) / (alto - bajo)
    if pendiente >= 0:
        return False, "la grafica sube donde el precio baja"
    origen = y_bajo - pendiente * bajo
    peor = max(abs(pendiente * valor + origen - y) for valor, y in zip(valores, coordenadas))
    if peor > TOLERANCIA:
        return False, f"el punto peor queda a {peor:.2f} px de la serie recalculada"
    return True, f"{len(valores)} puntos sobre la serie, desvio maximo {peor:.2f} px"


def filas_de_la_pagina():
    with open(asegurar("A terminal", PAGINA_A), encoding="utf-8") as archivo:
        pagina = archivo.read()
    salida = []
    for mercado, cuerpo in SECCION.findall(pagina):
        for producto, presentacion, _origen, celda in FILA.findall(cuerpo):
            encontrados = PUNTOS.findall(celda)
            if not encontrados:
                continue
            coordenadas = [
                float(par.split(",")[1]) for par in encontrados[0].split()
            ]
            salida.append(
                (
                    desescapar(mercado),
                    desescapar(producto),
                    desescapar(presentacion),
                    coordenadas,
                )
            )
    return salida


def verificar(control):
    detalles = []

    for nombre, camino in PAGINAS.items():
        camino = asegurar(nombre, camino)
        exigir(os.path.exists(camino), f"falta la pagina {nombre}: {camino}")
        if os.path.isdir(camino):
            import glob

            archivos = sorted(glob.glob(os.path.join(camino, "*.html")))
            exigir(archivos, f"la carpeta {camino} no tiene ninguna pagina de plaza")
            contenido = ""
            for uno in archivos:
                with open(uno, encoding="utf-8") as archivo:
                    contenido += archivo.read()
        else:
            with open(camino, encoding="utf-8") as archivo:
                contenido = archivo.read()
        dibujadas = len(PUNTOS.findall(contenido))
        exigir(dibujadas > 0, f"la pagina {nombre} no dibuja ninguna serie historica")
        # Se prohibe la mediana movil POR PRODUCTO, que es la que el historico
        # viene a sustituir. Un resumen como "brecha mediana" entre productos es
        # otra cosa y no cae aqui.
        for sobra in ("Mediana 7d", "Mediana de 7 dias", "mediana_frec_7d"):
            exigir(
                sobra not in contenido,
                f"la pagina {nombre} sigue presentando la mediana movil por producto"
                f" ({sobra}) en lugar del historico",
            )
        detalles.append(
            f"{nombre}: {dibujadas} series dibujadas, sin mediana movil por producto"
        )

    filas = filas_de_la_pagina()
    exigir(len(filas) >= 20, f"solo se pudieron leer {len(filas)} graficas de la pagina A")

    conexion = conectar()
    revisadas, con_forma = 0, 0
    for mercado, producto, presentacion, coordenadas in filas:
        valores = serie_cruda(conexion, mercado, producto, presentacion)
        if len(valores) < 2:
            continue
        bien, motivo = coincide(valores, coordenadas)
        exigir(bien, f"{producto} en {mercado}: {motivo}")
        revisadas += 1
        if len({round(valor, 4) for valor in valores}) >= 3:
            con_forma += 1
    exigir(revisadas >= 20, f"solo {revisadas} graficas pudieron recalcularse desde la base")
    exigir(
        con_forma >= 5,
        f"solo {con_forma} series tienen tres valores distintos: con series planas la "
        "comprobacion no demuestra nada",
    )
    detalles.append(f"{revisadas} graficas recalculadas desde las filas crudas y coincidentes")

    if control:
        # La misma prueba con la serie corrida un dia. Tiene que fallar en casi
        # todas las que de verdad tienen forma.
        rechazadas, candidatas = 0, 0
        for mercado, producto, presentacion, coordenadas in filas:
            valores = serie_cruda(conexion, mercado, producto, presentacion)
            if len({round(valor, 4) for valor in valores}) < 3:
                continue
            candidatas += 1
            desfasada = valores[1:] + valores[:1]
            bien, _motivo = coincide(desfasada, coordenadas)
            if not bien:
                rechazadas += 1
        exigir(candidatas >= 5, "no hay suficientes series con forma para el control")
        exigir(
            rechazadas == candidatas,
            f"el control desfasado paso en {candidatas - rechazadas} de {candidatas} series: "
            "la comprobacion no esta mirando los datos",
        )
        detalles.append(
            f"control desfasado rechazado en las {candidatas} series con forma"
        )

    conexion.close()
    return detalles


if __name__ == "__main__":
    lector = argparse.ArgumentParser(description="Verifica la grafica historica")
    lector.add_argument("--control-desfasado", action="store_true")
    argumentos = lector.parse_args()
    sys.exit(gate_util.correr(lambda: verificar(argumentos.control_desfasado), MARCADOR))
