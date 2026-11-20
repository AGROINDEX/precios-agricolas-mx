"""B8 · la pagina no dibuja velas, y el verificador si sabe detectarlas.

POR QUE EL GATE. Una vela afirma apertura, cierre, maximo y minimo de un periodo
de negociacion. El dato publicado no trae hora, ni volumen, ni calidad
homogenea: el minimo y el maximo del dia son el rango de cotizaciones
encuestadas en la plaza, no el recorrido de un precio de transaccion. Pintar
velas con eso es una afirmacion falsa, y un comprador profesional la detecta.

Gate negativo, asi que exige control positivo: el mismo verificador corre contra
una pagina que si trae velas y tiene que rechazarla.

Uso:
  python tools/verificar_sin_velas.py --control-positivo fixtures/pista_b/pagina_con_velas.html
"""
import argparse
import os
import re
import sys

import gate_util
from gate_util import exigir, ruta

MARCADOR = "ausencia de velas verificada · control positivo rechazado como se esperaba"
PAGINA = ruta("web", "index.html")

# Senales de grafica financiera. Se busca por nombre de tecnica y por libreria,
# porque cualquiera de las dos vias produce el mismo claim falso.
SENALES = (
    r"candlestick",
    r"candle[\s_-]?series",
    r"\bohlc\b",
    r"addCandlestick",
    r"lightweight-charts",
    r"\bapexcharts\b",
    r"highcharts",
    r"\bplotly\b",
    r"chart\.js",
    r"techan",
    r"\bvela(s)?\s+(de|japonesa)",
    r"grafica\s+de\s+velas",
    r"gr[áa]fica\s+de\s+velas",
)


def velas_en(texto):
    encontradas = []
    for senal in SENALES:
        for coincidencia in re.finditer(senal, texto, re.I):
            fragmento = texto[max(0, coincidencia.start() - 40) : coincidencia.end() + 40]
            encontradas.append((senal, " ".join(fragmento.split())))
            break
    return encontradas


def verificar(control):
    detalles = []
    exigir(os.path.exists(PAGINA), f"no existe la pagina en {PAGINA}")
    with open(PAGINA, encoding="utf-8") as archivo:
        pagina = archivo.read()

    # La mencion que explica por que NO hay velas no cuenta como vela. Se quita
    # esa frase antes de buscar, y se exige que siga estando.
    exigir(
        "Sin graficas de velas a proposito" in pagina,
        "la pagina no declara por que no usa velas",
    )
    cuerpo = pagina.replace(
        "Sin graficas de velas a proposito: el dato publicado no trae hora, volumen ni "
        "calidad homogenea que las sostengan.",
        "",
    )

    encontradas = velas_en(cuerpo)
    exigir(not encontradas, f"la pagina trae senales de velas: {encontradas}")

    exigir("<canvas" not in cuerpo.lower(), "la pagina trae un canvas, que es donde se dibujan")
    exigir(
        "<script" not in cuerpo.lower(),
        "la pagina trae script: la version estatica no lo necesita y es la via de una grafica",
    )
    detalles.append("pagina publicada sin senales de velas, sin canvas y sin script")

    # Control positivo.
    exigir(os.path.exists(control), f"no existe el control positivo en {control}")
    with open(control, encoding="utf-8") as archivo:
        infractora = archivo.read()
    senales_control = velas_en(infractora)
    exigir(
        senales_control,
        "el verificador no detecto velas en el control positivo: no sirve, y el verde de"
        " la pagina real no prueba nada",
    )
    detalles.append(
        f"control positivo rechazado por {len(senales_control)} senales, entre ellas"
        f" {senales_control[0][0]}"
    )
    return detalles


if __name__ == "__main__":
    lector = argparse.ArgumentParser(description="Verifica que no haya graficas de velas")
    lector.add_argument("--control-positivo", required=True)
    argumentos = lector.parse_args()
    sys.exit(gate_util.correr(lambda: verificar(argumentos.control_positivo), MARCADOR))
