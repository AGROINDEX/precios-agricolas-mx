"""Vigilante de reaparicion: avisa el dia en que una plaza muerta vuelve.

POR QUE ESTE VIGILANTE INTERRUMPE CON UNA BUENA NOTICIA. Rojo en CI es lo unico
que GitHub notifica, y este flujo no despliega nada, asi que ponerlo en rojo no
deja el tablero sin actualizar. Una plaza que vuelve despues de un ano es una
noticia que hay que atender el mismo dia: hay que promoverla al piloto normal,
medir su cadencia nueva, y rellenar su ventana. Por eso sale en rojo, y el
mensaje lo dice con todas sus letras para que nadie lo lea como una falla.

POR QUE NO GRITA MIENTRAS SIGUE MUERTA. Es la regla de la casa, la misma del
aviso de plaza quieta: lo que interrumpe es la transicion, no el estado. Una
plaza muerta conocida se reporta como nota en cada corrida, con los intentos
acumulados, y eso basta para saber que la vigilancia esta viva.

COMO SABE QUE VOLVIO. No lo deduce de la base, porque una plaza muerta no tiene
ni una fila ahi. Lo lee del registro de intentos, `_sondas.json`, que la ingesta
escribe en cada corrida.

CODIGOS DE SALIDA
  1  alguna plaza vigilada volvio a traer filas
  0  todas siguen muertas, o nunca se han vigilado

Uso:
  python ingesta/check_reaparicion.py
  python ingesta/check_reaparicion.py --sondas fixtures/pista_b/sondas_reaparicion.json
"""
import argparse
import sys

import comun_bootstrap  # noqa: F401
from sondas import leer

for _flujo in (sys.stdout, sys.stderr):
    try:
        _flujo.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass


def evaluar(datos):
    """Devuelve (reaparecidas, muertas, sin_vigilar)."""
    reaparecidas, muertas, sin_vigilar = [], [], []
    for registro in sorted(datos.get("plazas", {}).values(), key=lambda r: r["nombre"]):
        if registro["intentos"] == 0:
            sin_vigilar.append(registro)
        elif registro["filas_ultimo_intento"] > 0:
            reaparecidas.append(registro)
        else:
            muertas.append(registro)
    return reaparecidas, muertas, sin_vigilar


def main():
    lector = argparse.ArgumentParser(description="Avisa cuando una plaza muerta reaparece")
    lector.add_argument("--sondas")
    argumentos = lector.parse_args()

    datos = leer(argumentos.sondas)
    reaparecidas, muertas, sin_vigilar = evaluar(datos)

    if not datos.get("plazas"):
        print("no hay ninguna plaza en vigilancia de reaparicion")
        return 0

    for r in muertas:
        print(
            f"::notice::plaza muerta en vigilancia {r['nombre']} · "
            f"{r['intentos_sin_filas']} intentos seguidos sin filas de {r['intentos']} "
            f"totales · ultimo intento {r['ultimo_intento']}"
        )
    for r in sin_vigilar:
        print(f"ok      {r['nombre']} · registrada y todavia sin intentos")
    for r in reaparecidas:
        print(
            f"::error::REAPARECIO la plaza {r['nombre']} · su ultimo intento trajo "
            f"{r['filas_ultimo_intento']} filas despues de {r['intentos']} intentos de "
            f"vigilancia. Esto NO es una falla: es la noticia que esta vigilancia existe "
            f"para dar. Lo que toca es promoverla al piloto normal, medir su cadencia "
            f"nueva y rellenar su ventana declarada."
        )

    if reaparecidas:
        print(f"PLAZAS QUE REAPARECIERON: {len(reaparecidas)}")
        return 1
    print(
        f"vigilancia de reaparicion al dia · {len(muertas)} plazas siguen muertas · "
        f"{len(sin_vigilar)} sin intentos todavia"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
