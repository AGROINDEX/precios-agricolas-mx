"""Piezas de marcado compartidas por las propuestas."""
import html


def escapar(valor):
    return html.escape("" if valor is None else str(valor))


def pesos(valor, decimales=2):
    return "" if valor is None else f"{valor:,.{decimales}f}"


def rumbo(variacion):
    if variacion is None:
        return "", ""
    if variacion > 0.005:
        return "sube", f"+{variacion:.2f}%"
    if variacion < -0.005:
        return "baja", f"{variacion:.2f}%"
    return "quieto", "0.00%"


CABEZA = (
    '<!doctype html><html lang="es"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width, initial-scale=1">'
)


# La grafica vive en ingesta/grafica.py, compartida con la pagina publicada.
from grafica import ESTILO_GRAFICA, grafica  # noqa: E402,F401
