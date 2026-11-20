"""Utilidades de los verificadores de gates.

Regla de la casa: el marcador de exito se imprime SOLO despues de que pasaron
todas las aserciones, y cualquier fallo sale con codigo distinto de cero. Un
marcador impreso antes de terminar convierte el gate en decorativo.
"""
import os
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

for _flujo in (sys.stdout, sys.stderr):
    try:
        _flujo.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

sys.path.insert(0, os.path.join(RAIZ, "ingesta"))


def ruta(*partes):
    return os.path.join(RAIZ, *partes)


def ruta_datos_a(nombre):
    """Registro de la pista A, con desvio opcional para el banco de pruebas.

    Por defecto apunta a los registros reales. `PRECIOS_DATOS_PISTA_A` solo lo
    usa `autoprueba_pista_a.py`, para demostrar que estos verificadores tambien
    saben ponerse en verde cuando el dato existe. Un verificador que solo sabe
    fallar no prueba nada.
    """
    carpeta = os.environ.get("PRECIOS_DATOS_PISTA_A") or os.path.join(RAIZ, "datos", "pista_a")
    return os.path.join(carpeta, nombre)


class Fallo(Exception):
    pass


def exigir(condicion, mensaje):
    if not condicion:
        raise Fallo(mensaje)


def correr(verificacion, marcador):
    """Ejecuta la verificacion y solo entonces imprime el marcador."""
    try:
        detalles = verificacion() or []
    except Fallo as fallo:
        print(f"FALLO · {fallo}")
        return 1
    except Exception as fallo:  # noqa: BLE001
        print(f"FALLO inesperado · {type(fallo).__name__}: {fallo}")
        return 1
    for linea in detalles:
        print(f"  {linea}")
    print(marcador)
    return 0
