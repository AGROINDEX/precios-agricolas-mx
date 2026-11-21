"""B17 · la cadencia de cada plaza esta declarada y su silencio se juzga contra ella.

TRES COSAS, y las tres hacen falta:

1. La cadencia esta DECLARADA en una sola tabla, `comun.CADENCIAS`, y cubre a
   toda plaza que ya tiene filas en la base. Una plaza sin cadencia declarada se
   juzgaria con un umbral inventado.
2. La plaza semanal se sigue consultando los dias que NO le toca publicar. Es
   gasto a proposito: dejar de preguntar es la unica forma de no enterarse el
   dia en que cambie de cadencia.
3. El vigilante falla por la TRANSICION y no por el estado. Se arman cuatro
   plazas de control y se exige un desenlace distinto para cada una. Sin los
   controles, un vigilante que siempre dijera "al dia" pasaria igual, y uno que
   siempre gritara tambien.

Uso:
  python tools/verificar_cadencia.py --control-callada
"""
import argparse
import os
import sys
import tempfile
from datetime import date, timedelta

import gate_util
from gate_util import exigir

MARCADOR = "cadencia verificada · falta en su dia detectada y silencio esperado tolerado"

# Lunes de referencia para armar los controles. Se fija un lunes real para que
# el control no cambie de significado segun el dia en que corra el gate.
LUNES = date(2026, 11, 16)


def sembrar(conexion, mercado, fechas, base=11.0):
    import comun

    filas = []
    for paso, fecha in enumerate(fechas):
        for indice in range(6):
            filas.append(
                {
                    "fuente": "SNIIM_FYH",
                    "fecha_dato": fecha.isoformat(),
                    "hora_dato": None,
                    "categoria": "Hortalizas",
                    "producto": f"Producto {indice}",
                    "calidad": "Primera",
                    "presentacion": "Kilogramo",
                    "origen": "Control",
                    "mercado": mercado,
                    "observaciones": "",
                    "precio_min": base + indice,
                    "precio_max": base + indice + 2,
                    # El valor se mueve en cada corte: asi el control prueba la
                    # cadencia y no se confunde con una plaza estancada.
                    "precio_frec": base + indice + paso,
                    "moneda": "MXN",
                    "base_precio": "kilogramo",
                    "alcance": "mayoreo",
                    "consulta_url": "https://www.economia-sniim.gob.mx/control",
                    "capturado_en": f"{fecha.isoformat()}T12:00:00+00:00",
                }
            )
    comun.guardar(conexion, filas)


def grupo_de(registros):
    return {registro["mercado"] for registro in registros}


def verificar(con_control):
    import comun
    import sniim
    from check_cadencia import evaluar
    from comun import CADENCIAS, cadencia, toca_publicar

    detalles = []

    # 1. Cadencia declarada para toda plaza con filas en la base.
    conexion = comun.conectar()
    plazas = [fila[0] for fila in conexion.execute("SELECT DISTINCT mercado FROM precios")]
    conexion.close()
    exigir(plazas, "no hay ninguna plaza en la base")
    for mercado in plazas:
        exigir(
            mercado in CADENCIAS,
            f"la plaza {mercado} tiene filas y no tiene cadencia declarada en comun.CADENCIAS",
        )
        regla = cadencia(mercado)
        exigir(
            regla["cadencia"] in ("diaria", "semanal"),
            f"{mercado} declara una cadencia que no se sabe juzgar: {regla['cadencia']}",
        )
        exigir(
            regla["umbral_dias"] >= 1,
            f"{mercado} declara un umbral de silencio invalido: {regla['umbral_dias']}",
        )
    detalles.append(f"{len(plazas)} plazas con cadencia declarada y umbral propio")

    # 2. La plaza semanal se consulta tambien los dias que no le toca.
    semanales = [nombre for nombre in CADENCIAS if cadencia(nombre)["cadencia"] == "semanal"]
    exigir(semanales, "ninguna plaza declara cadencia semanal: este gate no esta midiendo nada")
    for nombre in semanales:
        identificadores = [pid for pid, plaza in sniim.PLAZAS.items() if plaza == nombre]
        exigir(identificadores, f"{nombre} declara cadencia y no esta en sniim.PLAZAS")
        exigir(
            identificadores[0] in sniim.PILOTO,
            f"{nombre} no esta en el piloto, asi que no se consulta nunca",
        )
        # Cada plaza semanal tiene SUS dias, que no son los mismos: una publica
        # los lunes y dos publican martes y viernes. Se comprueba contra los
        # dias que ella declara, no contra un lunes fijo.
        propios = set(cadencia(nombre)["dias"])
        ajenos = set(range(7)) - propios
        for dia_propio in propios:
            exigir(
                toca_publicar(nombre, LUNES + timedelta(days=dia_propio)),
                f"{nombre} declara publicar en {dia_propio} y no tiene cita ese dia",
            )
        for dia_ajeno in ajenos:
            exigir(
                not toca_publicar(nombre, LUNES + timedelta(days=dia_ajeno)),
                f"{nombre} no declara el dia {dia_ajeno} y aun asi tiene cita: el control"
                " no prueba nada",
            )
    detalles.append(
        f"{len(semanales)} plaza semanal en el piloto, consultada tambien fuera de su dia"
    )

    if con_control:
        carpeta = tempfile.mkdtemp(prefix="gate_cadencia_")
        base = os.path.join(carpeta, "control.db")
        conexion = comun.conectar(base)

        # Las plazas de control llevan nombre de control y cadencia declarada
        # aqui mismo, en vez de pedir prestado el nombre de una plaza real: asi
        # se lee de un golpe que desenlace se espera de cada una.
        diaria = {"cadencia": "diaria", "dias": None, "umbral_dias": 3}
        semanal = {"cadencia": "semanal", "dias": [0], "umbral_dias": 10}
        jueves = LUNES + timedelta(days=3)
        miercoles = LUNES + timedelta(days=2)

        # a) diaria que cumplio su cita anterior y falto a la ultima: transicion.
        diaria_callada = "Control: plaza diaria que acaba de faltar"
        comun.CADENCIAS[diaria_callada] = diaria
        sembrar(
            conexion,
            diaria_callada,
            [LUNES - timedelta(days=3), LUNES, LUNES + timedelta(days=1)],
        )

        # b) semanal que falto a su lunes: transicion.
        semanal_callada = "Control: plaza semanal sin su lunes"
        comun.CADENCIAS[semanal_callada] = semanal
        sembrar(conexion, semanal_callada, [LUNES - timedelta(days=7 * k) for k in (3, 2, 1)])

        # c) semanal al dia, mirada un jueves: silencio esperado, NO debe fallar.
        semanal_al_dia = "Control: plaza semanal al dia"
        comun.CADENCIAS[semanal_al_dia] = semanal
        sembrar(conexion, semanal_al_dia, [LUNES - timedelta(days=7 * k) for k in (2, 1, 0)])

        # d) semanal callada desde varias semanas: estado conocido, nota y no fallo.
        callada_vieja = "Control: plaza semanal callada desde antes"
        comun.CADENCIAS[callada_vieja] = semanal
        sembrar(conexion, callada_vieja, [LUNES - timedelta(days=7 * k) for k in (5, 4, 3)])

        # e) diaria callada hace varios dias: tambien estado conocido, no fallo.
        diaria_vieja = "Control: plaza diaria callada desde antes"
        comun.CADENCIAS[diaria_vieja] = diaria
        sembrar(conexion, diaria_vieja, [LUNES - timedelta(days=dia) for dia in (7, 6, 5)])

        faltaron, calladas, sanas = evaluar(conexion, jueves)
        conexion.close()

        exigir(
            diaria_callada in grupo_de(faltaron),
            "la plaza diaria callada no fue detectada como falta: cayo en "
            + ("calladas" if diaria_callada in grupo_de(calladas) else "sanas"),
        )
        exigir(
            semanal_callada in grupo_de(faltaron),
            "la plaza semanal que falto a su lunes no fue detectada: cayo en "
            + ("calladas" if semanal_callada in grupo_de(calladas) else "sanas"),
        )
        exigir(
            semanal_al_dia in grupo_de(sanas),
            "la plaza semanal al dia fue reportada como problema un jueves: el vigilante "
            "esta juzgando con el umbral diario",
        )
        for nombre in (callada_vieja, diaria_vieja):
            exigir(
                nombre in grupo_de(calladas),
                f"{nombre} no quedo como nota: un aviso que sale todos los dias es un "
                "aviso que nadie mira",
            )
        # El control tambien tiene que distinguir: si todo cayera en el mismo
        # grupo, las cuatro aserciones de arriba se podrian cumplir por accidente.
        exigir(
            len(grupo_de(faltaron)) == 2 and len(grupo_de(calladas)) >= 2,
            f"los controles no se separaron: {len(grupo_de(faltaron))} faltas y "
            f"{len(grupo_de(calladas))} notas",
        )
        detalles.append(
            f"control: 2 transiciones detectadas (diaria y semanal), semanal al dia tolerada "
            f"mirandola el jueves {jueves.isoformat()}, 2 calladas viejas degradadas a nota"
        )

    return detalles


if __name__ == "__main__":
    lector = argparse.ArgumentParser(description="Verifica la cadencia declarada por plaza")
    lector.add_argument("--control-callada", action="store_true")
    argumentos = lector.parse_args()
    sys.exit(gate_util.correr(lambda: verificar(argumentos.control_callada), MARCADOR))
