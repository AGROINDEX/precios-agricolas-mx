"""Vigilante POR PLAZA: avisa cuando una plaza falta a su propio dia.

POR QUE EXISTE, Y POR QUE NO LO CUBRE check_fuentes_stale.py. Ese vigilante
mide por FUENTE: dias desde el ultimo fetch bueno del SNIIM entero. Mientras
Iztapalapa publique, el SNIIM se ve sano aunque una plaza lleve un ano muerta.
Es exactamente como murio la Central de Abasto de Cuautla, el 16 de octubre de
2025, sin que nadie lo notara.

POR QUE SE JUZGA CONTRA LA CADENCIA DECLARADA. Una plaza semanal calla seis dias
de siete, y eso no es una falla: es su cadencia. Juzgarla con el umbral diario
la declararia muerta cada martes, y una alerta que sale siempre es una alerta
que nadie mira. La cadencia vive declarada en `comun.CADENCIAS`, a la vista y no
escondida en una condicion.

QUE INTERRUMPE Y QUE NO. Igual que check_plazas_quietas.py, lo que interrumpe es
la TRANSICION: el dia en que una plaza que cumplio su ultima cita falta a la
siguiente. El silencio que ya se conocia se reporta como nota. El silencio
prolongado no se queda solo en el log: la pagina lo dice en la cara del usuario
con los dias que lleva sin publicar, que es donde alguien lo va a leer.

CODIGOS DE SALIDA
  1  alguna plaza falto a su cita por primera vez
  0  todas al dia, o calladas desde antes

Uso:
  python ingesta/check_cadencia.py
  python ingesta/check_cadencia.py --base otra.db --hoy 2026-11-20
"""
import argparse
import sys
from datetime import date, datetime, timedelta

import comun_bootstrap  # noqa: F401
from comun import cadencia, conectar, frase_cadencia, toca_publicar

for _flujo in (sys.stdout, sys.stderr):
    try:
        _flujo.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

# Cuantos dias hacia atras se cuentan las citas, para poder decir "cumplio 11 de
# 13" en vez de un si o no que esconde la intermitencia.
VENTANA_CITAS = 90


def citas(mercado, hasta, desde):
    """Dias en que a esta plaza le tocaba publicar, de mas nuevo a mas viejo."""
    salida = []
    dia = hasta
    while dia >= desde:
        if toca_publicar(mercado, dia):
            salida.append(dia)
        dia -= timedelta(days=1)
    return salida


def evaluar(conexion, hoy=None):
    hoy = hoy or date.today()
    desde = hoy - timedelta(days=VENTANA_CITAS)
    filas = conexion.execute(
        "SELECT fuente, mercado, MAX(fecha_dato), MIN(fecha_dato) FROM precios"
        " GROUP BY fuente, mercado"
    ).fetchall()

    faltaron, calladas, sanas = [], [], []
    for fuente, mercado, ultimo, primero in filas:
        regla = cadencia(mercado)
        publicados = {
            fila[0]
            for fila in conexion.execute(
                "SELECT DISTINCT fecha_dato FROM precios WHERE fuente = ? AND mercado = ?",
                (fuente, mercado),
            )
        }
        # Las citas se cuentan desde que ESTA ingesta empezo a mirar la plaza,
        # no desde hace noventa dias. Contar antes mide nuestra antiguedad y no
        # el cumplimiento de la plaza: la Central de Abasto llevaria un dia
        # ingestado y apareceria como que falto a sesenta y tres citas.
        inicio = max(desde, datetime.strptime(primero, "%Y-%m-%d").date())
        agenda = citas(mercado, hoy, inicio)
        # La cita de hoy no se juzga: la ingesta corre a las 13:00 UTC y la
        # fuente puede publicar mas tarde. La primera cita juzgable es la
        # anterior a hoy.
        juzgables = [dia for dia in agenda if dia < hoy]
        cumplidas = [dia for dia in juzgables if dia.isoformat() in publicados]
        dias_sin = (hoy - datetime.strptime(ultimo, "%Y-%m-%d").date()).days

        registro = {
            "fuente": fuente,
            "mercado": mercado,
            "cadencia": regla["cadencia"],
            "ultimo": ultimo,
            "dias_sin_publicar": dias_sin,
            "umbral": regla["umbral_dias"],
            "citas": len(juzgables),
            "cumplidas": len(cumplidas),
            "frase": frase_cadencia(mercado),
        }

        if not juzgables:
            sanas.append(registro)
            continue

        ultima_cita = juzgables[0]
        cumplio_ultima = ultima_cita.isoformat() in publicados
        anterior = juzgables[1] if len(juzgables) > 1 else None
        cumplio_anterior = bool(anterior) and anterior.isoformat() in publicados
        registro["ultima_cita"] = ultima_cita.isoformat()

        if cumplio_ultima:
            sanas.append(registro)
        elif cumplio_anterior:
            # Transicion: cumplio la cita anterior y falto a la ultima.
            faltaron.append(registro)
        else:
            # Ya estaba callada antes de hoy. Nota, no interrupcion.
            calladas.append(registro)
    return faltaron, calladas, sanas


def main():
    lector = argparse.ArgumentParser(description="Avisa cuando una plaza falta a su propio dia")
    lector.add_argument("--base")
    lector.add_argument("--hoy", help="fecha de referencia, para control positivo")
    argumentos = lector.parse_args()

    hoy = datetime.strptime(argumentos.hoy, "%Y-%m-%d").date() if argumentos.hoy else None
    conexion = conectar(argumentos.base)
    faltaron, calladas, sanas = evaluar(conexion, hoy)
    conexion.close()

    for r in sanas:
        print(
            f"ok      {r['mercado']} · corte {r['ultimo']} · {r['frase']} · "
            f"cumplio {r['cumplidas']} de {r['citas']} citas"
        )
    for r in calladas:
        print(
            f"::notice::plaza callada desde antes {r['mercado']} · {r['dias_sin_publicar']} dias "
            f"sin publicar · {r['frase']} · cumplio {r['cumplidas']} de {r['citas']} citas"
        )
    for r in faltaron:
        print(
            f"::error::plaza falto a su cita {r['mercado']} · le tocaba el {r['ultima_cita']} "
            f"y su ultimo corte es del {r['ultimo']} · {r['frase']} · "
            f"cumplio {r['cumplidas']} de {r['citas']} citas"
        )

    if faltaron:
        print(f"PLAZAS QUE FALTARON A SU CITA: {len(faltaron)}")
        return 1
    print(
        f"cadencia verificada · {len(sanas)} plazas al dia · "
        f"{len(calladas)} calladas desde antes"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
