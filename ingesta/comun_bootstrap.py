"""Pone la carpeta de la ingesta en el path, para correr los scripts sueltos.

Existe para que `python ingesta/sniim.py` y `python tools/verificar_x.py`
importen `comun` sin convertir el proyecto en paquete instalable, que seria
ceremonia para nada en un piloto.
"""
import os
import sys

CARPETA = os.path.dirname(os.path.abspath(__file__))
if CARPETA not in sys.path:
    sys.path.insert(0, CARPETA)
