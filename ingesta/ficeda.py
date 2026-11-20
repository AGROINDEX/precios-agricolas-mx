"""Ingesta incremental del visor de mayoreo de la Central de Abasto de la CDMX.

QUE ENTREGA. `visor_mayoreo.php` devuelve HTML renderizado en servidor con
cuatro tablas, una por categoria: abarrotes, hortalizas, frutas de temporada y
frutas. Cada fila trae su propia fecha, que es la del corte publicado, no la de
la descarga, y por eso la frescura se mide con esa fecha y no con el momento en
que corrio el fetcher.

SIN HTTPS. El visor se sirve por HTTP en un puerto no estandar. No se envia
ningun dato propio en la peticion, solo un GET, asi que no hay secreto que
proteger, pero queda anotado en la ficha de licencia como riesgo de integridad:
un intermediario podria alterar la respuesta y no habria forma de notarlo.

Uso:
  python ingesta/ficeda.py
  python ingesta/ficeda.py --base otra.db
"""
import argparse
import re
import sys

import comun_bootstrap  # noqa: F401
from comun import ahora, anotar_fetch, conectar, guardar, numero, podar, traer

CLAVE = "FICEDA_CDMX"
MERCADO = "DF: Central de Abasto de Iztapalapa (FICEDA)"
ENCABEZADO = ("producto", "calidad", "presentacion", "origen")


def limpiar(fragmento):
    import html

    texto = html.unescape(re.sub(r"<[^>]+>", " ", fragmento))
    return re.sub(r"\s+", " ", texto.replace("\xa0", " ")).strip()


def plegar(texto):
    tabla = str.maketrans("áéíóúÁÉÍÓÚñÑüÜ", "aeiouAEIOUnNuU")
    return texto.translate(tabla).lower()


def categoria_previa(pagina, posicion):
    """Titulo mas cercano antes de la tabla, que es su categoria."""
    titulos = [
        (encontrado.start(), limpiar(encontrado.group(1)))
        for encontrado in re.finditer(r"<h\d[^>]*>(.*?)</h\d>", pagina, re.S | re.I)
    ]
    anteriores = [texto for inicio, texto in titulos if inicio < posicion and texto]
    if not anteriores:
        return None
    return anteriores[-1].replace("MAYOREO", "").strip().title() or None


def extraer(pagina, url, capturado_en):
    filas_salida = []
    for encontrado in re.finditer(r"<table.*?</table>", pagina, re.S | re.I):
        tabla = encontrado.group(0)
        filas = re.findall(r"<tr.*?</tr>", tabla, re.S | re.I)
        if len(filas) < 2:
            continue
        encabezado = [plegar(limpiar(c)) for c in re.findall(r"<t[dh].*?</t[dh]>", filas[0], re.S | re.I)]
        if len(encabezado) < 8 or tuple(encabezado[:4]) != ENCABEZADO:
            continue
        categoria = categoria_previa(pagina, encontrado.start())
        for fila in filas[1:]:
            celdas = [limpiar(c) for c in re.findall(r"<t[dh].*?</t[dh]>", fila, re.S | re.I)]
            if len(celdas) < 8 or not celdas[0]:
                continue
            fecha = celdas[7].strip()
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fecha):
                continue
            filas_salida.append(
                {
                    "fuente": CLAVE,
                    "fecha_dato": fecha,
                    "hora_dato": None,
                    "categoria": categoria,
                    "producto": celdas[0],
                    "calidad": celdas[1],
                    "presentacion": celdas[2],
                    "origen": celdas[3],
                    "mercado": MERCADO,
                    "observaciones": "",
                    "precio_min": numero(celdas[4]),
                    "precio_frec": numero(celdas[5]),
                    "precio_max": numero(celdas[6]),
                    "moneda": "MXN",
                    # El visor publica por presentacion comercial, no por kilo.
                    "base_precio": "presentacion",
                    "alcance": "mayoreo",
                    "consulta_url": url,
                    "capturado_en": capturado_en,
                }
            )
    return filas_salida


def correr(ruta_base=None, ruta_reporte=None):
    from comun import FUENTES

    url = FUENTES[CLAVE]["url_base"]
    conexion = conectar(ruta_base)
    capturado_en = ahora()
    error = None
    filas = []
    try:
        pagina = traer(url)
        filas = extraer(pagina, url, capturado_en)
    except Exception as fallo:  # noqa: BLE001
        error = f"{type(fallo).__name__} {fallo}"
    nuevas, repetidas = guardar(conexion, filas) if filas else (0, 0)
    podadas = podar(conexion, CLAVE)
    fechas = sorted({fila["fecha_dato"] for fila in filas})
    conexion.close()

    exito = bool(filas) and error is None
    detalle = error or f"{len(filas)} filas, {nuevas} nuevas, {repetidas} repetidas, corte {fechas[-1] if fechas else 'sin fecha'}"
    anotar_fetch(CLAVE, exito, nuevas, detalle, ruta_reporte)
    print(f"FICEDA · {len(filas)} filas leidas · {nuevas} nuevas · {podadas} podadas · {detalle}")
    return 0 if exito else 1


if __name__ == "__main__":
    lector = argparse.ArgumentParser(description="Ingesta incremental de la Central de Abasto CDMX")
    lector.add_argument("--base")
    lector.add_argument("--reporte")
    argumentos = lector.parse_args()
    sys.exit(correr(argumentos.base, argumentos.reporte))
