"""B21 · la cadencia de cada plaza esta medida, y sigue siendo cierta.

POR QUE ESTE GATE Y NO SOLO B17. B17 comprueba que el silencio se juzga contra
la cadencia declarada. Este comprueba que la cadencia declarada es VERDAD. Son
cosas distintas: un vigilante impecable que juzgue contra una cadencia
equivocada da por muerta una plaza viva todos los dias.

QUE SE COMPRUEBA

1. La tabla es generada, no escrita a mano. Lleva su fecha de medicion y la
   ventana sobre la que se midio, y el generador existe.
2. Toda plaza que se ingiere tiene cadencia declarada, y toda plaza declarada
   existe en el catalogo de la fuente.
3. Se vuelve a PREGUNTARLE A LA FUENTE por una muestra de plazas, con una
   consulta de rango propia, y se exige que los dias de la semana en que
   publican coincidan con lo declarado. Sin esto el gate solo probaria que un
   archivo generado coincide consigo mismo.
4. Control positivo: una tabla con una cadencia falsa tiene que ser rechazada
   por la misma comprobacion.

La muestra incluye SIEMPRE las plazas de cadencia no diaria, que son las que
importan y las que se escaparon la primera vez, mas unas cuantas diarias.

Uso:
  python tools/verificar_cadencia_medida.py --control-falso
"""
import argparse
import collections
import os
import sys
from datetime import date, timedelta

import gate_util
from gate_util import exigir, ruta

MARCADOR = "cadencia medida verificada · muestra coincide con la fuente y control falso rechazado"

# Cuantas plazas diarias se vuelven a preguntar. Todas las no diarias se
# preguntan siempre: son tres y son las que deciden. La muestra es chica a
# proposito: este gate corre en cada verificacion y la fuente es un servidor de
# 2003 que ya devolvio 503 cuando se le pidio de mas en un dia.
MUESTRA_DIARIAS = 2

# Dias que se piden al volver a preguntar. Treinta alcanzan para ver en que
# dias de la semana publica una plaza, y pesan una quinta parte que noventa.
DIAS_MUESTRA = 30

# Reintentos ante un fallo de la fuente. Un 503 de un servidor viejo no es una
# cadencia equivocada, y un gate que se pone rojo por eso entrena a cualquiera
# a ignorarlo. Si ni asi responde, el gate falla DICIENDO que fue la fuente.
REINTENTOS = 3

# La medicion no puede ser mas vieja que esto sin volver a correrse: una plaza
# puede cambiar de cadencia y el archivo generado se quedaria mintiendo.
VIGENCIA_DIAS = 120


def preguntar(medir_cadencia, plaza_id, desde, hasta):
    """Una consulta a la fuente, con reintentos y espera creciente."""
    import time

    ultimo = None
    for intento in range(REINTENTOS):
        try:
            return medir_cadencia.traer(
                medir_cadencia.url_rango(plaza_id, desde, hasta), tiempo=180
            )
        except Exception as fallo:  # noqa: BLE001
            ultimo = fallo
            if intento < REINTENTOS - 1:
                time.sleep(5 * (intento + 1))
    raise gate_util.Fallo(
        f"la fuente no respondio para la plaza {plaza_id} tras {REINTENTOS} intentos:"
        f" {type(ultimo).__name__} {ultimo}. Esto es la fuente caida, no una cadencia"
        " equivocada"
    )


def dias_de_la_semana(fechas):
    return {date.fromisoformat(f).weekday() for f in fechas}


def coincide(declarada, medidos, publicados):
    """La cadencia declarada explica lo que la fuente publica. Funcion pura."""
    if declarada["cadencia"] == "diaria":
        if len(medidos) >= 5:
            return True, f"publico en {len(medidos)} dias de la semana"
        return False, (
            f"declarada diaria y solo publico en {len(medidos)} dias de la semana"
            f" ({sorted(medidos)})"
        )
    esperados = set(declarada["dias"])
    if medidos and medidos <= esperados:
        return True, f"publico solo en {sorted(medidos)}, declarados {sorted(esperados)}"
    return False, (
        f"declarada semanal en {sorted(esperados)} y publico en {sorted(medidos)}"
    )


def verificar(con_control):
    sys.path.insert(0, ruta("ingesta"))
    import cadencias
    import medir_cadencia
    import sniim
    from comun import conectar

    detalles = []

    # 1. Es un archivo generado, con su procedencia.
    exigir(
        os.path.exists(ruta("ingesta", "medir_cadencia.py")),
        "no existe el generador ingesta/medir_cadencia.py: la tabla seria escrita a mano",
    )
    archivo = ruta("ingesta", "cadencias.py")
    with open(archivo, encoding="utf-8") as mano:
        fuente_tabla = mano.read()
    exigir(
        "ARCHIVO GENERADO" in fuente_tabla,
        "la tabla de cadencias no se declara como generada",
    )
    exigir(
        hasattr(cadencias, "MEDIDO_EN") and hasattr(cadencias, "VENTANA_MEDIDA"),
        "la tabla no dice cuando ni sobre que ventana se midio",
    )
    antiguedad = (date.today() - date.fromisoformat(cadencias.MEDIDO_EN)).days
    exigir(
        antiguedad <= VIGENCIA_DIAS,
        f"la medicion de cadencias tiene {antiguedad} dias y la vigencia declarada es de"
        f" {VIGENCIA_DIAS}: hay que volver a correr medir_cadencia.py",
    )
    detalles.append(
        f"tabla generada el {cadencias.MEDIDO_EN} sobre {cadencias.VENTANA_MEDIDA[0]}"
        f" a {cadencias.VENTANA_MEDIDA[1]}, {len(cadencias.CADENCIAS_MEDIDAS)} plazas"
    )

    # 2. Cobertura en los dos sentidos.
    for plaza_id in sniim.PILOTO:
        nombre = cadencias.PLAZAS[plaza_id]
        exigir(
            nombre in cadencias.CADENCIAS_MEDIDAS,
            f"la plaza {plaza_id} esta en el piloto y no tiene cadencia medida",
        )
    nombres_catalogo = set(cadencias.PLAZAS.values())
    for nombre in cadencias.CADENCIAS_MEDIDAS:
        exigir(
            nombre in nombres_catalogo,
            f"se declara cadencia de {nombre}, que no esta en el catalogo de la fuente",
        )
    conexion = conectar()
    plazas_base = {
        fila[0]
        for fila in conexion.execute("SELECT DISTINCT mercado FROM precios WHERE fuente = 'SNIIM_FYH'")
    }
    conexion.close()
    for nombre in plazas_base:
        exigir(
            nombre in cadencias.CADENCIAS_MEDIDAS,
            f"hay filas de {nombre} en la base y no tiene cadencia medida",
        )
    detalles.append(
        f"{len(sniim.PILOTO)} plazas del piloto y {len(plazas_base)} con filas, todas con"
        " cadencia medida y presentes en el catalogo"
    )

    # 3. Se vuelve a preguntar a la fuente.
    no_diarias = [
        (plaza_id, nombre)
        for plaza_id, nombre in cadencias.PLAZAS.items()
        if cadencias.CADENCIAS_MEDIDAS.get(nombre, {}).get("cadencia") == "semanal"
    ]
    diarias = [
        (plaza_id, nombre)
        for plaza_id, nombre in sorted(cadencias.PLAZAS.items(), key=lambda par: int(par[0]))
        if cadencias.CADENCIAS_MEDIDAS.get(nombre, {}).get("cadencia") == "diaria"
    ][:MUESTRA_DIARIAS]
    muestra = no_diarias + diarias
    exigir(
        no_diarias,
        "la muestra no incluye ninguna plaza de cadencia no diaria: son las que deciden",
    )

    hasta = date.today()
    desde = hasta - timedelta(days=DIAS_MUESTRA)
    comprobadas = []
    for plaza_id, nombre in muestra:
        pagina = preguntar(medir_cadencia, plaza_id, desde, hasta)
        por_fecha = medir_cadencia.fechas_de(pagina)
        exigir(por_fecha, f"{nombre} no devolvio filas al volver a preguntarle a la fuente")
        medidos = dias_de_la_semana(set(por_fecha))
        bien, motivo = coincide(cadencias.CADENCIAS_MEDIDAS[nombre], medidos, set(por_fecha))
        exigir(bien, f"{nombre}: la cadencia declarada no explica lo que la fuente publica, {motivo}")
        comprobadas.append((nombre, motivo))
    detalles.append(
        f"{len(comprobadas)} plazas vueltas a preguntar a la fuente, "
        f"{len(no_diarias)} de ellas no diarias, todas coinciden"
    )

    if con_control:
        # Control positivo: una cadencia falsa tiene que caerse. Se le miente a
        # la plaza no diaria diciendo que es diaria, y al reves.
        plaza_id, nombre = no_diarias[0]
        pagina = preguntar(medir_cadencia, plaza_id, desde, hasta)
        medidos = dias_de_la_semana(set(medir_cadencia.fechas_de(pagina)))
        falsa = {"cadencia": "diaria", "dias": None, "umbral_dias": 3}
        bien, motivo = coincide(falsa, medidos, set())
        exigir(
            not bien,
            f"la comprobacion acepto que {nombre} fuera diaria cuando publica en"
            f" {sorted(medidos)}: no esta mirando los dias",
        )
        plaza_diaria, nombre_diaria = diarias[0]
        pagina = preguntar(medir_cadencia, plaza_diaria, desde, hasta)
        medidos_diaria = dias_de_la_semana(set(medir_cadencia.fechas_de(pagina)))
        falsa_semanal = {"cadencia": "semanal", "dias": [0], "umbral_dias": 10}
        bien, motivo = coincide(falsa_semanal, medidos_diaria, set())
        exigir(
            not bien,
            f"la comprobacion acepto que {nombre_diaria} publicara solo los lunes cuando"
            f" publica en {sorted(medidos_diaria)}",
        )
        detalles.append(
            "control: rechazada una no diaria declarada diaria y una diaria declarada semanal"
        )

    reparto = collections.Counter(
        valor["cadencia"] for valor in cadencias.CADENCIAS_MEDIDAS.values()
    )
    detalles.append("reparto declarado: " + ", ".join(f"{k} {v}" for k, v in sorted(reparto.items())))
    return detalles


if __name__ == "__main__":
    lector = argparse.ArgumentParser(description="Verifica que la cadencia medida siga siendo cierta")
    lector.add_argument("--control-falso", action="store_true")
    argumentos = lector.parse_args()
    sys.exit(gate_util.correr(lambda: verificar(argumentos.control_falso), MARCADOR))
