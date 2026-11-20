"""Arma el boletin diario de un cultivo y una plaza, desde la base de la pista B.

POR QUE ASI. El boletin no se escribe a mano. Cada numero sale de una fila de la
base, con su identificador anotado en el bloque de trazas del final, para que un
verificador pueda seguirlo hasta la ingesta. Un boletin escrito a mano es un
boletin que nadie puede auditar, y el primer numero inventado quema la
credibilidad del producto entero.

QUE DICE Y QUE NO. Dice mayoreo en plaza de destino, con la base del precio
pegada al numero, porque el SNIIM cotiza por kilogramo calculado y la Central de
Abasto por presentacion comercial. No promete precio en finca: lo que el
productor cobra esta por debajo de esto, y eso se dice con todas sus letras.

Uso:
  python boletin/generar.py
  python boletin/generar.py --producto "Limon c/semilla # 5" --plaza morelia
"""
import argparse
import json
import os
import sys
from datetime import date, datetime

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "ingesta"))

from comun import conectar  # noqa: E402

CARPETA = os.path.join(RAIZ, "boletin")

PLAZAS = {
    "morelia": "Michoacan: Mercado de Abasto de Morelia",
    "iztapalapa": "DF: Central de Abasto de Iztapalapa DF",
    "iztapalapa_ficeda": "DF: Central de Abasto de Iztapalapa (FICEDA)",
}

MESES = (
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
)

BASES = {
    "kilogramo": "por kilogramo",
    "presentacion": "por presentacion comercial completa",
    "": "con base de precio no declarada",
}


def en_letras(iso):
    momento = datetime.strptime(iso, "%Y-%m-%d").date()
    return f"{momento.day} de {MESES[momento.month - 1]} de {momento.year}"


def pesos(valor):
    return "sin dato" if valor is None else f"{valor:,.2f}"


def ultima_fila(conexion, producto, mercado):
    return conexion.execute(
        """
        SELECT p.id, p.fecha_dato, p.producto, p.presentacion, p.origen, p.calidad,
               p.precio_min, p.precio_max, p.precio_frec, p.base_precio, p.fuente,
               p.consulta_url, f.atribucion,
               d.mediana_frec_7d, d.variacion_pct_1d, d.amplitud_rel, d.n_obs_7d
        FROM precios p
        JOIN fuentes f ON f.clave = p.fuente
        LEFT JOIN derivados d ON d.fuente = p.fuente AND d.producto = p.producto
             AND d.mercado = p.mercado AND d.fecha_dato = p.fecha_dato
        WHERE p.producto = ? AND p.mercado = ? AND p.precio_frec IS NOT NULL
        ORDER BY p.fecha_dato DESC, p.id DESC
        LIMIT 1
        """,
        (producto, mercado),
    ).fetchone()


def generar(producto, plaza, contraste, ruta_base=None):
    conexion = conectar(ruta_base)
    principal = ultima_fila(conexion, producto, plaza)
    if principal is None:
        conexion.close()
        raise SystemExit(f"no hay ninguna fila de {producto} en {plaza}")
    otra = ultima_fila(conexion, producto, contraste) if contraste else None
    conexion.close()

    (
        id_fila, fecha, nombre, presentacion, origen, calidad,
        minimo, maximo, frecuente, base, fuente, consulta, atribucion,
        mediana, variacion, amplitud, n_obs,
    ) = principal

    hoy = date.today().isoformat()
    trazas = [
        {
            "id": id_fila,
            "fuente": fuente,
            "fecha_dato": fecha,
            "precio_frec": frecuente,
            "consulta_url": consulta,
        }
    ]

    lineas = [
        f"# {nombre} en {plaza.split(':')[-1].strip()}",
        "",
        f"Boletin del {en_letras(hoy)}.",
        "",
    ]

    if fecha != hoy:
        lineas.append(
            f"**El corte mas reciente publicado es del {en_letras(fecha)}, no de hoy.** "
            "La fuente no habia publicado el dato de hoy cuando se armo este boletin."
        )
    else:
        lineas.append(f"Corte del {en_letras(fecha)}.")
    lineas.append("")

    lineas += [
        f"Mayoreo en {plaza}, precio {BASES.get(base, BASES[''])}, "
        f"calidad {calidad.lower() or 'sin declarar'}, presentacion {presentacion.lower()}, "
        f"origen {origen}.",
        "",
        f"- Frecuente: **{pesos(frecuente)} pesos**",
        f"- Rango del dia: {pesos(minimo)} a {pesos(maximo)}",
    ]
    if mediana is not None:
        lineas.append(
            f"- Mediana de los ultimos {n_obs} dias publicados: {pesos(mediana)} "
            "(calculo nuestro, no es dato de la fuente)"
        )
    if variacion is not None:
        if abs(variacion) < 0.005:
            lineas.append("- Contra el dia publicado anterior: sin cambio")
        else:
            rumbo = "arriba" if variacion > 0 else "abajo"
            lineas.append(f"- Contra el dia publicado anterior: {abs(variacion):.2f} por ciento {rumbo}")
    if amplitud is not None:
        lineas.append(
            f"- Amplitud del dia: {amplitud * 100:.0f} por ciento del precio frecuente, "
            "que es lo que el numero unico no alcanza a describir"
        )
    lineas.append("")

    if otra is not None:
        (
            id_otra, fecha_otra, _n2, _p2, _o2, _c2,
            _min2, _max2, frec_otra, base_otra, fuente_otra, consulta_otra, atribucion_otra,
            *_resto,
        ) = otra
        trazas.append(
            {
                "id": id_otra,
                "fuente": fuente_otra,
                "fecha_dato": fecha_otra,
                "precio_frec": frec_otra,
                "consulta_url": consulta_otra,
            }
        )
        lineas.append("## A donde va la fruta")
        lineas.append("")
        if base_otra == base and frecuente:
            brecha = frec_otra - frecuente
            porcentaje = brecha / frecuente * 100
            rumbo = "arriba" if brecha >= 0 else "abajo"
            lineas.append(
                f"En {contraste} el mismo producto se paga **{pesos(frec_otra)} pesos** "
                f"{BASES.get(base_otra, BASES[''])}, corte del {en_letras(fecha_otra)}. "
                f"Son {pesos(abs(brecha))} pesos {rumbo}, es decir {abs(porcentaje):.1f} por ciento "
                "de diferencia entre las dos plazas."
            )
            if fecha_otra != fecha:
                lineas.append("")
                lineas.append(
                    "Cuidado al leer esa diferencia: las dos cifras son de dias distintos, "
                    f"{en_letras(fecha)} contra {en_letras(fecha_otra)}, asi que incluye tambien "
                    "lo que se movio el precio de un dia al otro."
                )
        else:
            lineas.append(
                f"En {contraste} se paga {pesos(frec_otra)} pesos "
                f"{BASES.get(base_otra, BASES[''])}, corte del {en_letras(fecha_otra)}. "
                "Las dos plazas no cotizan sobre la misma base, asi que la diferencia no se "
                "resta directo y aqui no se presenta como si se pudiera."
            )
        lineas.append("")
        if atribucion_otra not in atribucion:
            lineas.append(f"{atribucion_otra}.")
            lineas.append("")

    lineas += [
        "## Lo que este numero no es",
        "",
        "Esto es precio de mayoreo en la plaza, que no es precio en finca. Es lo que se paga "
        "en el mercado de destino, no lo que recibe quien cosecha: entre una cosa y la otra "
        "estan el flete, la merma y el margen de quien compra. Sirve como referencia para "
        "negociar, no como el precio que a usted le toca.",
        "",
        "Si usted vende en origen y quiere que su precio entre a este boletin, respondalo con "
        "su producto, su precio y su plaza. Consultarlo es y seguira siendo gratis.",
        "",
        "## De donde sale el dato",
        "",
        f"{atribucion}.",
        "",
        f"Consulta de origen: {consulta}",
        "",
        "<!-- trazas: " + json.dumps(trazas, ensure_ascii=False) + " -->",
        "",
    ]

    texto = "\n".join(lineas)
    os.makedirs(CARPETA, exist_ok=True)
    marca = nombre.lower().replace(" ", "_").replace("/", "-")
    destino = os.path.join(CARPETA, f"{hoy}_{marca}.md")
    for ruta in (destino, os.path.join(CARPETA, "ultimo.md")):
        with open(ruta, "w", encoding="utf-8") as archivo:
            archivo.write(texto)
    return destino, len(trazas)


if __name__ == "__main__":
    lector = argparse.ArgumentParser(description="Genera el boletin diario")
    lector.add_argument("--producto", default="Aguacate Hass")
    lector.add_argument("--plaza", default="morelia")
    lector.add_argument("--contraste", default="iztapalapa")
    lector.add_argument("--base")
    argumentos = lector.parse_args()
    ruta_escrita, trazas_escritas = generar(
        argumentos.producto,
        PLAZAS.get(argumentos.plaza, argumentos.plaza),
        PLAZAS.get(argumentos.contraste, argumentos.contraste),
        argumentos.base,
    )
    print(f"boletin escrito en {ruta_escrita} · {trazas_escritas} trazas")
