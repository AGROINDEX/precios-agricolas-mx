"""A5 · la bitacora cubre siete dias seguidos, con un envio por dia y sin huecos.

Siete dias seguidos no es capricho: la pregunta del piloto es si alguien lo abre
al tercer dia, y eso no se puede medir con envios salteados. Un hueco a mitad de
la semana cambia la metrica y hay que verlo.
"""
import argparse
import json
import os
import re
import sys
from datetime import date, datetime, timedelta

import gate_util
from gate_util import exigir, ruta, ruta_datos_a

MARCADOR = "bitacora verificada · siete dias consecutivos sin huecos"
BITACORA = ruta_datos_a("bitacora.json")
LADOS = ("vendedor", "comprador")


def cargar():
    exigir(os.path.exists(BITACORA), f"no existe la bitacora en {BITACORA}")
    with open(BITACORA, encoding="utf-8") as archivo:
        return json.load(archivo)


def verificar(dias):
    detalles = []
    datos = cargar()
    envios = datos.get("envios", [])
    exigir(
        envios,
        "la bitacora no tiene un solo envio. Este gate no lo cierra un agente:"
        " se cierra enviando el boletin a personas reales durante siete dias",
    )

    identificadores = set()
    for envio in envios:
        for campo in ("fecha", "lado", "boletin", "canal", "destinatarios"):
            exigir(envio.get(campo), f"un envio del {envio.get('fecha', 'sin fecha')} no tiene {campo}")
        exigir(
            re.fullmatch(r"\d{4}-\d{2}-\d{2}", envio["fecha"]),
            f"la fecha {envio['fecha']} no es una fecha",
        )
        exigir(envio["lado"] in LADOS, f"el envio del {envio['fecha']} no declara un lado valido")
        exigir(
            envio["fecha"] <= date.today().isoformat(),
            f"el envio del {envio['fecha']} esta fechado en el futuro",
        )
        camino = ruta(*envio["boletin"].split("/"))
        exigir(os.path.exists(camino), f"el envio del {envio['fecha']} cita un boletin que no existe")
        exigir(
            isinstance(envio["destinatarios"], list) and envio["destinatarios"],
            f"el envio del {envio['fecha']} no lista destinatarios",
        )
        identificadores.update(envio["destinatarios"])

    fechas = sorted({envio["fecha"] for envio in envios})
    exigir(
        len(fechas) >= dias,
        f"la bitacora cubre {len(fechas)} dias distintos y el gate pide {dias}",
    )

    # Ventana de dias consecutivos: se busca la racha mas larga.
    mejor = 1
    racha = 1
    for anterior, actual in zip(fechas, fechas[1:]):
        uno = datetime.strptime(anterior, "%Y-%m-%d").date()
        dos = datetime.strptime(actual, "%Y-%m-%d").date()
        racha = racha + 1 if dos - uno == timedelta(days=1) else 1
        mejor = max(mejor, racha)
    exigir(
        mejor >= dias,
        f"la racha mas larga sin huecos es de {mejor} dias y el gate pide {dias}",
    )

    por_dia = {}
    for envio in envios:
        por_dia.setdefault(envio["fecha"], []).append(envio)
    sin_vendedor = [fecha for fecha, lista in por_dia.items() if not any(e["lado"] == "vendedor" for e in lista)]
    exigir(not sin_vendedor, f"estos dias no tienen envio al lado vendedor: {sorted(sin_vendedor)}")

    # Los destinatarios tienen que existir en alguna cohorte: un envio a un id
    # que no esta registrado es un envio sin consentimiento comprobable.
    registrados = set()
    for nombre in ("cohorte_vendedor.json", "cohorte_comprador.json"):
        camino = ruta_datos_a(nombre)
        if os.path.exists(camino):
            with open(camino, encoding="utf-8") as archivo:
                registrados.update(r.get("id") for r in json.load(archivo).get("registros", []))
    huerfanos = sorted(identificadores - registrados)
    exigir(not huerfanos, f"se envio a destinatarios que no estan en ninguna cohorte: {huerfanos}")

    detalles.append(f"dias cubiertos: {len(fechas)} · racha sin huecos: {mejor}")
    detalles.append(f"destinatarios distintos alcanzados: {len(identificadores)}")
    lados = sorted({envio["lado"] for envio in envios})
    detalles.append(f"lados distinguidos en la bitacora: {lados}")
    return detalles


if __name__ == "__main__":
    lector = argparse.ArgumentParser(description="Verifica la bitacora de envios")
    lector.add_argument("--dias", type=int, default=7)
    argumentos = lector.parse_args()
    sys.exit(gate_util.correr(lambda: verificar(argumentos.dias), MARCADOR))
