"""Construye la pagina de precios de hoy, con frescura y atribucion por fila.

LO QUE LA PAGINA DICE Y LO QUE NO. Dice mayoreo en central de abasto, con el
alcance pegado al numero, porque es lo que el dato mide. No dice precio en
finca, no promete precio de transaccion y no dibuja velas: no hay hora, volumen
ni calidad homogenea que las sostenga, y un comprador profesional lo detecta de
inmediato.

UNA PAGINA POR PLAZA, Y UN INDICE. Con 42 plazas por unas sesenta cotizaciones
por una grafica cada una, una sola pagina serian del orden de 2,500 SVG en
linea y varios megabytes. El indice lleva una fila por plaza, con su corte, su
cadencia y su veredicto de movimiento, que es lo que de verdad hacia falta: ver
de un golpe quien publico hoy y quien no. El detalle con graficas vive en la
pagina de cada plaza.

FRESCURA EN LA CARA DEL USUARIO. Si una fuente se congelo, la pagina lo dice
arriba y marca sus filas, en vez de mostrar el ultimo dato bueno como si fuera
de hoy. El veredicto de congelamiento no se inventa aqui: lo da el mismo
vigilante que corre en CI.

Uso:
  python web/construir.py
  python web/construir.py --reporte fixtures/pista_b/fetch_report_congelado.json --salida /tmp/x.html
"""
import argparse
import html
import json
import os
import re
import sys
import unicodedata
from datetime import date, datetime, timezone

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "ingesta"))

from check_cadencia import evaluar as evaluar_cadencia  # noqa: E402
from check_reaparicion import evaluar as evaluar_reaparicion  # noqa: E402
from check_fuentes_stale import evaluar  # noqa: E402
from frescura_real import VEREDICTOS, frase, medir  # noqa: E402
import sondas  # noqa: E402
from cadencias import PLAZAS as PLAZAS_CATALOGO  # noqa: E402
from comun import conectar, frase_cadencia  # noqa: E402
from grafica import ESTILO_GRAFICA, grafica  # noqa: E402

SALIDA = os.path.join(RAIZ, "web", "index.html")
CARPETA_PLAZAS = "plaza"

# Presupuesto declarado de peso por pagina. No es estetico: una pagina de varios
# megabytes en una conexion de campo no se abre, y el 78 por ciento de este peso
# son graficas en linea.
PRESUPUESTO_KIB = 700
REPORTE = os.path.join(RAIZ, "datos", "pista_b", "_fetch_report.json")

ESTILO = """
:root { color-scheme: light dark; --tinta: #16211c; --papel: #fbfaf7; --borde: #d8d4cb;
        --suave: #6b6b63; --alerta: #8a2b14; --alerta-fondo: #fdeee9; --acento: #1f5c3d; }
@media (prefers-color-scheme: dark) { :root { --tinta: #eef0ec; --papel: #14161a;
        --borde: #343a41; --suave: #9aa0a6; --alerta: #ffb59c; --alerta-fondo: #3a1d14;
        --acento: #86d0a5; } }
* { box-sizing: border-box; }
body { margin: 0; padding: 0 16px 64px; background: var(--papel); color: var(--tinta);
       font: 16px/1.55 ui-sans-serif, system-ui, -apple-system, "Segoe UI", sans-serif; }
main { max-width: 1040px; margin: 0 auto; }
h1 { font-size: clamp(1.5rem, 4vw, 2rem); margin: 32px 0 4px; letter-spacing: -0.015em; }
h2 { font-size: 1.1rem; margin: 40px 0 6px; }
p.sub, p.nota { color: var(--suave); margin: 4px 0 0; font-size: 0.92rem; }
.aviso { border: 1px solid var(--alerta); background: var(--alerta-fondo); color: var(--alerta);
         padding: 12px 14px; border-radius: 10px; margin: 20px 0; font-size: 0.95rem; }
.alcance { display: inline-block; border: 1px solid var(--borde); border-radius: 999px;
           padding: 1px 9px; font-size: 0.78rem; color: var(--suave); }
.envoltura { overflow-x: auto; -webkit-overflow-scrolling: touch; }
table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 0.9rem;
        min-width: 560px; }
th, td { text-align: left; padding: 7px 8px; border-bottom: 1px solid var(--borde);
         vertical-align: top; }
th { font-weight: 600; font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.04em;
     color: var(--suave); }
td.num { text-align: right; font-variant-numeric: tabular-nums; white-space: nowrap; }
td.historia { padding: 3px 8px; }
.grafica { color: #2f6fae; }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) .grafica { color: #76b2e8; } }
.sin-serie { color: var(--suave); font-size: 0.74rem; }
tr.rancia td { opacity: 0.55; }
.marca-rancia { color: var(--alerta); font-size: 0.78rem; }
.pulso { display: inline-block; border-radius: 999px; padding: 1px 9px; font-size: 0.78rem;
         border: 1px solid var(--borde); }
.pulso.viva { border-color: var(--acento); color: var(--acento); }
.pulso.parcial { border-color: #9a7b12; color: #9a7b12; }
.pulso.estancada { border-color: var(--alerta); color: var(--alerta); }
@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) .pulso.parcial {
         border-color: #d8b544; color: #d8b544; } }
.sube { color: var(--alerta); } .baja { color: var(--acento); }
footer { margin-top: 48px; border-top: 1px solid var(--borde); padding-top: 14px;
         color: var(--suave); font-size: 0.85rem; }
@media (max-width: 720px) { .oculta-chico { display: none; } }
"""


def escapar(valor):
    return html.escape("" if valor is None else str(valor))


def pesos(valor):
    return "" if valor is None else f"{valor:,.2f}"


def archivo_de_plaza(clave, mercado, ids):
    """Nombre estable para la pagina de una plaza.

    Se usa el id del catalogo cuando existe, porque es lo unico que la fuente
    garantiza estable: el nombre lleva acentos y comillas y puede cambiar de
    redaccion sin avisar.
    """
    plaza_id = ids.get(mercado)
    if plaza_id:
        return f"{CARPETA_PLAZAS}/{plaza_id}.html"
    base = unicodedata.normalize("NFKD", mercado).encode("ascii", "ignore").decode()
    base = re.sub(r"[^A-Za-z0-9]+", "-", base).strip("-").lower()[:40]
    return f"{CARPETA_PLAZAS}/{clave.lower()}-{base}.html"


def cabeza(titulo, subir=False):
    raiz = "../" if subir else ""
    return [
        "<!doctype html>",
        '<html lang="es"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        f"<title>{escapar(titulo)}</title>",
        f"<style>{ESTILO}{ESTILO_GRAFICA}</style></head><body><main>",
        (
            f'<p class="nota"><a href="{raiz}index.html">volver al indice de plazas</a></p>'
            if subir
            else ""
        ),
    ]


def pie_comun(fuentes, con_graficas):
    partes = ["<footer>"]
    partes.append(
        "<p>La etiqueta de movimiento de cada plaza compara el valor de cada producto contra el "
        "dia publicado anterior y cuenta cuantos dias lleva sin cambiar. Una plaza marcada como "
        "que casi no se mueve no afirma que la fuente haya dejado de levantar el dato: afirma "
        "que sus numeros llevan dias quietos, y que conviene tomarlos como referencia gruesa. "
        "Se marca asi cuando la mitad o mas de sus productos no cambio ni una vez en la ventana, "
        "o cuando menos del cinco por ciento se movio en el ultimo corte.</p>"
    )
    partes.append(
        "<p>Cada plaza publica a su propio ritmo y ese ritmo esta MEDIDO, no adivinado: se mide "
        "consultando la ventana completa de cada plaza y contando en que dias de la semana "
        "publica. De las plazas que se siguen, la mayoria publica cada dia habil, una publica "
        "los lunes y dos publican martes y viernes. Por eso el aviso de que una plaza falto a su "
        "publicacion se juzga contra su propia cadencia: una plaza semanal callada un jueves "
        "esta al dia, y la misma plaza callada un lunes no lo esta. Para una plaza semanal, la "
        "antiguedad de los precios se cuenta en publicaciones y no en dias, porque un precio que "
        "cambio en la ultima publicacion no esta detenido aunque tenga siete dias.</p>"
    )
    partes.append(
        "<p>Los dias festivos no se adivinan con un calendario, se leen de la fuente: un dia en "
        "que ninguna plaza publico es un dia en que la fuente no publico, y entonces no se le "
        "reclama a nadie. En esta ventana hubo tres de esos dias.</p>"
    )
    partes.append(
        "<p>Una advertencia que importa al comparar plazas: el SNIIM publica el precio por "
        "kilogramo calculado y la Central de Abasto lo publica por presentacion comercial. "
        "Una caja de nueve kilos a 310 pesos y un kilogramo a 34.44 pesos son el mismo precio. "
        "Cada plaza dice sobre que base esta cotizada. Y la presentacion importa aunque la base "
        "sea la misma: una pieza contra un kilogramo no se compara, porque la fuente no pudo "
        "convertirla.</p>"
    )
    if con_graficas:
        partes.append(
            "<p>La grafica une el precio frecuente de cada dia publicado dentro de la ventana, un "
            "valor por dia, con la dispersion del mismo dia en gris detras. El eje son dias "
            "publicados y no dias de calendario: un domingo sin publicacion no deja hueco ni se "
            "rellena con el valor del viernes. No son velas: no existe apertura, cierre, maximo "
            "intradia ni volumen que las sostengan.</p>"
        )
    partes.append(
        "<p>La variacion contra el dia publicado anterior y la amplitud relativa son calculo "
        "propio sobre la ventana, no dato de la fuente. El precio puntual se cita con su fecha "
        "y su fuente, y el acervo historico completo se consulta en la fuente, que es quien lo "
        "elaboro.</p>"
    )
    for clave in sorted(fuentes):
        fuente = fuentes[clave]
        partes.append(
            f"<p>{escapar(fuente['atribucion'])} · consulta: "
            f'<a href="{escapar(fuente["url"])}">{escapar(fuente["url"])}</a></p>'
        )
    partes.append(
        "<p>Sin graficas de velas a proposito: el dato publicado no trae hora, volumen ni "
        "calidad homogenea que las sostengan.</p>"
    )
    partes.append("</footer></main></body></html>")
    return partes


def aviso_congelada(clave, registro, nombre):
    dias = "nunca" if registro["dias"] is None else f"{registro['dias']} dias"
    return (
        f'<div class="aviso"><strong>Fuente congelada: {escapar(nombre)}.</strong> '
        f"Lleva {escapar(dias)} sin una descarga buena, con umbral de {registro['umbral']} dias. "
        "Lo que se muestra es el ultimo corte que si se pudo leer, y no es de hoy. "
        f"Ultimo detalle tecnico: {escapar(registro['detalle'])}.</div>"
    )


def aviso_cadencia(estado, registro):
    if estado == "falto":
        return (
            f'<div class="aviso"><strong>Esta plaza falto a su publicacion.</strong> '
            f"Le tocaba publicar el {escapar(registro['ultima_cita'])} y su ultimo "
            f"corte es del {escapar(registro['ultimo'])}, "
            f"{registro['dias_sin_publicar']} dias atras. "
            f"Cumplio {registro['cumplidas']} de "
            f"{registro['citas']} publicaciones esperadas desde que se sigue. "
            "Lo que se muestra abajo es su ultimo corte y no es de hoy.</div>"
        )
    if estado == "callada":
        return (
            f'<div class="aviso"><strong>Esta plaza lleva callada '
            f"{registro['dias_sin_publicar']} dias.</strong> "
            f"Cumplio {registro['cumplidas']} de "
            f"{registro['citas']} publicaciones esperadas desde que se sigue. "
            "Lo que se muestra abajo es su ultimo corte y no es de hoy.</div>"
        )
    return ""


def nota_base(bases):
    if bases == {"kilogramo"}:
        return "precios por kilogramo, calculados por la fuente"
    if bases == {"presentacion"}:
        return "precios por presentacion comercial completa, no por kilogramo"
    return "cuidado: esta plaza mezcla bases de precio distintas"


def pagina_de_plaza(bloque, fuentes, congeladas, cadencias, destino_dir, archivo):
    clave, mercado, fecha, filas, pulso, series = bloque
    fuente = fuentes[clave]
    rancia = clave in congeladas
    hoy = date.today().isoformat()

    partes = cabeza(f"{mercado} · precios de mayoreo", subir=True)
    partes.append(f"<h1>{escapar(mercado)}</h1>")
    etiqueta = f"corte del {fecha}" + (" · no es de hoy" if fecha != hoy else "")
    etiqueta += " · " + frase_cadencia(mercado)
    partes.append(
        '<p class="sub">Precio de mayoreo en central de abasto, que no es precio en finca: '
        "es lo que se paga en la plaza, y el productor cobra menos que esto.</p>"
    )
    partes.append(
        f'<p class="nota"><span class="alcance">mayoreo</span> {escapar(etiqueta)} · '
        f"{escapar(nota_base({fila[8] for fila in filas}))} · {escapar(fuente['atribucion'])} · "
        f"ventana publicada de {fuente['ventana']} dias</p>"
    )
    if rancia:
        partes.append(aviso_congelada(clave, congeladas[clave], fuente["nombre"]))
    estado, registro = cadencias.get((clave, mercado), (None, None))
    if estado:
        partes.append(aviso_cadencia(estado, registro))
    if pulso:
        partes.append(
            f'<p class="nota"><span class="pulso {pulso["veredicto"]}">'
            f'{escapar(VEREDICTOS[pulso["veredicto"]])}</span> {escapar(frase(pulso))}. '
            "Esto mide el movimiento real de los numeros, no la fecha que la fuente declara.</p>"
        )

    partes.append('<div class="envoltura">')
    partes.append(
        "<table><thead><tr><th>Producto</th><th class='oculta-chico'>Calidad</th>"
        "<th>Presentacion</th><th>Origen</th><th>Historico publicado</th>"
        "<th class='num'>Min</th><th class='num'>Frec</th>"
        "<th class='num'>Max</th><th class='num'>Var. 1d</th>"
        "<th class='num oculta-chico'>Amplitud</th><th>Fecha</th></tr></thead><tbody>"
    )
    for fila in filas:
        (
            producto, calidad, presentacion, origen, minimo, maximo, frecuente,
            fecha_dato, _base, _url, _mediana, variacion, amplitud, _n,
        ) = fila
        clase = ' class="rancia"' if rancia else ""
        if variacion is None:
            celda_var = "<td class='num'></td>"
        else:
            signo = "sube" if variacion > 0 else ("baja" if variacion < 0 else "")
            celda_var = f"<td class='num {signo}'>{variacion:+.2f}%</td>"
        marca = ' <span class="marca-rancia">dato detenido</span>' if rancia else ""
        partes.append(
            f"<tr{clase}><td>{escapar(producto)}{marca}</td>"
            f"<td class='oculta-chico'>{escapar(calidad)}</td>"
            f"<td>{escapar(presentacion)}</td><td>{escapar(origen)}</td>"
            f"<td class='historia'>"
            f"{grafica(series.get((producto, presentacion), []), ancho=168, alto=42, etiquetas=False)}"
            f"</td>"
            f"<td class='num'>{pesos(minimo)}</td><td class='num'>{pesos(frecuente)}</td>"
            f"<td class='num'>{pesos(maximo)}</td>"
            f"{celda_var}"
            f"<td class='num oculta-chico'>{'' if amplitud is None else f'{amplitud:.2f}'}</td>"
            f"<td>{escapar(fecha_dato)}</td></tr>"
        )
    partes.append("</tbody></table></div>")
    partes.extend(pie_comun(fuentes, con_graficas=True))

    ruta = os.path.join(destino_dir, archivo.replace("/", os.sep))
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as salida:
        salida.write("\n".join(partes))
    return ruta


def construir(ruta_base=None, ruta_reporte=None, salida=SALIDA):
    conexion = conectar(ruta_base)
    fuentes = {
        fila[0]: {
            "nombre": fila[1],
            "atribucion": fila[2],
            "url": fila[3],
            "veredicto": fila[4],
            "ventana": fila[5],
        }
        for fila in conexion.execute(
            "SELECT clave, nombre, atribucion, url_base, licencia_veredicto, ventana_dias FROM fuentes"
        )
    }

    movimiento = medir(conexion)

    with open(ruta_reporte or REPORTE, encoding="utf-8") as archivo:
        reporte = json.load(archivo)
    congeladas_lista, _sanas = evaluar(reporte)
    congeladas = {registro["fuente"]: registro for registro in congeladas_lista}

    # La cadencia de cada plaza y su cumplimiento no se inventan aqui: los da el
    # mismo vigilante que corre en CI, igual que el aviso de congelamiento. Dos
    # implementaciones de la misma regla acabarian diciendo cosas distintas.
    faltaron, calladas, _al_dia = evaluar_cadencia(conexion)
    cadencias = {}
    for registro in faltaron:
        cadencias[(registro["fuente"], registro["mercado"])] = ("falto", registro)
    for registro in calladas:
        cadencias[(registro["fuente"], registro["mercado"])] = ("callada", registro)

    # Cada plaza trae su propia fecha de corte. Tomar el maximo de la fuente y
    # mostrar solo las plazas que publicaron ese dia haria desaparecer en
    # silencio a la plaza que va con retraso, que es justo lo que el usuario
    # necesita saber.
    bloques = []
    for clave in sorted(fuentes):
        for mercado, ultima in conexion.execute(
            "SELECT mercado, MAX(fecha_dato) FROM precios WHERE fuente = ?"
            " GROUP BY mercado ORDER BY mercado",
            (clave,),
        ).fetchall():
            if not ultima:
                continue
            filas = conexion.execute(
                """
                SELECT p.producto, p.calidad, p.presentacion, p.origen, p.precio_min, p.precio_max,
                       p.precio_frec, p.fecha_dato, p.base_precio, p.consulta_url,
                       d.mediana_frec_7d, d.variacion_pct_1d, d.amplitud_rel, d.n_obs_7d
                FROM precios p
                LEFT JOIN derivados d
                  ON d.fuente = p.fuente AND d.producto = p.producto
                 AND d.mercado = p.mercado AND d.fecha_dato = p.fecha_dato
                WHERE p.fuente = ? AND p.fecha_dato = ? AND p.mercado = ?
                ORDER BY p.producto, p.presentacion
                """,
                (clave, ultima, mercado),
            ).fetchall()
            # Historico crudo de la plaza, un punto por dia PUBLICADO. Se lee de
            # una sola consulta y se reparte por producto, en vez de una consulta
            # por fila, que con 250 cotizaciones serian 250 viajes a la base.
            series = {}
            for producto, presentacion, fecha_punto, minimo, maximo, frecuente in conexion.execute(
                "SELECT producto, presentacion, fecha_dato, precio_min, precio_max, precio_frec"
                " FROM precios WHERE fuente = ? AND mercado = ? AND precio_frec IS NOT NULL"
                " ORDER BY fecha_dato",
                (clave, mercado),
            ):
                series.setdefault((producto, presentacion), []).append(
                    {"fecha": fecha_punto, "min": minimo, "max": maximo, "frec": frecuente}
                )
            bloques.append(
                (clave, mercado, ultima, filas, movimiento.get(clave, {}).get(mercado), series)
            )
    # El corte mas fresco arriba. Ordenar por clave de fuente dejaba primero a la
    # plaza que publico ayer y con un solo dia de historico, que es la peor
    # carta de presentacion posible para una pagina que vende frescura.
    bloques.sort(key=lambda bloque: (bloque[2], len(bloque[3])), reverse=True)

    _reaparecidas, vigiladas, _sin_intentos = evaluar_reaparicion(sondas.leer())
    conexion.close()

    destino_dir = os.path.dirname(os.path.abspath(salida))
    ids = {nombre: plaza_id for plaza_id, nombre in PLAZAS_CATALOGO.items()}

    escritas = []
    for bloque in bloques:
        archivo = archivo_de_plaza(bloque[0], bloque[1], ids)
        escritas.append(
            (bloque, archivo, pagina_de_plaza(bloque, fuentes, congeladas, cadencias, destino_dir, archivo))
        )

    generado = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M %Z")
    cotizaciones = sum(len(bloque[3]) for bloque in bloques)
    hoy = date.today().isoformat()
    publicaron_hoy = sum(1 for bloque in bloques if bloque[2] == hoy)

    partes = cabeza("Precios de hoy")
    partes.append("<h1>Precios de hoy</h1>")
    partes.append(
        '<p class="sub">Precio de mayoreo en central de abasto, que no es precio en finca: '
        "es lo que se paga en la plaza de destino, y el productor cobra menos que esto. "
        f"{len(bloques)} plazas seguidas, {publicaron_hoy} con corte de hoy, "
        f"{cotizaciones} cotizaciones en el ultimo corte de cada una. "
        f"Pagina generada el {escapar(generado)}.</p>"
    )

    for clave, registro in sorted(congeladas.items()):
        partes.append(
            aviso_congelada(clave, registro, fuentes.get(clave, {}).get("nombre", clave))
        )

    if not bloques:
        partes.append('<div class="aviso">No hay datos cargados todavia.</div>')

    faltantes = [b for b in bloques if (b[0], b[1]) in cadencias]
    if faltantes:
        partes.append(
            f'<div class="aviso"><strong>{len(faltantes)} de {len(bloques)} plazas no estan al '
            "dia.</strong> Cada una lo dice en su propia pagina, con los dias que lleva sin "
            "publicar y las publicaciones que cumplio.</div>"
        )

    partes.append('<div class="envoltura">')
    partes.append(
        "<table><thead><tr><th>Plaza</th><th>Corte</th>"
        "<th class='oculta-chico'>Cadencia</th><th>Movimiento</th>"
        "<th class='num'>Cotizaciones</th>"
        "<th class='num oculta-chico'>Dias publicados</th></tr></thead><tbody>"
    )
    for bloque, archivo, _ruta in escritas:
        clave, mercado, fecha, filas, pulso, series = bloque
        dias_publicados = len({punto["fecha"] for puntos in series.values() for punto in puntos})
        veredicto = pulso["veredicto"] if pulso else "sin_medir"
        estado = cadencias.get((clave, mercado), (None, None))[0]
        marca = "" if fecha == hoy else ' <span class="marca-rancia">no es de hoy</span>'
        if estado == "falto":
            marca = ' <span class="marca-rancia">falto a su publicacion</span>'
        elif estado == "callada":
            marca = ' <span class="marca-rancia">callada</span>'
        partes.append(
            f'<tr><td><a href="{escapar(archivo)}">{escapar(mercado)}</a></td>'
            f"<td>{escapar(fecha)}{marca}</td>"
            f"<td class='oculta-chico'>{escapar(frase_cadencia(mercado))}</td>"
            f'<td><span class="pulso {veredicto}">{escapar(VEREDICTOS[veredicto])}</span></td>'
            f"<td class='num'>{len(filas)}</td>"
            f"<td class='num oculta-chico'>{dias_publicados}</td></tr>"
        )
    partes.append("</tbody></table></div>")

    if vigiladas:
        nombres_vigilados = ", ".join(sorted(registro["nombre"] for registro in vigiladas))
        partes.append(
            f'<p class="nota">Hay plazas que hoy no publican nada y se consultan igual todos los '
            f"dias, para enterarse el dia en que vuelvan: {escapar(nombres_vigilados)}. No "
            "apareceran arriba mientras sigan en cero, y no se rellena su hueco con el ultimo "
            "dato que dieron. La Central de Abasto de Cuautla publicaba de lunes a viernes sin "
            "faltar y dejo de publicar el 31 de octubre de 2025.</p>"
        )

    partes.extend(pie_comun(fuentes, con_graficas=False))

    os.makedirs(os.path.dirname(salida), exist_ok=True)
    with open(salida, "w", encoding="utf-8") as archivo:
        archivo.write("\n".join(partes))
    return salida, len(bloques), sorted(congeladas)


if __name__ == "__main__":
    lector = argparse.ArgumentParser(description="Construye la pagina de precios de hoy")
    lector.add_argument("--base")
    lector.add_argument("--reporte")
    lector.add_argument("--salida", default=SALIDA)
    argumentos = lector.parse_args()
    ruta, bloques_totales, congeladas_vistas = construir(
        argumentos.base, argumentos.reporte, argumentos.salida
    )
    print(f"pagina escrita en {ruta} · {bloques_totales} bloques · congeladas: {congeladas_vistas}")
