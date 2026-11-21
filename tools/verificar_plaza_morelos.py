"""B18 · la plaza de Morelos esta en el piloto, dentro de la ventana y en su cadencia.

QUE SE RECUENTA, desde las filas crudas y sin usar el modulo de cadencia:

1. La plaza existe en la base con filas propias y esta en el piloto de la
   ingesta, no solo en el catalogo de plazas.
2. Todos sus dias publicados caen en el dia de la semana que declara su
   cadencia. Un solo dia fuera significa que la cadencia declarada es falsa, y
   una cadencia falsa es peor que ninguna: el vigilante juzgaria el silencio
   contra una cita equivocada.
3. Ningun dia excede la ventana declarada de la fuente, que es lo que el
   articulo 108 obliga.
4. Toda fila trae base de precio por kilogramo, que es lo que permite
   compararla contra las otras plazas sin inventar una conversion.

CONTROL POSITIVO OBLIGATORIO. La comprobacion 2 es una ausencia: "no hay ningun
dia fuera de su cadencia". Se le mete un martes a una copia en memoria y se
exige que la misma comprobacion lo rechace. Sin eso, una comprobacion que
nunca mirara las fechas pasaria igual.

Uso:
  python tools/verificar_plaza_morelos.py
"""
import sys
from datetime import date, datetime

import gate_util
from gate_util import exigir

MARCADOR = "plaza de Morelos verificada · dias publicados dentro de la ventana y en su cadencia"

PLAZA = 'Morelos: Mercado "Adolfo López Mateos" de Cuernavaca'
CLAVE = "SNIIM_FYH"

# Minimo para que la plaza aporte algo. Once publicaciones semanales son casi
# tres meses; por debajo de seis no hay con que mirar una tendencia.
MINIMO_PUBLICACIONES = 6


def dias_fuera_de_cadencia(fechas, dias_declarados):
    """Dias publicados que NO caen en la cadencia declarada. Funcion pura."""
    return [
        fecha
        for fecha in fechas
        if date.fromisoformat(fecha).weekday() not in dias_declarados
    ]


def verificar():
    import comun
    import sniim
    from comun import FUENTES, cadencia

    detalles = []

    identificadores = [pid for pid, nombre in sniim.PLAZAS.items() if nombre == PLAZA]
    exigir(identificadores, f"{PLAZA} no esta en sniim.PLAZAS")
    exigir(
        identificadores[0] in sniim.PILOTO,
        f"{PLAZA} esta en el catalogo pero no en el piloto: la ingesta diaria no la toca",
    )
    detalles.append(f"plaza {identificadores[0]} en el piloto de la ingesta")

    regla = cadencia(PLAZA)
    exigir(
        regla["cadencia"] == "semanal" and regla["dias"],
        f"{PLAZA} no declara cadencia semanal con dias: declara {regla}",
    )

    conexion = comun.conectar()
    fechas = [
        fila[0]
        for fila in conexion.execute(
            "SELECT DISTINCT fecha_dato FROM precios WHERE fuente = ? AND mercado = ?"
            " ORDER BY fecha_dato",
            (CLAVE, PLAZA),
        )
    ]
    total, con_precio, bases = conexion.execute(
        "SELECT COUNT(*), SUM(CASE WHEN precio_frec IS NOT NULL THEN 1 ELSE 0 END),"
        " COUNT(DISTINCT base_precio) FROM precios WHERE fuente = ? AND mercado = ?",
        (CLAVE, PLAZA),
    ).fetchone()
    base_declarada = conexion.execute(
        "SELECT DISTINCT base_precio FROM precios WHERE fuente = ? AND mercado = ?",
        (CLAVE, PLAZA),
    ).fetchall()
    conexion.close()

    exigir(fechas, f"{PLAZA} no tiene ninguna fila en la base")
    exigir(
        len(fechas) >= MINIMO_PUBLICACIONES,
        f"{PLAZA} trae {len(fechas)} publicaciones y el minimo util es {MINIMO_PUBLICACIONES}",
    )
    exigir(total > 0 and con_precio > 0, f"{PLAZA} no trae ninguna fila con precio frecuente")
    exigir(
        bases == 1 and base_declarada[0][0] == "kilogramo",
        f"{PLAZA} mezcla bases de precio o no declara kilogramo: {base_declarada}",
    )

    fuera = dias_fuera_de_cadencia(fechas, set(regla["dias"]))
    exigir(
        not fuera,
        f"{PLAZA} publico en dias que su cadencia declarada no contempla: {fuera[:5]}."
        " La cadencia declarada es falsa y el vigilante juzgaria contra una cita equivocada",
    )

    ventana = FUENTES[CLAVE]["ventana_dias"]
    antiguedad = (date.today() - date.fromisoformat(fechas[0])).days
    exigir(
        antiguedad <= ventana,
        f"{PLAZA} guarda {antiguedad} dias de profundidad y la ventana declarada es"
        f" de {ventana}: eso ya es espejo del acervo",
    )

    nombres = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]
    dias_nombrados = " y ".join(nombres[dia] for dia in regla["dias"])
    detalles.append(
        f"{len(fechas)} publicaciones entre {fechas[0]} y {fechas[-1]}, todas en {dias_nombrados}"
    )
    detalles.append(
        f"{total} filas, {con_precio} con precio frecuente, base kilogramo,"
        f" profundidad {antiguedad} dias dentro de la ventana de {ventana}"
    )

    # Control positivo de la comprobacion de cadencia: un martes metido a mano
    # tiene que ser rechazado por la misma funcion.
    martes = (
        datetime.strptime(fechas[-1], "%Y-%m-%d").date().toordinal() + 1
    )
    fecha_martes = date.fromordinal(martes).isoformat()
    exigir(
        date.fromisoformat(fecha_martes).weekday() not in set(regla["dias"]),
        "el control positivo no quedo fuera de la cadencia: no prueba nada",
    )
    rechazo = dias_fuera_de_cadencia(fechas + [fecha_martes], set(regla["dias"]))
    exigir(
        rechazo == [fecha_martes],
        f"la comprobacion de cadencia no rechazo el dia de control {fecha_martes}:"
        f" devolvio {rechazo}",
    )
    detalles.append(f"control positivo: el dia {fecha_martes} fuera de cadencia fue rechazado")
    return detalles


if __name__ == "__main__":
    sys.exit(gate_util.correr(verificar, MARCADOR))
