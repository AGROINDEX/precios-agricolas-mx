"""B11 · ningun texto de cara al usuario usa guion largo.

Gate negativo con control positivo obligatorio: el mismo verificador corre
contra un archivo que si lo usa y tiene que rechazarlo.

Uso:
  python tools/verificar_sin_guion_largo.py --rutas web --control-positivo fixtures/pista_b/texto_con_guion_largo.md
"""
import argparse
import os
import sys

import gate_util
from gate_util import exigir, ruta

MARCADOR = "tipografia verificada · control positivo rechazado como se esperaba"

# Guion largo y guion corto de rango: los dos se usan como el que el proyecto
# prohibe. El interpunto si se permite y no se busca.
PROHIBIDOS = ("—", "–", "&mdash;", "&ndash;", "&#8212;", "&#8211;")
EXTENSIONES = (".html", ".md", ".txt", ".py")


def ofensas(texto):
    return [simbolo for simbolo in PROHIBIDOS if simbolo in texto]


def recorrer(rutas):
    archivos = []
    for relativa in rutas:
        camino = ruta(*relativa.split("/"))
        if os.path.isfile(camino):
            archivos.append(camino)
            continue
        if not os.path.isdir(camino):
            raise gate_util.Fallo(f"la ruta declarada no existe: {relativa}")
        for raiz_actual, _carpetas, nombres in os.walk(camino):
            for nombre in nombres:
                if nombre.endswith(EXTENSIONES):
                    archivos.append(os.path.join(raiz_actual, nombre))
    return archivos


def verificar(rutas, control):
    detalles = []
    archivos = recorrer(rutas)
    exigir(archivos, f"las rutas {rutas} no contienen archivos de texto que revisar")

    sucios = []
    for camino in archivos:
        with open(camino, encoding="utf-8") as archivo:
            encontrados = ofensas(archivo.read())
        if encontrados:
            sucios.append((os.path.relpath(camino, gate_util.RAIZ), encontrados))
    exigir(not sucios, f"guion largo encontrado en: {sucios}")
    detalles.append(f"archivos revisados sin guion largo: {len(archivos)}")

    exigir(os.path.exists(control), f"no existe el control positivo en {control}")
    with open(control, encoding="utf-8") as archivo:
        encontrados = ofensas(archivo.read())
    exigir(
        encontrados,
        "el verificador no detecto el guion largo del control positivo: no sirve, y el verde"
        " de las rutas reales no prueba nada",
    )
    detalles.append(f"control positivo rechazado por {encontrados}")
    return detalles


if __name__ == "__main__":
    lector = argparse.ArgumentParser(description="Verifica la tipografia de cara al usuario")
    lector.add_argument("--rutas", required=True, help="lista separada por comas")
    lector.add_argument("--control-positivo", required=True)
    argumentos = lector.parse_args()
    sys.exit(
        gate_util.correr(
            lambda: verificar(argumentos.rutas.split(","), argumentos.control_positivo), MARCADOR
        )
    )
