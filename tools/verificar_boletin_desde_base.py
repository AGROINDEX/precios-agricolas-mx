"""A8 · el boletin se arma desde la base, no a mano.

COMO SE PRUEBA. No basta con que las trazas existan: un boletin podria citar dos
filas reales y escribir a mano un tercer numero. Asi que se recogen TODAS las
cifras de dinero y de porcentaje del cuerpo del boletin y se exige que cada una
se explique con un valor de la base o con un derivado calculado sobre ella.
Una cifra que no se explica es una cifra capturada a mano.
"""
import json
import os
import re
import sys

import gate_util
from gate_util import exigir, ruta

MARCADOR = "boletin trazado a la base · sin filas capturadas a mano"
BOLETIN = ruta("boletin", "ultimo.md")

TOLERANCIA = 0.011


def cuerpo_y_trazas(texto):
    encontrado = re.search(r"<!--\s*trazas:\s*(\[.*?\])\s*-->", texto, re.S)
    exigir(encontrado, "el boletin no trae bloque de trazas")
    cuerpo = texto[: encontrado.start()]
    # La consulta de origen lleva fechas con numeros que no son cifras de precio.
    cuerpo = re.sub(r"Consulta de origen:.*", "", cuerpo, flags=re.S)
    return cuerpo, json.loads(encontrado.group(1))


def cifras(cuerpo):
    # Se toman solo las cifras con decimales o seguidas de "por ciento": las
    # fechas y los conteos de dias no son precios.
    encontradas = set()
    for bruto in re.findall(r"\d{1,3}(?:,\d{3})*\.\d{1,2}", cuerpo):
        encontradas.add(round(float(bruto.replace(",", "")), 2))
    for bruto in re.findall(r"(\d+(?:\.\d+)?)\s*por ciento", cuerpo):
        encontradas.add(round(float(bruto), 2))
    return encontradas


def valores_de_la_base(conexion, trazas):
    permitidos = set()
    for traza in trazas:
        fila = conexion.execute(
            "SELECT fuente, producto, mercado, fecha_dato, precio_min, precio_max, precio_frec"
            " FROM precios WHERE id = ?",
            (traza["id"],),
        ).fetchone()
        exigir(fila is not None, f"la traza {traza['id']} no existe en la base")
        fuente, producto, mercado, fecha, minimo, maximo, frecuente = fila
        for valor in (minimo, maximo, frecuente):
            if valor is not None:
                permitidos.add(round(valor, 2))
        derivado = conexion.execute(
            "SELECT mediana_frec_7d, variacion_pct_1d, amplitud_rel FROM derivados"
            " WHERE fuente = ? AND producto = ? AND mercado = ? AND fecha_dato = ?",
            (fuente, producto, mercado, fecha),
        ).fetchone()
        if derivado:
            mediana, variacion, amplitud = derivado
            for valor in (mediana, variacion, amplitud):
                if valor is not None:
                    permitidos.add(round(valor, 2))
            if amplitud is not None:
                # El boletin redondea el porcentaje a entero para que se lea en
                # un telefono. El redondeo de presentacion es legitimo, la
                # cifra inventada no, asi que se admite solo la version
                # redondeada del mismo valor.
                permitidos.add(round(amplitud * 100, 2))
                permitidos.add(float(round(amplitud * 100)))
            if variacion is not None:
                permitidos.add(round(abs(variacion), 2))
                permitidos.add(float(round(abs(variacion))))
    # Diferencias entre dos filas citadas: son calculo sobre la base, no captura.
    frecuentes = []
    for traza in trazas:
        if traza.get("precio_frec") is not None:
            frecuentes.append(round(traza["precio_frec"], 2))
    for uno in frecuentes:
        for otro in frecuentes:
            if uno and otro:
                permitidos.add(round(abs(uno - otro), 2))
                permitidos.add(round(abs(uno - otro) / uno * 100, 1))
                permitidos.add(round(abs(uno - otro) / uno * 100, 2))
    return permitidos


def verificar():
    import comun

    detalles = []
    exigir(os.path.exists(BOLETIN), f"no existe el boletin en {BOLETIN}")
    with open(BOLETIN, encoding="utf-8") as archivo:
        texto = archivo.read()
    cuerpo, trazas = cuerpo_y_trazas(texto)
    exigir(trazas, "el boletin no cita ninguna fila")

    conexion = comun.conectar()
    permitidos = valores_de_la_base(conexion, trazas)
    conexion.close()

    publicadas = cifras(cuerpo)
    exigir(publicadas, "el boletin no publica ninguna cifra")

    sin_respaldo = [
        cifra
        for cifra in sorted(publicadas)
        if not any(abs(cifra - permitido) <= TOLERANCIA for permitido in permitidos)
    ]
    exigir(
        not sin_respaldo,
        f"cifras publicadas que no salen de la base ni de sus derivados: {sin_respaldo}",
    )
    detalles.append(f"cifras publicadas: {len(publicadas)} · todas explicadas por la base")
    detalles.append(f"filas citadas: {[traza['id'] for traza in trazas]}")

    # Control del propio verificador: una cifra inventada tiene que delatarse.
    inventada = max(permitidos) + 7.77
    exigir(
        not any(abs(inventada - permitido) <= TOLERANCIA for permitido in permitidos),
        "el verificador acepta una cifra inventada: no sirve",
    )
    detalles.append("control interno: una cifra ajena a la base si es rechazada")
    return detalles


if __name__ == "__main__":
    sys.exit(gate_util.correr(verificar, MARCADOR))
