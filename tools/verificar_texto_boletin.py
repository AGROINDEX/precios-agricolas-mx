"""A2 · el boletin no promete precio en finca ni usa guion largo.

DOS REGLAS DISTINTAS. Decir "esto no es precio en finca" es obligatorio;
afirmar un precio en finca sobre un dato de mayoreo esta prohibido. Un buscador
ingenuo de la frase "precio en finca" castigaria el descargo honesto y dejaria
pasar la mentira, asi que lo que se busca es la AFIRMACION: un precio en finca
con numero, con verbo de afirmacion o presentado como garantizado.

Se agrega una tercera regla, que es la misma disciplina: no prometer el futuro.
Un boletin de referencia no dice si conviene vender manana.

Gate negativo, asi que trae control positivo obligatorio.

Uso:
  python tools/verificar_texto_boletin.py --boletin boletin/ultimo.md \
      --control-positivo fixtures/pista_a/boletin_infractor.md
"""
import argparse
import os
import re
import sys

import gate_util
from gate_util import exigir, ruta

MARCADOR = "texto verificado · control positivo rechazado como se esperaba"

GUIONES = ("—", "–", "&mdash;", "&ndash;")

# Afirmaciones de precio en finca. Cada patron describe una manera concreta de
# afirmarlo, no la simple aparicion de las palabras.
AFIRMACIONES = (
    (r"precio\s+en\s+finca(?:\s+(?:de\s+)?hoy)?\s*[:=]\s*\$?\s*\d", "precio en finca con cifra"),
    (r"precio\s+en\s+finca\s+(?:es|era|sera|fue|anda|esta|ronda)\b", "precio en finca afirmado con verbo"),
    (r"precio\s+en\s+finca\s+de\s+\$?\s*\d", "precio en finca con monto"),
    (r"precio\s+en\s+finca\b[^.]{0,40}?\b(?:subio|bajo|aumento|cayo|se\s+movio)", "movimiento del precio en finca"),
    (r"en\s+finca\s+(?:se\s+paga|le\s+pagan|pagan)\b", "pago en finca afirmado"),
    (r"\bprecio\s+al\s+productor\s*[:=]\s*\$?\s*\d", "precio al productor con cifra"),
    (r"garantizado", "precio presentado como garantizado"),
)

PRONOSTICOS = (
    (r"\bva\s+a\s+(?:subir|bajar)\b", "pronostico de precio"),
    (r"\bseguira\s+(?:subiendo|bajando)\b", "pronostico de precio"),
    (r"\bconviene\s+vender\b", "recomendacion de venta"),
    (r"\bes\s+la\s+decision\s+correcta\b", "recomendacion de venta"),
)

DESCARGO = "no es precio en finca"


def plegar(texto):
    tabla = str.maketrans("áéíóúÁÉÍÓÚñÑüÜ", "aeiouAEIOUnNuU")
    return texto.translate(tabla).lower()


def faltas(texto):
    plano = plegar(texto)
    encontradas = []
    for patron, etiqueta in AFIRMACIONES + PRONOSTICOS:
        coincidencia = re.search(patron, plano)
        if coincidencia:
            encontradas.append((etiqueta, " ".join(plano[max(0, coincidencia.start() - 30): coincidencia.end() + 30].split())))
    for guion in GUIONES:
        if guion in texto:
            encontradas.append(("guion largo", guion))
    return encontradas


def verificar(camino, control):
    detalles = []
    exigir(os.path.exists(camino), f"no existe el boletin en {camino}")
    with open(camino, encoding="utf-8") as archivo:
        boletin = archivo.read()

    encontradas = faltas(boletin)
    exigir(not encontradas, f"el boletin comete faltas: {encontradas}")
    exigir(DESCARGO in plegar(boletin), "el boletin no trae el descargo de que no es precio en finca")
    detalles.append("boletin sin afirmacion de precio en finca, sin pronostico y sin guion largo")

    exigir(os.path.exists(control), f"no existe el control positivo en {control}")
    with open(control, encoding="utf-8") as archivo:
        infractor = archivo.read()
    faltas_control = faltas(infractor)
    exigir(
        faltas_control,
        "el verificador no detecto nada en el control positivo: no sirve, y el verde del"
        " boletin real no prueba nada",
    )
    etiquetas = sorted({etiqueta for etiqueta, _fragmento in faltas_control})
    # Las dos reglas del gate tienen que dispararse por separado: la del guion
    # largo y, sobre todo, la de afirmar precio en finca. Un control que solo
    # dispara la tipografia dejaria sin probar la regla que de verdad importa.
    exigir("guion largo" in etiquetas, "el control positivo no disparo la regla del guion largo")
    exigir(
        any("finca" in etiqueta or "productor" in etiqueta for etiqueta in etiquetas),
        f"el control positivo no disparo ninguna regla de precio en finca: {etiquetas}",
    )
    detalles.append(f"control positivo rechazado por {etiquetas}")
    return detalles


if __name__ == "__main__":
    lector = argparse.ArgumentParser(description="Verifica el texto del boletin")
    lector.add_argument("--boletin", default=ruta("boletin", "ultimo.md"))
    lector.add_argument("--control-positivo", required=True)
    argumentos = lector.parse_args()
    sys.exit(
        gate_util.correr(
            lambda: verificar(argumentos.boletin, argumentos.control_positivo), MARCADOR
        )
    )
