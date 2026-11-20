"""Aviso de plaza quieta: avisa cuando una plaza DEJA de moverse.

POR QUE AVISA DEL CAMBIO Y NO DEL ESTADO. Es la misma leccion que dejo el
fetcher roto diecinueve dias en AgroPatentIndex: una alerta que sale en todas
las corridas es una alerta que nadie mira. Morelia esta quieta hoy y lo va a
estar manana; fallar todos los dias por eso entrena a cualquiera a ignorar el
vigilante. Lo que si merece interrumpir a alguien es el dia en que una plaza que
se movia deja de moverse, porque ahi probablemente se rompio algo.

COMO SABE COMO ESTABA ANTES, SIN GUARDAR ESTADO. No hay archivo de memoria que
mantener: se vuelve a medir la misma plaza recortando la base al dia publicado
anterior y se comparan los dos veredictos. La base es su propia memoria, y el
resultado es reproducible: cualquiera puede recalcular el aviso de ayer.

CODIGOS DE SALIDA
  1  alguna plaza empeoro respecto del dia publicado anterior
  0  todo igual, o alguna plaza se recupero

Uso:
  python ingesta/check_plazas_quietas.py
  python ingesta/check_plazas_quietas.py --base otra.db
"""
import argparse
import sys

import comun_bootstrap  # noqa: F401
from comun import conectar
from frescura_real import VEREDICTOS, frase, medir

for _flujo in (sys.stdout, sys.stderr):
    try:
        _flujo.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

# De mejor a peor. Empeorar es bajar en esta escala.
ORDEN = {"viva": 3, "parcial": 2, "estancada": 1, "sin_medir": 0}


def fecha_anterior(conexion, fuente, mercado):
    fechas = [
        fila[0]
        for fila in conexion.execute(
            "SELECT DISTINCT fecha_dato FROM precios WHERE fuente = ? AND mercado = ?"
            " AND precio_frec IS NOT NULL ORDER BY fecha_dato DESC LIMIT 2",
            (fuente, mercado),
        )
    ]
    return fechas[1] if len(fechas) > 1 else None


def evaluar(conexion):
    """Devuelve (empeoraron, recuperadas, quietas_conocidas, sanas)."""
    hoy = medir(conexion)
    empeoraron, recuperadas, quietas, sanas = [], [], [], []

    for fuente, plazas in hoy.items():
        for mercado, medida in plazas.items():
            previa = fecha_anterior(conexion, fuente, mercado)
            antes = None
            if previa:
                medidas_previas = medir(conexion, previa)
                antes = medidas_previas.get(fuente, {}).get(mercado, {}).get("veredicto")

            registro = {
                "fuente": fuente,
                "mercado": mercado,
                "antes": antes,
                "ahora": medida["veredicto"],
                "frase": frase(medida),
                "corte": medida["ultimo_corte"],
            }

            # Sin un dia anterior comparable no hay transicion que juzgar. Eso lo
            # cubre el vigilante de fuentes congeladas, que mira la descarga.
            if antes is None or medida["veredicto"] == "sin_medir" or antes == "sin_medir":
                sanas.append(registro)
                continue

            if ORDEN[medida["veredicto"]] < ORDEN[antes]:
                empeoraron.append(registro)
            elif ORDEN[medida["veredicto"]] > ORDEN[antes]:
                recuperadas.append(registro)
            elif medida["veredicto"] in ("estancada", "parcial"):
                quietas.append(registro)
            else:
                sanas.append(registro)
    return empeoraron, recuperadas, quietas, sanas


def main():
    lector = argparse.ArgumentParser(description="Avisa cuando una plaza deja de moverse")
    lector.add_argument("--base")
    argumentos = lector.parse_args()

    conexion = conectar(argumentos.base)
    empeoraron, recuperadas, quietas, sanas = evaluar(conexion)
    conexion.close()

    for registro in sanas:
        print(f"ok      {registro['mercado']} · {VEREDICTOS[registro['ahora']]}")
    for registro in recuperadas:
        print(
            f"mejora  {registro['mercado']} · paso de {VEREDICTOS[registro['antes']]} "
            f"a {VEREDICTOS[registro['ahora']]}"
        )
    for registro in quietas:
        # Estado conocido: se reporta, no interrumpe. Esta es la linea que evita
        # que el vigilante grite todos los dias lo mismo.
        print(
            f"::notice::plaza quieta conocida {registro['mercado']} · "
            f"{VEREDICTOS[registro['ahora']]} desde antes · {registro['frase']}"
        )
    for registro in empeoraron:
        print(
            f"::error::plaza dejo de moverse {registro['mercado']} · "
            f"paso de {VEREDICTOS[registro['antes']]} a {VEREDICTOS[registro['ahora']]} "
            f"en el corte del {registro['corte']} · {registro['frase']}"
        )

    if empeoraron:
        print(f"PLAZAS QUE EMPEORARON: {len(empeoraron)}")
        return 1
    print(
        f"movimiento verificado · {len(sanas)} plazas sin cambio de estado · "
        f"{len(quietas)} quietas conocidas · {len(recuperadas)} recuperadas"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
