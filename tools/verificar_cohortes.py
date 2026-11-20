"""A3 y A4 · las cohortes son de personas reales, con consentimiento y sin relleno.

Este verificador no puede volverse verde solo porque haya un archivo. Exige
numero minimo, campos completos, contactos distintos y, en el lado vendedor,
consentimiento con fecha, medio y lo que la persona contesto. Ademas rechaza el
relleno tipico, que es la manera facil de aprobar un gate sin haber hablado con
nadie.

Uso:
  python tools/verificar_cohortes.py --lado vendedor --minimo 15
  python tools/verificar_cohortes.py --lado comprador --minimo 3
"""
import argparse
import json
import os
import re
import sys
from datetime import date

import gate_util
from gate_util import exigir, ruta_datos_a

def archivo_de(lado):
    return ruta_datos_a(f"cohorte_{lado}.json")

CAMPOS = {
    "vendedor": ("id", "nombre", "rol", "cultivo", "plaza", "canal", "contacto", "fuente_del_contacto"),
    "comprador": ("id", "empresa", "persona", "cargo", "tipo", "contacto", "fecha_conversacion", "fuente_del_contacto"),
}

TIPOS_COMPRADOR = {"mayorista", "exportador", "cadena", "servicio de alimentos", "agroindustria"}

RELLENO = re.compile(
    r"ejemplo|pendiente|por definir|lorem|prueba\b|test\b|xxx|\bfulano\b|\bnombre\b$|^\+?52 \.\.\.",
    re.I,
)


def verificar(lado, minimo):
    detalles = []
    camino = archivo_de(lado)
    exigir(os.path.exists(camino), f"no existe el registro de la cohorte en {camino}")
    with open(camino, encoding="utf-8") as archivo:
        datos = json.load(archivo)

    registros = datos.get("registros", [])
    exigir(
        len(registros) >= minimo,
        f"la cohorte {lado} tiene {len(registros)} registros y el gate pide {minimo}."
        " Este gate no lo cierra un agente: son personas reales de la red del fundador",
    )

    contactos = set()
    identificadores = set()
    for registro in registros:
        etiqueta = registro.get("id", "sin id")
        for campo in CAMPOS[lado]:
            valor = str(registro.get(campo, "")).strip()
            exigir(valor, f"el registro {etiqueta} no tiene {campo}")
            exigir(
                not RELLENO.search(valor),
                f"el registro {etiqueta} tiene relleno en {campo}: {valor}",
            )
        exigir(registro["id"] not in identificadores, f"el id {registro['id']} esta repetido")
        identificadores.add(registro["id"])
        contacto = str(registro["contacto"]).strip().lower()
        exigir(contacto not in contactos, f"el contacto de {etiqueta} esta repetido")
        contactos.add(contacto)

        if lado == "vendedor":
            consentimiento = registro.get("consentimiento") or {}
            for campo in ("fecha", "medio", "texto"):
                valor = str(consentimiento.get(campo, "")).strip()
                exigir(valor, f"el registro {etiqueta} no tiene consentimiento.{campo}")
            exigir(
                re.fullmatch(r"\d{4}-\d{2}-\d{2}", consentimiento["fecha"]),
                f"la fecha de consentimiento de {etiqueta} no es una fecha",
            )
            exigir(
                consentimiento["fecha"] <= date.today().isoformat(),
                f"el consentimiento de {etiqueta} esta fechado en el futuro",
            )
            exigir(
                len(str(consentimiento["texto"]).strip()) >= 10,
                f"el consentimiento de {etiqueta} no registra lo que la persona contesto",
            )
        else:
            exigir(
                str(registro["tipo"]).strip().lower() in TIPOS_COMPRADOR,
                f"el tipo de comprador de {etiqueta} no es uno de los del gate: {TIPOS_COMPRADOR}",
            )
            exigir(
                re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(registro["fecha_conversacion"])),
                f"la fecha de conversacion de {etiqueta} no es una fecha",
            )
            exigir(
                str(registro["fecha_conversacion"]) <= date.today().isoformat(),
                f"la conversacion de {etiqueta} esta fechada en el futuro",
            )

    detalles.append(f"cohorte {lado}: {len(registros)} registros completos y sin repetidos")
    if lado == "vendedor":
        detalles.append("consentimiento con fecha, medio y respuesta textual en todos")
    else:
        tipos = sorted({str(r["tipo"]).lower() for r in registros})
        detalles.append(f"tipos de comprador representados: {tipos}")
    return detalles


if __name__ == "__main__":
    lector = argparse.ArgumentParser(description="Verifica una cohorte del piloto")
    lector.add_argument("--lado", required=True, choices=["vendedor", "comprador"])
    lector.add_argument("--minimo", type=int, required=True)
    argumentos = lector.parse_args()
    if argumentos.lado == "vendedor":
        marcador = "cohorte vendedor verificada · consentimiento presente en todos los registros"
    else:
        marcador = "cohorte comprador verificada · tres o mas compradores con conversacion fechada"
    sys.exit(gate_util.correr(lambda: verificar(argumentos.lado, argumentos.minimo), marcador))
