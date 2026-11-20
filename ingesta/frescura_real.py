"""Frescura REAL por plaza: cuanto se mueve el dato, no que fecha dice tener.

POR QUE EXISTE. La fecha declarada es la que pone la fuente, y una fuente puede
republicar el mismo numero todos los dias con la fecha de hoy. Medido asi,
Morelia y la Central de Abasto de Iztapalapa parecen igual de frescas. Al
comparar valores aparece la diferencia: en Morelia la mayoria de los productos
no cambia de precio en dos semanas y en Iztapalapa casi todos se mueven. Un
numero que no se mueve en diez dias no describe un mercado estable, describe una
captura que no esta ocurriendo todos los dias.

QUE SE MIDE, por fuente y plaza, sobre la ventana declarada:

  dias_publicados        cuantos dias distintos trae la plaza en la ventana
  cobertura_ultimo       productos con precio en el ultimo corte
  prop_movio_ultimo      proporcion de esos productos cuyo precio frecuente
                         cambio respecto del dia publicado anterior
  mediana_edad_valor     dias desde que cada producto cambio de valor por
                         ultima vez, en mediana. Es la edad REAL del numero
  prop_planos            proporcion de productos que nunca cambiaron de valor
                         en toda la ventana, mirando solo los que tienen al
                         menos `MINIMO_DIAS` dias publicados

QUE NO SE AFIRMA. Que el precio no se mueva no prueba que la fuente no lo
levante: hay productos genuinamente estables, sobre todo los de precio
administrado o los de poca rotacion. Por eso el veredicto se declara como lo que
es, una medida de movimiento, y el umbral queda escrito y a la vista en vez de
escondido en el codigo.

Uso:
  python ingesta/frescura_real.py
  python ingesta/frescura_real.py --json
"""
import argparse
import json
import statistics
import sys
from datetime import datetime

import comun_bootstrap  # noqa: F401
from comun import conectar

# Un producto necesita al menos estos dias publicados para opinar si esta plano.
MINIMO_DIAS = 5

# Umbrales declarados. No son ley: son el punto donde esta medida deja de
# describir un mercado tranquilo y empieza a describir una captura detenida.
PLANOS_ESTANCADA = 0.50
PLANOS_PARCIAL = 0.25
MOVIO_ESTANCADA = 0.05

VEREDICTOS = {
    "viva": "la plaza se mueve",
    "parcial": "la plaza se mueve a medias",
    "estancada": "la plaza casi no se mueve",
    "sin_medir": "todavia sin medir",
}


def series_por_plaza(conexion, hasta=None):
    """Series por plaza y producto, opcionalmente recortadas a una fecha.

    `hasta` existe para poder preguntar que veredicto habria dado esta misma
    medida el dia publicado anterior. Asi la base es su propia memoria y el
    vigilante puede detectar el cambio de estado sin guardar un archivo aparte.
    """
    filas = conexion.execute(
        """
        SELECT fuente, mercado, producto, fecha_dato, AVG(precio_frec)
        FROM precios
        WHERE precio_frec IS NOT NULL AND (? IS NULL OR fecha_dato <= ?)
        GROUP BY fuente, mercado, producto, fecha_dato
        ORDER BY fuente, mercado, producto, fecha_dato
        """,
        (hasta, hasta),
    ).fetchall()
    series = {}
    for fuente, mercado, producto, fecha, valor in filas:
        series.setdefault((fuente, mercado), {}).setdefault(producto, []).append((fecha, valor))
    return series


def medir_plaza(productos):
    """Devuelve las metricas de una plaza a partir de sus series por producto."""
    fechas = sorted({fecha for puntos in productos.values() for fecha, _valor in puntos})
    ultimo = fechas[-1]
    anterior = fechas[-2] if len(fechas) > 1 else None

    movieron = 0
    comparables = 0
    edades = []
    planos = 0
    con_historia = 0

    for puntos in productos.values():
        valores = dict(puntos)
        if ultimo in valores and anterior in valores:
            comparables += 1
            if abs(valores[ultimo] - valores[anterior]) > 0.005:
                movieron += 1

        # Edad del valor: dias desde el ultimo cambio real, contra el ultimo
        # corte de la plaza. Si nunca cambio, la edad es toda su historia.
        ordenados = sorted(puntos)
        if ultimo not in valores:
            continue
        ultimo_cambio = ordenados[0][0]
        for (_fecha_previa, valor_previo), (fecha, valor) in zip(ordenados, ordenados[1:]):
            if abs(valor - valor_previo) > 0.005:
                ultimo_cambio = fecha
        edades.append(
            (
                datetime.strptime(ultimo, "%Y-%m-%d").date()
                - datetime.strptime(ultimo_cambio, "%Y-%m-%d").date()
            ).days
        )

        dias_producto = len({fecha for fecha, _valor in puntos})
        if dias_producto >= MINIMO_DIAS:
            con_historia += 1
            if len({round(valor, 2) for _fecha, valor in puntos}) == 1:
                planos += 1

    prop_movio = movieron / comparables if comparables else None
    prop_planos = planos / con_historia if con_historia else None

    # Con un solo dia publicado no hay movimiento que medir, y llamarle viva
    # seria afirmar lo que no se sabe. Es el caso del visor de la Central de
    # Abasto, que solo publica el corte vigente y apenas empieza a acumular.
    if prop_movio is None or len(fechas) < 2:
        veredicto = "sin_medir"
    elif prop_planos is not None and (
        prop_planos >= PLANOS_ESTANCADA or (prop_movio is not None and prop_movio <= MOVIO_ESTANCADA)
    ):
        veredicto = "estancada"
    elif prop_planos is not None and prop_planos >= PLANOS_PARCIAL:
        veredicto = "parcial"
    else:
        veredicto = "viva"

    return {
        "ultimo_corte": ultimo,
        "dias_publicados": len(fechas),
        "cobertura_ultimo": sum(1 for puntos in productos.values() if ultimo in dict(puntos)),
        "comparables": comparables,
        "movieron": movieron,
        "prop_movio_ultimo": None if prop_movio is None else round(prop_movio, 4),
        "mediana_edad_valor": None if not edades else round(statistics.median(edades), 1),
        "productos_con_historia": con_historia,
        "planos": planos,
        "prop_planos": None if prop_planos is None else round(prop_planos, 4),
        "veredicto": veredicto,
    }


def medir(conexion, hasta=None):
    series = series_por_plaza(conexion, hasta)
    medidas = {}
    for (fuente, mercado), productos in series.items():
        medidas.setdefault(fuente, {})[mercado] = medir_plaza(productos)
    return medidas


def frase(medida):
    """Como se le cuenta esto a quien lee la pagina, sin jerga y sin exagerar."""
    if medida["prop_movio_ultimo"] is None:
        return "sin dia anterior publicado, todavia no se puede medir el movimiento"
    movio = medida["prop_movio_ultimo"] * 100
    partes = [f"{movio:.0f} por ciento de los productos cambio de precio en el ultimo corte"]
    if medida["mediana_edad_valor"] is not None:
        partes.append(f"la mitad de los precios lleva {medida['mediana_edad_valor']:.0f} dias o mas sin moverse")
    if medida["prop_planos"]:
        partes.append(
            f"{medida['prop_planos'] * 100:.0f} por ciento no cambio ni una vez en la ventana"
        )
    return " · ".join(partes)


if __name__ == "__main__":
    lector = argparse.ArgumentParser(description="Mide la frescura real por plaza")
    lector.add_argument("--base")
    lector.add_argument("--json", action="store_true")
    argumentos = lector.parse_args()

    conexion_abierta = conectar(argumentos.base)
    resultado = medir(conexion_abierta)
    conexion_abierta.close()

    if argumentos.json:
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
        sys.exit(0)

    for fuente in sorted(resultado):
        for mercado in sorted(resultado[fuente]):
            medida = resultado[fuente][mercado]
            print(f"{mercado}")
            print(f"   corte {medida['ultimo_corte']} · {medida['dias_publicados']} dias publicados")
            print(f"   {VEREDICTOS[medida['veredicto']]} · {frase(medida)}")
