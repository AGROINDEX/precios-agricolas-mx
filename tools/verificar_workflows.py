"""B10 · ingesta y vigilante corren en flujos separados.

La separacion no es estetica. El vigilante tiene que poder fallar, porque fallar
es como avisa, y si viviera en el flujo que despliega, una fuente congelada
dejaria el tablero sin actualizar justo el dia en que hay algo que avisar.
"""
import os
import re
import sys

import gate_util
from gate_util import exigir, ruta

MARCADOR = "workflows verificados · ingesta y vigilante en flujos separados"
CARPETA = ruta(".github", "workflows")

VIGILANTE = "check_fuentes_stale.py"
INGESTAS = ("ingesta/sniim.py", "ingesta/ficeda.py")
DESPLIEGUE = re.compile(r"git push|wrangler|cloudflare|pages deploy|actions/deploy", re.I)


def verificar():
    detalles = []
    exigir(os.path.isdir(CARPETA), f"no existe la carpeta de flujos en {CARPETA}")
    archivos = sorted(f for f in os.listdir(CARPETA) if f.endswith((".yml", ".yaml")))
    exigir(len(archivos) >= 2, f"hacen falta al menos dos flujos y hay {len(archivos)}")

    contenidos = {}
    for nombre in archivos:
        with open(os.path.join(CARPETA, nombre), encoding="utf-8") as archivo:
            contenidos[nombre] = archivo.read()

    flujos_vigilante = [n for n, c in contenidos.items() if VIGILANTE in c]
    flujos_ingesta = [n for n, c in contenidos.items() if any(i in c for i in INGESTAS)]
    exigir(flujos_vigilante, f"ningun flujo corre {VIGILANTE}")
    exigir(flujos_ingesta, "ningun flujo corre la ingesta")

    compartidos = set(flujos_vigilante) & set(flujos_ingesta)
    exigir(
        not compartidos,
        f"el vigilante y la ingesta viven en el mismo flujo: {sorted(compartidos)}",
    )
    detalles.append(f"ingesta en {flujos_ingesta} · vigilante en {flujos_vigilante}")

    for nombre in flujos_vigilante:
        exigir(
            not DESPLIEGUE.search(contenidos[nombre]),
            f"{nombre} corre el vigilante y tambien despliega: fallar dejaria el tablero sin actualizar",
        )
        exigir(
            "fetch_report_congelado.json" in contenidos[nombre],
            f"{nombre} no prueba el control positivo del vigilante antes de medir en vivo",
        )
    detalles.append("el flujo del vigilante no despliega y corre su control positivo")

    for nombre, contenido in contenidos.items():
        exigir("concurrency:" in contenido, f"{nombre} no declara concurrencia")
        exigir(re.search(r"group:\s*\S+", contenido), f"{nombre} declara concurrencia sin grupo")
        exigir("timeout-minutes:" in contenido, f"{nombre} no acota el tiempo de corrida")

    # La cadencia diaria se le exige a los flujos que miden el mundo, que son la
    # ingesta y el vigilante. Un flujo de publicacion se dispara por evento y
    # pedirle un cron seria ceremonia: publicaria lo mismo otra vez.
    for nombre in set(flujos_ingesta) | set(flujos_vigilante):
        exigir(
            "schedule:" in contenidos[nombre] and "cron:" in contenidos[nombre],
            f"{nombre} no tiene cadencia diaria",
        )
    detalles.append(
        f"los {len(contenidos)} flujos declaran concurrencia y tiempo limite · "
        f"cadencia diaria en ingesta y vigilante"
    )

    for nombre in flujos_ingesta:
        exigir(
            "derivados.py" in contenidos[nombre],
            f"{nombre} no calcula los indicadores propios tras la ingesta",
        )
        exigir(
            "web/construir.py" in contenidos[nombre],
            f"{nombre} no reconstruye la pagina tras la ingesta",
        )
    detalles.append("el flujo de ingesta recalcula derivados y reconstruye la pagina")
    return detalles


if __name__ == "__main__":
    sys.exit(gate_util.correr(verificar, MARCADOR))
