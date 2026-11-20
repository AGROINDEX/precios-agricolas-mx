"""A6 y A7 · las metricas del piloto se calculan desde la bitacora.

Dos lados, dos preguntas distintas, dos metricas distintas:

  vendedor   oferta de dato. Lecturas al tercer dia y cuantas respuestas traen
             el precio propio de quien contesta. Un numero alto aqui NO prueba
             negocio: prueba que la fuente de dato existe.
  comprador  disposicion a pagar. Conversaciones donde se puso un precio sobre
             la mesa, con la respuesta textual y clasificada. El gate pide al
             menos tres, porque una sola conversacion no es senal.

El verificador calcula los numeros aqui, desde la bitacora, y no acepta cifras
escritas en ningun otro lado.

Uso:
  python tools/verificar_metricas.py --lado vendedor
  python tools/verificar_metricas.py --lado comprador
"""
import argparse
import json
import os
import sys
from datetime import datetime, timedelta

import gate_util
from gate_util import exigir, ruta_datos_a

BITACORA = ruta_datos_a("bitacora.json")
CLASIFICACIONES = {"pagaria", "no_pagaria", "condicionada"}


def cargar():
    exigir(os.path.exists(BITACORA), f"no existe la bitacora en {BITACORA}")
    with open(BITACORA, encoding="utf-8") as archivo:
        return json.load(archivo)


def verificar_vendedor():
    detalles = []
    datos = cargar()
    envios = [e for e in datos.get("envios", []) if e.get("lado") == "vendedor"]
    exigir(
        envios,
        "no hay envios al lado vendedor en la bitacora: no hay nada que medir."
        " Este gate se cierra enviando el boletin a la cohorte real",
    )

    fechas = sorted({envio["fecha"] for envio in envios})
    primera = datetime.strptime(fechas[0], "%Y-%m-%d").date()
    tercer_dia = (primera + timedelta(days=2)).isoformat()
    envios_tercer_dia = [e for e in envios if e["fecha"] == tercer_dia]
    exigir(
        envios_tercer_dia,
        f"no hay envio del tercer dia ({tercer_dia}), que es justo el dia que mide el piloto",
    )

    alcanzados = sum(len(e["destinatarios"]) for e in envios_tercer_dia)
    lecturas = 0
    for envio in envios_tercer_dia:
        exigir(
            "lecturas" in envio,
            f"el envio del {envio['fecha']} no registra lecturas, que es la metrica del gate",
        )
        exigir(
            isinstance(envio["lecturas"], int) and envio["lecturas"] >= 0,
            f"las lecturas del {envio['fecha']} no son un conteo",
        )
        exigir(
            envio["lecturas"] <= len(envio["destinatarios"]),
            f"el envio del {envio['fecha']} registra mas lecturas que destinatarios",
        )
        lecturas += envio["lecturas"]

    respuestas = [r for r in datos.get("respuestas", []) if r.get("lado") == "vendedor"]
    con_precio = []
    for respuesta in respuestas:
        if respuesta.get("tipo") != "precio_propio":
            continue
        precio = respuesta.get("precio") or {}
        exigir(
            str(respuesta.get("texto", "")).strip(),
            f"la respuesta de {respuesta.get('contacto')} no trae el texto literal",
        )
        for campo in ("producto", "precio", "plaza", "base"):
            exigir(
                precio.get(campo) not in (None, ""),
                f"la respuesta de {respuesta.get('contacto')} dice traer precio propio y le falta {campo}",
            )
        con_precio.append(respuesta)

    proporcion = (lecturas / alcanzados * 100) if alcanzados else 0
    detalles.append(f"primer envio: {fechas[0]} · tercer dia: {tercer_dia}")
    detalles.append(
        f"lecturas al tercer dia: {lecturas} de {alcanzados} destinatarios ({proporcion:.0f} por ciento)"
    )
    detalles.append(f"respuestas con precio propio: {len(con_precio)} de {len(respuestas)} respuestas")
    detalles.append(
        "nota de lectura: este numero mide oferta de dato del lado que no paga, no demanda"
    )
    return detalles


def verificar_comprador(minimo=3):
    detalles = []
    datos = cargar()
    respuestas = [r for r in datos.get("respuestas", []) if r.get("lado") == "comprador"]
    con_precio = [r for r in respuestas if r.get("tipo") == "disposicion_a_pagar"]
    exigir(
        len(con_precio) >= minimo,
        f"hay {len(con_precio)} conversaciones con precio sobre la mesa y el gate pide {minimo}."
        " Preguntar si les interesa no cuenta: hay que decir un numero y anotar la respuesta",
    )

    conteo = {clave: 0 for clave in CLASIFICACIONES}
    contactos = set()
    for respuesta in con_precio:
        etiqueta = respuesta.get("contacto", "sin contacto")
        exigir(respuesta.get("precio_puesto"), f"la conversacion con {etiqueta} no registra el precio puesto")
        exigir(
            isinstance(respuesta["precio_puesto"], (int, float)) and respuesta["precio_puesto"] > 0,
            f"el precio puesto con {etiqueta} no es un monto",
        )
        exigir(
            len(str(respuesta.get("texto", "")).strip()) >= 10,
            f"la conversacion con {etiqueta} no trae la respuesta textual",
        )
        clasificacion = str(respuesta.get("clasificacion", "")).strip().lower()
        exigir(
            clasificacion in CLASIFICACIONES,
            f"la conversacion con {etiqueta} no esta clasificada en {sorted(CLASIFICACIONES)}",
        )
        conteo[clasificacion] += 1
        contactos.add(etiqueta)

    exigir(
        len(contactos) >= minimo,
        f"las {len(con_precio)} conversaciones son con {len(contactos)} compradores distintos",
    )
    montos = sorted(r["precio_puesto"] for r in con_precio)
    detalles.append(f"conversaciones con precio sobre la mesa: {len(con_precio)} con {len(contactos)} compradores")
    detalles.append(f"clasificacion: {conteo}")
    detalles.append(f"precios puestos: de {montos[0]:,.0f} a {montos[-1]:,.0f}")
    return detalles


if __name__ == "__main__":
    lector = argparse.ArgumentParser(description="Calcula las metricas del piloto desde la bitacora")
    lector.add_argument("--lado", required=True, choices=["vendedor", "comprador"])
    argumentos = lector.parse_args()
    if argumentos.lado == "vendedor":
        sys.exit(gate_util.correr(verificar_vendedor, "metrica vendedor calculada desde bitacora"))
    sys.exit(gate_util.correr(verificar_comprador, "metrica comprador calculada desde bitacora"))
