"""Propuesta C · La brecha.

REFERENCIA: la vista de arbitraje entre exchanges, la que pone el mismo activo
en dos lugares y cobra sentido por la diferencia, no por el precio suelto.

POR QUE ESTA ES LA QUE SE PARECE AL PRODUCTO. El tablero de precios de mayoreo
ya existe dos veces en Mexico y cobra. Lo que no existe publicado es la
distancia entre lo que vale el producto donde se cosecha y lo que vale donde se
consume. Esa distancia es la pregunta del productor y tambien la del comprador,
y es la unica vista de este archivo que no se puede copiar de un tablero
existente.

HONESTIDAD OBLIGATORIA. La brecha no es margen ni es utilidad de nadie: entre
las dos cifras estan el flete, la merma y el margen de quien compra. Y si una
de las dos plazas tiene los numeros quietos, parte de la brecha es dato viejo y
no mercado. Las dos cosas se dicen arriba, no en una nota al pie.
"""
import os
import sys
from datetime import date, datetime, timezone

CARPETA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CARPETA)

from datos import VEREDICTOS, cargar, frase  # noqa: E402
from marcado import CABEZA, ESTILO_GRAFICA, escapar, grafica, pesos  # noqa: E402

ORIGEN = "Michoacán: Mercado de Abasto de Morelia"
DESTINO = "DF: Central de Abasto de Iztapalapa DF"

ESTILO = """
:root { --papel:#f6f6f3; --tarjeta:#fff; --tinta:#111a16; --suave:#6e7a74;
        --borde:#e3e2db; --oscuro:#101614; --azul:#2f6fae;
        --verde:#177950; --rojo:#b2372b; --ambar:#8a6a10; }
* { box-sizing:border-box; }
body { margin:0; background:var(--papel); color:var(--tinta);
       font:16px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;
       -webkit-font-smoothing:antialiased; }
.tapa { background:var(--oscuro); color:#eef2ef; padding:30px 0 26px; }
.ancho { max-width:1120px; margin:0 auto; padding:0 20px; }
.envoltura { overflow-x:auto; -webkit-overflow-scrolling:touch; }
table { min-width:720px; }
.tapa h1 { margin:0; font-size:clamp(1.6rem,3vw,2.15rem); letter-spacing:-.022em; }
.tapa p { margin:9px 0 0; color:#9fada7; max-width:64ch; font-size:.95rem; }
.par { display:flex; align-items:stretch; gap:14px; margin-top:22px; flex-wrap:wrap; }
.lado { flex:1 1 260px; background:#18211d; border:1px solid #243029; border-radius:12px;
        padding:13px 16px; }
.lado .rol { font-size:.7rem; letter-spacing:.14em; text-transform:uppercase; color:#8ba093; }
.lado .nombre { font-size:1rem; margin-top:4px; }
.lado .pie { color:#9fada7; font-size:.78rem; margin-top:6px; display:flex;
        align-items:center; gap:7px; }
.flecha { align-self:center; color:#6f8278; font-size:1.3rem; }
.punto { width:8px; height:8px; border-radius:50%; display:inline-block; flex:none; }
.punto.viva { background:#35c37d; } .punto.parcial { background:#e3a92b; }
.punto.estancada { background:#ff5f56; } .punto.sin_medir { background:#8a948f; }
.aviso { margin:22px 0 0; padding:14px 16px; border-radius:12px; font-size:.9rem;
        line-height:1.5; background:#fdf2ef; border:1px solid #f0cfc9; color:#7d2b22; }
.aviso b { color:inherit; }
.cifras { display:flex; gap:30px; flex-wrap:wrap; margin:24px 0 2px; }
.cifra .n { font-size:1.5rem; font-weight:650; font-variant-numeric:tabular-nums; }
.cifra .e { color:var(--suave); font-size:.76rem; text-transform:uppercase;
        letter-spacing:.07em; margin-top:2px; }
table { width:100%; border-collapse:collapse; margin-top:18px; background:var(--tarjeta);
        border:1px solid var(--borde); border-radius:14px; overflow:hidden; }
thead th { text-align:left; padding:11px 14px; font-size:.7rem; letter-spacing:.1em;
        text-transform:uppercase; color:var(--suave); font-weight:600;
        border-bottom:1px solid var(--borde); background:#fbfbf8; }
th.num, td.num { text-align:right; }
tbody td { padding:11px 14px; border-bottom:1px solid #f0efe9; vertical-align:middle;
        font-variant-numeric:tabular-nums; }
tbody tr:last-child td { border-bottom:0; }
td.prod { font-weight:600; font-variant-numeric:normal; }
td.prod small { display:block; font-weight:400; color:var(--suave); font-size:.76rem;
        margin-top:2px; }
td.lado-dato { color:var(--suave); }
td.brecha { font-weight:650; }
.riel { position:relative; height:7px; background:#efeee8; border-radius:4px; min-width:110px; }
.relleno { position:absolute; top:0; bottom:0; left:0; border-radius:4px; background:var(--azul); }
.pct { font-weight:650; }
.alta { color:var(--rojo); } .media { color:var(--ambar); } .baja { color:var(--verde); }
.dudosa td { background:#fcfaf5; }
.marca-dudosa { color:var(--ambar); font-size:.72rem; font-weight:600; }
footer { margin:40px 0 0; border-top:1px solid var(--borde); padding:16px 0 70px;
        color:var(--suave); font-size:.83rem; max-width:88ch; }
footer p { margin:0 0 8px; }
.grafica { color:var(--azul); }
.sin-serie { color:#b9bdb8; font-size:.72rem; }
"""


def indexar(bloque):
    """Indice por producto y presentacion, con las claves ambiguas marcadas.

    AQUI ESTA LA TRAMPA DE ESTA VISTA. El SNIIM declara base kilogramo para
    todo, pero la presentacion cambia: pina por pieza en una plaza y por
    kilogramo en la otra. Restar esas dos cifras produce una brecha inventada.
    Y a veces la misma plaza publica dos cotizaciones del mismo producto y la
    misma presentacion, con precios distintos, sin un campo que diga cual es
    cual. Esas claves se marcan ambiguas y no se comparan.
    """
    indice, repetidas = {}, set()
    for fila in bloque["filas"]:
        if fila["base"] != "kilogramo" or fila["frec"] is None:
            continue
        clave = (fila["producto"].strip().lower(), fila["presentacion"].strip().lower())
        if clave in indice:
            repetidas.add(clave)
            continue
        indice[clave] = fila
    for clave in repetidas:
        indice.pop(clave, None)
    return indice, repetidas


def construir(salida=None, ruta_base=None):
    fuentes, bloques = cargar(ruta_base)
    por_mercado = {bloque["mercado"]: bloque for bloque in bloques}
    origen = por_mercado.get(ORIGEN)
    destino = por_mercado.get(DESTINO)
    if origen is None or destino is None:
        raise SystemExit("faltan las dos plazas del par en la base")

    indice_origen, ambiguas_origen = indexar(origen)
    indice_destino, ambiguas_destino = indexar(destino)
    ambiguas = ambiguas_origen | ambiguas_destino
    sin_par = 0

    pares = []
    for clave, fila_origen in indice_origen.items():
        fila_destino = indice_destino.get(clave)
        if fila_destino is None:
            sin_par += 1
            continue
        brecha = fila_destino["frec"] - fila_origen["frec"]
        porcentaje = brecha / fila_origen["frec"] * 100 if fila_origen["frec"] else None
        if porcentaje is None:
            continue
        pares.append((fila_origen, fila_destino, brecha, porcentaje))
    pares.sort(key=lambda par: par[3], reverse=True)

    mayor = max((abs(par[3]) for par in pares), default=1) or 1
    generado = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")
    hoy = date.today().isoformat()
    pulso_origen = origen["pulso"]
    pulso_destino = destino["pulso"]
    dudoso = pulso_origen and pulso_origen["veredicto"] in ("estancada", "parcial")
    medianas = sorted(par[3] for par in pares)
    mediana = medianas[len(medianas) // 2] if medianas else 0

    partes = [
        CABEZA,
        "<title>Propuesta C · la brecha</title>",
        f"<style>{ESTILO}{ESTILO_GRAFICA}</style></head><body>",
        '<div class="tapa"><div class="ancho">',
        "<h1>De donde sale y donde se vende</h1>",
        "<p>El mismo producto, la misma presentacion, el mismo dia, en una plaza de la region "
        "que produce y en la plaza donde se consume. Las dos son de mayoreo: ninguna es precio "
        "en finca. La diferencia no es la utilidad de nadie, adentro estan el flete, la merma y "
        "el margen de quien compra.</p>",
        '<div class="par">',
    ]

    for rol, bloque, pulso in (
        ("plaza en region productora", origen, pulso_origen),
        ("plaza de consumo", destino, pulso_destino),
    ):
        veredicto = pulso["veredicto"] if pulso else "sin_medir"
        retraso = " · no es de hoy" if bloque["fecha"] != hoy else ""
        partes.append(
            f'<div class="lado"><div class="rol">{rol}</div>'
            f'<div class="nombre">{escapar(bloque["mercado"])}</div>'
            f'<div class="pie"><span class="punto {veredicto}"></span>'
            f'{escapar(VEREDICTOS[veredicto])} · corte {escapar(bloque["fecha"])}'
            f"{retraso} · {escapar(bloque['cadencia'])}</div></div>"
        )
        if rol == "plaza en region productora":
            partes.append('<div class="flecha">&rarr;</div>')
    partes.append("</div></div></div>")

    partes.append('<div class="ancho">')
    if dudoso:
        partes.append(
            f'<div class="aviso"><b>Lea esta brecha con reserva.</b> '
            f'{escapar(frase(pulso_origen))} en la plaza productora, mientras la de consumo '
            "mueve sus precios casi a diario. Parte de la diferencia puede ser dato quieto de "
            "un lado y no mercado del otro. La columna de la derecha marca cada fila afectada."
            "</div>"
        )

    partes.append('<div class="cifras">')
    partes.append(
        f'<div class="cifra"><div class="n">{len(pares)}</div>'
        '<div class="e">productos comparables</div></div>'
    )
    partes.append(
        f'<div class="cifra"><div class="n">{mediana:+.0f}%</div>'
        '<div class="e">brecha mediana</div></div>'
    )
    if pares:
        partes.append(
            f'<div class="cifra"><div class="n">{escapar(pares[0][0]["producto"])}</div>'
            '<div class="e">brecha mas ancha</div></div>'
        )
    partes.append(
        f'<div class="cifra"><div class="n">{escapar(generado[-5:])}</div>'
        '<div class="e">pagina generada hoy</div></div>'
    )
    partes.append("</div>")

    partes.append(
        '<div class="envoltura">'
        "<table><thead><tr><th>Producto</th><th class='num'>En la productora</th>"
        "<th class='num'>En consumo</th><th class='num'>Brecha</th><th class='num'>Brecha %</th>"
        "<th>Tamano de la brecha</th><th>Historico en la productora</th></tr></thead><tbody>"
    )
    for fila_origen, fila_destino, brecha, porcentaje in pares:
        ancho = min(100.0, abs(porcentaje) / mayor * 100)
        if abs(porcentaje) >= 60:
            nivel = "alta"
        elif abs(porcentaje) >= 25:
            nivel = "media"
        else:
            nivel = "baja"
        marca = (
            '<small class="marca-dudosa">productora quieta</small>'
            if dudoso and fila_origen["variacion"] in (None, 0)
            else ""
        )
        clase_fila = ' class="dudosa"' if marca else ""
        partes.append(
            f"<tr{clase_fila}><td class='prod'>{escapar(fila_origen['producto'])}"
            f"<small>{escapar(fila_origen['origen'])} · {escapar(fila_origen['calidad'].lower())}"
            f"</small>{marca}</td>"
            f"<td class='num lado-dato'>{pesos(fila_origen['frec'])}</td>"
            f"<td class='num lado-dato'>{pesos(fila_destino['frec'])}</td>"
            f"<td class='num brecha'>{brecha:+,.2f}</td>"
            f"<td class='num pct {nivel}'>{porcentaje:+.0f}%</td>"
            f"<td><div class='riel'><span class='relleno' style='width:{ancho:.1f}%'></span>"
            "</div></td>"
            f"<td>{grafica(fila_origen['serie'], ancho=150, alto=44, etiquetas=False)}</td></tr>"
        )
    partes.append("</tbody></table></div>")

    partes.append("<footer>")
    partes.append(
        "<p>Solo se comparan filas con el mismo producto y la misma presentacion. Una pieza "
        f"contra un kilogramo no se resta: {sin_par} productos de la plaza productora quedaron "
        "fuera porque la otra plaza no publica esa misma presentacion, y "
        f"{len(ambiguas)} quedaron fuera porque alguna de las dos publica varias cotizaciones "
        "del mismo producto y la misma presentacion, sin un campo que diga cual corresponde a "
        "cual. Esas filas se omiten en vez de presentarse como si se pudieran restar.</p>"
    )
    partes.append(
        "<p>Brecha es la diferencia entre el precio frecuente de la plaza de consumo y el de la "
        "plaza productora del mismo dia publicado. Es calculo propio, no dato de la fuente, y no es precio en finca: "
        "lo que recibe quien cosecha esta por debajo del precio de origen que aparece aqui.</p>"
    )
    partes.append(
        "<p>Sin graficas de velas a proposito: el dato publicado no trae apertura, cierre, "
        "volumen ni calidad homogenea que las sostengan. La grafica une el precio frecuente "
        "de cada dia publicado dentro de la ventana, un valor por dia, con la dispersion del "
        "dia en gris detras.</p>"
    )
    for clave in sorted(fuentes):
        partes.append(f"<p>{escapar(fuentes[clave]['atribucion'])}.</p>")
    partes.append("</footer></div></body></html>")

    destino_archivo = salida or os.path.join(CARPETA, "propuesta_c_brecha.html")
    with open(destino_archivo, "w", encoding="utf-8") as archivo:
        archivo.write("\n".join(partes))
    return destino_archivo


if __name__ == "__main__":
    print(construir())
