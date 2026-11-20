"""A11 · los dos competidores fueron probados pagando, y el desmontaje lo registra.

Gate de presencia de campos, no de ausencia, asi que no lleva control positivo.
Lo que no acepta es el atajo: mirar la pagina de precios desde fuera y llenar
los campos con lo que anuncian. Por eso exige fecha de prueba, plan contratado y
costo con cifra, que son las tres cosas que solo existen si alguien pago y entro.
"""
import os
import re
import sys
from datetime import date, datetime

import gate_util
from gate_util import exigir, ruta

MARCADOR = "competencia verificada · dos productos probados con campos completos y hueco declarado"
DESMONTAJE = ruta("competencia", "desmontaje.md")

COMPETIDORES = ("AgroPrecios MX", "Abasteros")

CAMPOS = (
    "Fecha de la prueba",
    "Plan contratado",
    "Costo",
    "Que entrega al lado comprador",
    "Que no entrega",
    "De donde saca el dato",
    "Frescura",
)

VACIO = re.compile(r"^(pendiente|por definir|n/?a|tbd|\-+)\.?$", re.I)
MINIMO_TEXTO = 25


def bloque_de(texto, titulo):
    patron = re.compile(rf"^##\s+{re.escape(titulo)}\s*$", re.M)
    encontrado = patron.search(texto)
    exigir(encontrado, f"el desmontaje no tiene una seccion para {titulo}")
    siguiente = re.compile(r"^##\s+", re.M).search(texto, encontrado.end())
    return texto[encontrado.end() : siguiente.start() if siguiente else len(texto)]


def campo_de(bloque, campo, titulo):
    encontrado = re.search(rf"^-\s*{re.escape(campo)}\s*:\s*(.+)$", bloque, re.M)
    exigir(encontrado, f"a {titulo} le falta el campo '{campo}'")
    valor = encontrado.group(1).strip()
    exigir(valor, f"el campo '{campo}' de {titulo} esta vacio")
    exigir(
        not VACIO.match(valor),
        f"el campo '{campo}' de {titulo} sigue en pendiente: el gate exige probar pagando el plan",
    )
    return valor


def verificar():
    detalles = []
    exigir(os.path.exists(DESMONTAJE), f"no existe el desmontaje en {DESMONTAJE}")
    with open(DESMONTAJE, encoding="utf-8") as archivo:
        texto = archivo.read()

    for titulo in COMPETIDORES:
        bloque = bloque_de(texto, titulo)
        valores = {campo: campo_de(bloque, campo, titulo) for campo in CAMPOS}

        fecha = valores["Fecha de la prueba"]
        exigir(
            re.search(r"\d{4}-\d{2}-\d{2}", fecha),
            f"la fecha de prueba de {titulo} no trae una fecha en formato 2026-11-20",
        )
        dia = datetime.strptime(re.search(r"\d{4}-\d{2}-\d{2}", fecha).group(0), "%Y-%m-%d").date()
        exigir(dia <= date.today(), f"la prueba de {titulo} esta fechada en el futuro")

        exigir(
            re.search(r"\d", valores["Costo"]),
            f"el costo de {titulo} no trae cifra: probar pagando deja un monto",
        )
        for campo in ("Que entrega al lado comprador", "Que no entrega", "De donde saca el dato"):
            exigir(
                len(valores[campo]) >= MINIMO_TEXTO,
                f"el campo '{campo}' de {titulo} tiene {len(valores[campo])} caracteres:"
                f" hace falta una descripcion util, no una palabra",
            )
        detalles.append(
            f"{titulo}: probado el {dia.isoformat()} · plan {valores['Plan contratado']}"
            f" · costo {valores['Costo']}"
        )

    hueco = bloque_de(texto, "El hueco")
    cuerpo = "\n".join(
        linea for linea in hueco.splitlines() if linea.strip() and not linea.strip().startswith("#")
    ).strip()
    exigir(cuerpo, "la seccion del hueco esta vacia")
    exigir(
        not VACIO.match(cuerpo.split("\n")[0].strip()),
        "la seccion del hueco sigue en pendiente: se escribe despues de usar los dos productos",
    )
    exigir(
        len(cuerpo) >= 200,
        f"la seccion del hueco tiene {len(cuerpo)} caracteres: el gate pide el hueco concreto",
    )
    detalles.append(f"seccion del hueco escrita, {len(cuerpo)} caracteres")

    exigir(
        "incompleto" not in texto.splitlines()[2].lower() if len(texto.splitlines()) > 2 else True,
        "el documento sigue marcado como incompleto en su propio encabezado",
    )
    return detalles


if __name__ == "__main__":
    sys.exit(gate_util.correr(verificar, MARCADOR))
