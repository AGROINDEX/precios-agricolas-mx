"""Vigilante de fuentes congeladas, apuntado a las fuentes de precios.

POR QUE EXISTE. Esta pieza nacio en AgroPatentIndex porque un fetcher estuvo
roto diecinueve dias sin que nadie lo notara: la alerta salia en todas las
corridas, y una alerta que sale siempre es una alerta que nadie mira. Ahi era
un extra. Aqui es el corazon del producto: en un tablero de precios, un dato
viejo presentado como de hoy es peor que no tener dato.

QUE MIDE. Dias desde el ultimo fetch BUENO, no la antiguedad del archivo ni del
ultimo intento. Una fuente puede responder 200 con la tabla vacia todos los dias
y eso es exactamente como se congela sin avisar.

QUE NO CUENTA COMO CONGELAMIENTO. El SNIIM no publica sabados, domingos ni dias
festivos, y la Central de Abasto publica con un dia de rezago. Por eso el umbral
critico es de tres dias y no de uno: cubre un fin de semana largo sin gritar.

Corre en su propio flujo de CI, asi que fallar no toca el despliegue: solo pone
la corrida en rojo, que es lo que GitHub si notifica.

Uso:
  python ingesta/check_fuentes_stale.py
  python ingesta/check_fuentes_stale.py --reporte fixtures/pista_b/fetch_report_congelado.json
  python ingesta/check_fuentes_stale.py --umbral-critico 5
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone

for _flujo in (sys.stdout, sys.stderr):
    try:
        _flujo.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTE = os.path.join(RAIZ, "datos", "pista_b", "_fetch_report.json")

UMBRAL_CRITICO = int(os.environ.get("STALE_UMBRAL_CRITICO", "3"))
UMBRAL_NORMAL = int(os.environ.get("STALE_UMBRAL_NORMAL", "8"))


def dias_desde(marca):
    if not marca:
        return None
    momento = datetime.fromisoformat(marca)
    if momento.tzinfo is None:
        momento = momento.replace(tzinfo=timezone.utc)
    return (datetime.now(timezone.utc) - momento).total_seconds() / 86400


def evaluar(reporte, umbral_critico=UMBRAL_CRITICO, umbral_normal=UMBRAL_NORMAL):
    """Devuelve (congeladas, sanas). Congelada = paso su umbral o nunca tuvo fetch bueno."""
    congeladas = []
    sanas = []
    for clave, entrada in sorted(reporte.get("fuentes", {}).items()):
        critica = bool(entrada.get("critical"))
        umbral = umbral_critico if critica else umbral_normal
        dias = dias_desde(entrada.get("ultimo_fetch_bueno"))
        registro = {
            "fuente": clave,
            "nombre": entrada.get("nombre", clave),
            "critica": critica,
            "umbral": umbral,
            "dias": None if dias is None else round(dias, 2),
            "detalle": entrada.get("ultimo_detalle", ""),
        }
        if dias is None or dias > umbral:
            congeladas.append(registro)
        else:
            sanas.append(registro)
    return congeladas, sanas


def main():
    lector = argparse.ArgumentParser(description="Vigilante de fuentes congeladas")
    lector.add_argument("--reporte", default=REPORTE)
    lector.add_argument("--umbral-critico", type=int, default=UMBRAL_CRITICO)
    lector.add_argument("--umbral-normal", type=int, default=UMBRAL_NORMAL)
    lector.add_argument("--json", action="store_true", help="salida en json, para la pagina")
    argumentos = lector.parse_args()

    if not os.path.exists(argumentos.reporte):
        print(f"::error::no existe el reporte de fetch en {argumentos.reporte}")
        return 1

    with open(argumentos.reporte, encoding="utf-8") as archivo:
        reporte = json.load(archivo)

    congeladas, sanas = evaluar(reporte, argumentos.umbral_critico, argumentos.umbral_normal)

    if argumentos.json:
        print(json.dumps({"congeladas": congeladas, "sanas": sanas}, ensure_ascii=False, indent=2))
        return 1 if congeladas else 0

    for registro in sanas:
        print(f"ok      {registro['fuente']} · {registro['dias']} dias desde el ultimo fetch bueno")
    for registro in congeladas:
        dias = "nunca" if registro["dias"] is None else f"{registro['dias']} dias"
        nivel = "error" if registro["critica"] else "warning"
        print(
            f"::{nivel}::fuente congelada {registro['fuente']} · {dias} sin fetch bueno "
            f"· umbral {registro['umbral']} · {registro['detalle']}"
        )

    if congeladas:
        print(f"CONGELADAS: {len(congeladas)} de {len(congeladas) + len(sanas)}")
        return 1
    print(f"frescura verificada · {len(sanas)} fuentes dentro de umbral")
    return 0


if __name__ == "__main__":
    sys.exit(main())
