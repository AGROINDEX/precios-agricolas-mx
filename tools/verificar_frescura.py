"""B6 · el vigilante detecta una fuente congelada y no grita con las sanas.

Un gate de ausencia sin control positivo no prueba nada: un vigilante que
siempre dice que todo esta bien pasaria igual. Aqui se exigen las dos mitades,
el control positivo tiene que fallar y el reporte real tiene que pasar, y ademas
se comprueba que lo que mide es el ultimo fetch BUENO y no el ultimo intento.

Uso:
  python tools/verificar_frescura.py --control-positivo fixtures/pista_b/fetch_report_congelado.json
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone

import gate_util
from gate_util import exigir, ruta

MARCADOR = "vigilante verificado · control positivo detectado como congelado"
VIGILANTE = ruta("ingesta", "check_fuentes_stale.py")


def correr_vigilante(reporte):
    resultado = subprocess.run(
        [sys.executable, VIGILANTE, "--reporte", reporte],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )
    return resultado.returncode, (resultado.stdout or "") + (resultado.stderr or "")


def verificar(control, reporte_real):
    detalles = []
    exigir(os.path.exists(control), f"no existe el control positivo en {control}")
    exigir(os.path.exists(reporte_real), f"no existe el reporte real en {reporte_real}")

    codigo, salida = correr_vigilante(control)
    exigir(codigo != 0, "el vigilante paso en verde el control positivo: esta roto")
    exigir("congelada" in salida, "el vigilante no nombro ninguna fuente congelada en el control")
    with open(control, encoding="utf-8") as archivo:
        esperadas = set(json.load(archivo)["fuentes"])
    for clave in esperadas:
        exigir(clave in salida, f"el vigilante no marco {clave} en el control positivo")
    detalles.append(f"control positivo: codigo {codigo} · marco {len(esperadas)} fuentes congeladas")

    codigo_real, salida_real = correr_vigilante(reporte_real)
    exigir(
        codigo_real == 0,
        f"el reporte real salio congelado, asi que la ingesta no esta corriendo: {salida_real.strip()}",
    )
    detalles.append("reporte real en vivo: dentro de umbral")

    # Lo que mide es el ultimo fetch bueno, no el ultimo intento. Se construye un
    # reporte con intentos de hace un minuto y un fetch bueno viejo: tiene que
    # marcarlo congelado igual.
    carpeta = tempfile.mkdtemp(prefix="gate_frescura_")
    sintetico = os.path.join(carpeta, "reporte.json")
    ahora = datetime.now(timezone.utc)
    with open(sintetico, "w", encoding="utf-8") as archivo:
        json.dump(
            {
                "fuentes": {
                    "SNIIM_FYH": {
                        "critical": True,
                        "nombre": "prueba",
                        "ultimo_intento": ahora.isoformat(timespec="seconds"),
                        "ultimo_fetch_bueno": (ahora - timedelta(days=9)).isoformat(timespec="seconds"),
                        "ultimo_detalle": "200 con cero filas",
                    }
                }
            },
            archivo,
        )
    codigo_sintetico, salida_sintetica = correr_vigilante(sintetico)
    exigir(
        codigo_sintetico != 0,
        "con intentos recientes y fetch bueno viejo el vigilante paso en verde:"
        " esta midiendo el intento y no la descarga buena",
    )
    exigir("SNIIM_FYH" in salida_sintetica, "el vigilante no nombro la fuente del caso sintetico")
    detalles.append("mide dias desde el ultimo fetch bueno, no desde el ultimo intento")
    return detalles


if __name__ == "__main__":
    lector = argparse.ArgumentParser(description="Verifica el vigilante de frescura")
    lector.add_argument("--control-positivo", required=True)
    lector.add_argument("--reporte", default=ruta("datos", "pista_b", "_fetch_report.json"))
    argumentos = lector.parse_args()
    sys.exit(
        gate_util.correr(
            lambda: verificar(argumentos.control_positivo, argumentos.reporte), MARCADOR
        )
    )
