"""Construye la pagina de precios de hoy, con frescura y atribucion por fila.

LO QUE LA PAGINA DICE Y LO QUE NO. Dice mayoreo en central de abasto, con el
alcance pegado al numero, porque es lo que el dato mide. No dice precio en
finca, no promete precio de transaccion y no dibuja velas: no hay hora, volumen
ni calidad homogenea que las sostenga, y un comprador profesional lo detecta de
inmediato.

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
import sys
from datetime import date, datetime, timezone

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "ingesta"))

from check_fuentes_stale import evaluar  # noqa: E402
from comun import conectar  # noqa: E402

SALIDA = os.path.join(RAIZ, "web", "index.html")
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
tr.rancia td { opacity: 0.55; }
.marca-rancia { color: var(--alerta); font-size: 0.78rem; }
.sube { color: var(--alerta); } .baja { color: var(--acento); }
footer { margin-top: 48px; border-top: 1px solid var(--borde); padding-top: 14px;
         color: var(--suave); font-size: 0.85rem; }
@media (max-width: 720px) { .oculta-chico { display: none; } }
"""


def escapar(valor):
    return html.escape("" if valor is None else str(valor))


def pesos(valor):
    return "" if valor is None else f"{valor:,.2f}"


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

    with open(ruta_reporte or REPORTE, encoding="utf-8") as archivo:
        reporte = json.load(archivo)
    congeladas, _sanas = evaluar(reporte)
    claves_congeladas = {registro["fuente"]: registro for registro in congeladas}

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
            bloques.append((clave, mercado, ultima, filas))
    conexion.close()

    generado = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M %Z")
    partes = [
        "<!doctype html>",
        '<html lang="es"><head><meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>Precios de hoy</title>",
        f"<style>{ESTILO}</style></head><body><main>",
        "<h1>Precios de hoy</h1>",
        '<p class="sub">Precio de mayoreo en central de abasto, que no es precio en finca: '
        "es lo que se paga en la plaza de destino, y el productor cobra menos que esto. "
        f"Pagina generada el {escapar(generado)}.</p>",
    ]

    for clave, registro in sorted(claves_congeladas.items()):
        nombre = fuentes.get(clave, {}).get("nombre", clave)
        dias = "nunca" if registro["dias"] is None else f"{registro['dias']} dias"
        partes.append(
            f'<div class="aviso"><strong>Fuente congelada: {escapar(nombre)}.</strong> '
            f"Lleva {escapar(dias)} sin una descarga buena, con umbral de {registro['umbral']} dias. "
            "Lo que se muestra abajo es el ultimo corte que si se pudo leer, y no es de hoy. "
            f"Ultimo detalle tecnico: {escapar(registro['detalle'])}.</div>"
        )

    if not bloques:
        partes.append('<div class="aviso">No hay datos cargados todavia.</div>')

    for clave, mercado, fecha, filas in bloques:
        fuente = fuentes[clave]
        rancia = clave in claves_congeladas
        hoy = date.today().isoformat()
        etiqueta_fecha = f"corte del {fecha}" + (" · no es de hoy" if fecha != hoy else "")
        partes.append(f"<h2>{escapar(mercado)}</h2>")
        bases = {fila[8] for fila in filas}
        if bases == {"kilogramo"}:
            nota_base = "precios por kilogramo, calculados por la fuente"
        elif bases == {"presentacion"}:
            nota_base = "precios por presentacion comercial completa, no por kilogramo"
        else:
            nota_base = "cuidado: esta plaza mezcla bases de precio distintas"
        partes.append(
            f'<p class="nota"><span class="alcance">mayoreo</span> {escapar(etiqueta_fecha)} · '
            f"{escapar(nota_base)} · {escapar(fuente['atribucion'])} · "
            f"ventana publicada de {fuente['ventana']} dias</p>"
        )
        partes.append('<div class="envoltura">')
        partes.append(
            "<table><thead><tr><th>Producto</th><th class='oculta-chico'>Calidad</th>"
            "<th>Presentacion</th><th>Origen</th><th class='num'>Min</th><th class='num'>Frec</th>"
            "<th class='num'>Max</th><th class='num'>Mediana 7d</th><th class='num'>Var. 1d</th>"
            "<th class='num oculta-chico'>Amplitud</th><th>Fecha</th></tr></thead><tbody>"
        )
        for fila in filas:
            (
                producto,
                calidad,
                presentacion,
                origen,
                minimo,
                maximo,
                frecuente,
                fecha_dato,
                _base,
                _url,
                mediana,
                variacion,
                amplitud,
                _n,
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
                f"<td class='num'>{pesos(minimo)}</td><td class='num'>{pesos(frecuente)}</td>"
                f"<td class='num'>{pesos(maximo)}</td><td class='num'>{pesos(mediana)}</td>"
                f"{celda_var}"
                f"<td class='num oculta-chico'>{'' if amplitud is None else f'{amplitud:.2f}'}</td>"
                f"<td>{escapar(fecha_dato)}</td></tr>"
            )
        partes.append("</tbody></table></div>")

    partes.append("<footer>")
    partes.append(
        "<p>Una advertencia que importa al comparar plazas: el SNIIM publica el precio por "
        "kilogramo calculado y la Central de Abasto lo publica por presentacion comercial. "
        "Una caja de nueve kilos a 310 pesos y un kilogramo a 34.44 pesos son el mismo precio. "
        "Cada bloque dice sobre que base esta cotizado.</p>"
    )
    partes.append(
        "<p>Mediana de 7 dias, variacion contra el dia publicado anterior y amplitud relativa "
        "son calculo propio sobre una ventana corta, no dato de la fuente. El precio puntual se "
        "cita con su fecha y su fuente, y el acervo historico se consulta en la fuente, que es "
        "quien lo elaboro.</p>"
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

    os.makedirs(os.path.dirname(salida), exist_ok=True)
    with open(salida, "w", encoding="utf-8") as archivo:
        archivo.write("\n".join(partes))
    return salida, len(bloques), sorted(claves_congeladas)


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
