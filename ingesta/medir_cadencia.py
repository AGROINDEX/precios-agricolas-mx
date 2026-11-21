"""Mide la cadencia real de cada plaza y GENERA la tabla declarada.

POR QUE SE GENERA Y NO SE ESCRIBE A MANO. Con tres plazas, escribir la cadencia
a mano era razonable. Con 41 es una invitacion al error, y una cadencia
declarada mal es peor que ninguna: el vigilante juzgaria el silencio contra una
cita equivocada y daria por muerta una plaza viva, o por viva una muerta. La
tabla sale de medir, y un gate comprueba que lo declarado sigue coincidiendo
con lo que la fuente publica.

QUE MIDE, por plaza, con UNA sola peticion de rango por plaza:

  dias_publicados   cuantos dias distintos trae en la ventana
  dias_semana       en que dias de la semana publica
  filas             cuantas filas trae en la ventana
  ultimo            su ultimo dia con dato

COMO DECIDE LA CADENCIA. Si publica en 5 dias de la semana distintos, es
diaria. Si publica en 1 o 2 dias fijos y cubre al menos el 60 por ciento de las
ocasiones en que esos dias ocurrieron, es semanal con esos dias. Si no publica
nada, queda sin cadencia y entra a vigilancia de reaparicion. Cualquier otro
caso se marca como irregular y NO se declara: declarar una cadencia que no se
entiende es justo lo que este modulo existe para evitar.

Uso:
  python ingesta/medir_cadencia.py                 # mide e imprime el resumen
  python ingesta/medir_cadencia.py --escribir      # reescribe ingesta/cadencias.py
  python ingesta/medir_cadencia.py --dias 90 --hilos 4
"""
import argparse
import collections
import re
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta

import comun_bootstrap  # noqa: F401
from comun import FUENTES, traer

for _flujo in (sys.stdout, sys.stderr):
    try:
        _flujo.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass

CLAVE = "SNIIM_FYH"
FORMULARIO = (
    "https://www.economia-sniim.gob.mx/Nuevo/Consultas/MercadosNacionales/"
    "PreciosDeMercado/Agricolas/ConsultaFrutasYHortalizas.aspx"
)
DESTINO = "ingesta/cadencias.py"

# Cuatro hilos. La fuente no declara limite de tasa y no se detecto bloqueo,
# pero es un IIS de 2003 y la cortesia es parte de poder seguir usandola.
HILOS = 4

# Proporcion de citas cumplidas para aceptar una cadencia semanal. Debajo de
# esto la plaza es irregular y no se le declara cadencia.
UMBRAL_REGULARIDAD = 0.60

NOMBRES_DIA = ["lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo"]


def limpiar(fragmento):
    import html

    texto = html.unescape(re.sub(r"<[^>]+>", " ", fragmento))
    return re.sub(r"\s+", " ", texto.replace("\xa0", " ")).strip()


def catalogo():
    """Las plazas del desplegable real, no una lista escrita a mano."""
    pagina = traer(FORMULARIO)
    bloque = re.search(r'name="ddlDestino"[^>]*>(.*?)</select>', pagina, re.S | re.I)
    if not bloque:
        raise SystemExit("no se encontro el desplegable de plazas en el formulario")
    salida = {}
    for valor, etiqueta in re.findall(
        r'<option[^>]*value="([^"]*)"[^>]*>(.*?)</option>', bloque.group(1), re.S
    ):
        if valor in ("", "-1"):
            continue
        salida[valor] = limpiar(etiqueta)
    return salida


def url_rango(plaza_id, desde, hasta):
    """Una peticion por plaza para toda la ventana.

    El parametro Destino, el del nombre, es decorativo: el servidor rotula la
    plaza a partir de DestinoId. Se manda fijo para no depender del nombre.
    """
    return (
        FUENTES[CLAVE]["url_base"]
        + f"?fechaInicio={desde.strftime('%d/%m/%Y')}&fechaFinal={hasta.strftime('%d/%m/%Y')}"
        + "&ProductoId=-1&OrigenId=-1&Origen=Todos"
        + f"&DestinoId={plaza_id}&Destino=Todos"
        + "&PreciosPorId=2&RegistrosPorPagina=100000"
    )


def fechas_de(pagina):
    """Dias publicados y filas, leyendo la tabla con columna Fecha."""
    por_fecha = collections.Counter()
    for tabla in re.findall(r"<table.*?</table>", pagina, re.S | re.I):
        filas = re.findall(r"<tr.*?</tr>", tabla, re.S | re.I)
        if len(filas) < 2:
            continue
        encabezado = [limpiar(c) for c in re.findall(r"<t[dh].*?</t[dh]>", filas[0], re.S | re.I)]
        if not encabezado or not encabezado[0].lower().startswith("fecha"):
            continue
        for fila in filas[1:]:
            celdas = [limpiar(c) for c in re.findall(r"<t[dh].*?</t[dh]>", fila, re.S | re.I)]
            if len(celdas) < 8 or not re.match(r"\d{2}/\d{2}/\d{4}", celdas[0]):
                continue
            dia, mes, anio = celdas[0].split("/")
            por_fecha[f"{anio}-{mes}-{dia}"] += 1
    return por_fecha


def ocasiones(dias_semana, desde, hasta):
    """Cuantas veces ocurrieron esos dias de la semana en la ventana."""
    total = 0
    dia = desde
    while dia <= hasta:
        if dia.weekday() in dias_semana:
            total += 1
        dia += timedelta(days=1)
    return total


def clasificar(fechas, desde, hasta):
    """Devuelve (cadencia, dias, umbral, nota). Nunca inventa una cadencia."""
    if not fechas:
        return "muerta", None, 3, "sin una sola fila en la ventana"

    cuenta = collections.Counter(date.fromisoformat(f).weekday() for f in fechas)
    presentes = sorted(cuenta)

    if len(presentes) >= 5:
        return "diaria", None, 3, f"{len(fechas)} dias en {len(presentes)} dias de la semana"

    if len(presentes) <= 2:
        posibles = ocasiones(set(presentes), desde, hasta)
        regularidad = len(fechas) / posibles if posibles else 0
        etiqueta = " y ".join(NOMBRES_DIA[d] for d in presentes)
        if regularidad >= UMBRAL_REGULARIDAD:
            # Una plaza de dos dias fijos sigue tolerando una semana saltada:
            # el umbral se calcula sobre el hueco esperado mas tres dias.
            hueco = 7 // max(1, len(presentes))
            return "semanal", presentes, hueco + 7 + 3, (
                f"{len(fechas)} de {posibles} ocasiones en {etiqueta}, "
                f"regularidad {regularidad:.0%}"
            )
        return "irregular", None, 10, (
            f"solo {len(fechas)} de {posibles} ocasiones en {etiqueta}, "
            f"regularidad {regularidad:.0%}"
        )

    return "irregular", None, 10, f"{len(fechas)} dias repartidos en {len(presentes)} dias de la semana"


def medir(dias=90, hilos=HILOS):
    plazas = catalogo()
    hasta = date.today()
    desde = hasta - timedelta(days=dias)

    def una(par):
        plaza_id, nombre = par
        try:
            pagina = traer(url_rango(plaza_id, desde, hasta), tiempo=180)
        except Exception as fallo:  # noqa: BLE001
            return plaza_id, nombre, None, f"{type(fallo).__name__}"
        return plaza_id, nombre, fechas_de(pagina), None

    resultados = []
    with ThreadPoolExecutor(max_workers=hilos) as ejecutor:
        for plaza_id, nombre, por_fecha, error in ejecutor.map(una, sorted(plazas.items())):
            if error:
                resultados.append(
                    {
                        "id": plaza_id, "nombre": nombre, "cadencia": "error",
                        "dias": None, "umbral": 3, "nota": error,
                        "dias_publicados": 0, "filas": 0, "ultimo": None,
                    }
                )
                continue
            cadencia, dias_semana, umbral, nota = clasificar(set(por_fecha), desde, hasta)
            resultados.append(
                {
                    "id": plaza_id,
                    "nombre": nombre,
                    "cadencia": cadencia,
                    "dias": dias_semana,
                    "umbral": umbral,
                    "nota": nota,
                    "dias_publicados": len(por_fecha),
                    "filas": sum(por_fecha.values()),
                    "ultimo": max(por_fecha) if por_fecha else None,
                }
            )
    return sorted(resultados, key=lambda r: -r["filas"]), desde, hasta


def escribir(resultados, desde, hasta, destino=DESTINO):
    import os

    from comun import RAIZ

    ruta = os.path.join(RAIZ, destino) if not os.path.isabs(destino) else destino
    vivas = [r for r in resultados if r["cadencia"] in ("diaria", "semanal")]
    otras = [r for r in resultados if r["cadencia"] not in ("diaria", "semanal")]
    por_nombre = sorted(resultados, key=lambda r: r["nombre"])

    lineas = [
        '"""Catalogo de plazas y cadencia declarada. ARCHIVO GENERADO, no editar a mano.',
        "",
        "Lo genera `python ingesta/medir_cadencia.py --escribir` midiendo la fuente.",
        f"Medicion del {hasta.isoformat()} sobre la ventana {desde.isoformat()} a"
        f" {hasta.isoformat()}.",
        "",
        "Los nombres son los del desplegable de la fuente, con sus acentos y sus",
        "comillas, porque son la clave con la que se guardan las filas. Inventarles",
        "una version limpia obligaria a mantener una traduccion a mano, que es",
        "exactamente lo que este archivo existe para evitar.",
        "",
        "Se declara la cadencia solo cuando la medicion la entiende. Una plaza",
        "irregular queda sin declarar a proposito: inventarle una cita haria que el",
        "vigilante la juzgara contra un dia equivocado.",
        '"""',
        "",
        f"MEDIDO_EN = {hasta.isoformat()!r}",
        f"VENTANA_MEDIDA = ({desde.isoformat()!r}, {hasta.isoformat()!r})",
        "",
        "# Todas las plazas del desplegable, vivas y muertas.",
        "PLAZAS = {",
    ]
    for registro in sorted(resultados, key=lambda r: int(r["id"])):
        lineas.append(f'    {registro["id"]!r}: {registro["nombre"]!r},')
    lineas.append("}")
    lineas.append("")
    lineas.append("# plaza -> cadencia, dias de la semana (lunes 0), umbral de silencio en dias")
    lineas.append("CADENCIAS_MEDIDAS = {")
    for registro in por_nombre:
        if registro["cadencia"] not in ("diaria", "semanal"):
            continue
        lineas.append(
            f'    # {registro["id"]} · {registro["nota"]} · {registro["filas"]} filas'
        )
        lineas.append(f'    {registro["nombre"]!r}: {{')
        lineas.append(f'        "cadencia": {registro["cadencia"]!r},')
        lineas.append(f'        "dias": {registro["dias"]!r},')
        lineas.append(f'        "umbral_dias": {registro["umbral"]},')
        lineas.append("    },")
    lineas.append("}")
    lineas.append("")
    lineas.append("# Plazas del catalogo sin cadencia declarable, con su motivo medido.")
    lineas.append("SIN_CADENCIA = {")
    for registro in por_nombre:
        if registro["cadencia"] in ("diaria", "semanal"):
            continue
        lineas.append(
            f'    {registro["nombre"]!r}: ({registro["cadencia"]!r}, {registro["nota"]!r}),'
        )
    lineas.append("}")
    lineas.append("")
    lineas.append("# Plazas que se ingieren. Son las que publicaron en la ventana medida.")
    lineas.append("PILOTO = [")
    for registro in sorted(vivas, key=lambda r: -r["filas"]):
        lineas.append(f'    {registro["id"]!r},  # {registro["nombre"][:56]}')
    lineas.append("]")
    lineas.append("")
    lineas.append("# Plazas que no publican nada y se consultan solo para notar si vuelven.")
    lineas.append("# De estas no se guardan filas: se guarda el INTENTO, en sondas.py.")
    lineas.append("VIGILANCIA = [")
    for registro in sorted(otras, key=lambda r: int(r["id"])):
        lineas.append(f'    {registro["id"]!r},  # {registro["nombre"][:56]}')
    lineas.append("]")
    lineas.append("")
    with open(ruta, "w", encoding="utf-8") as archivo:
        archivo.write("\n".join(lineas))
    return ruta


if __name__ == "__main__":
    lector = argparse.ArgumentParser(description="Mide la cadencia real de cada plaza")
    lector.add_argument("--dias", type=int, default=90)
    lector.add_argument("--hilos", type=int, default=HILOS)
    lector.add_argument("--escribir", action="store_true")
    argumentos = lector.parse_args()

    ventana = FUENTES[CLAVE]["ventana_dias"]
    if argumentos.dias > ventana:
        raise SystemExit(f"--dias {argumentos.dias} excede la ventana declarada de {ventana}")

    filas, desde, hasta = medir(argumentos.dias, argumentos.hilos)
    resumen = collections.Counter(r["cadencia"] for r in filas)
    print(f"ventana {desde} a {hasta} · {len(filas)} plazas del catalogo")
    print(f"{'id':>4s} {'cadencia':10s} {'dias':>5s} {'filas':>7s} {'ultimo':12s} plaza")
    for r in filas:
        print(
            f"{r['id']:>4s} {r['cadencia']:10s} {r['dias_publicados']:5d} {r['filas']:7d} "
            f"{(r['ultimo'] or '-'):12s} {r['nombre'][:46]}"
        )
    print()
    for cadencia, cuantas in sorted(resumen.items()):
        print(f"  {cadencia}: {cuantas}")
    print(f"  filas totales en la ventana: {sum(r['filas'] for r in filas)}")

    if argumentos.escribir:
        ruta = escribir(filas, desde, hasta)
        print(f"\ntabla escrita en {ruta}")
