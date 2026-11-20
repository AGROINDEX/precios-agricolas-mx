"""Propuesta B · Mercado.

REFERENCIA: la vista de consumidor de un exchange (Coinbase, Kraken, Revolut):
fondo claro, tarjeta por activo, el numero grande y una sola cifra de contexto,
buscador arriba, pensado para el telefono antes que para el escritorio.

QUE SE TOMA Y QUE NO. Se toma la tarjeta por producto, el numero grande y la
barra de rango. No se toma la promesa implicita de "este es el precio al que
usted opera": aqui el numero es el precio frecuente de una plaza de mayoreo,
y la tarjeta lo dice sin que haya que buscarlo.
"""
import os
import sys
from datetime import date, datetime, timezone

CARPETA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CARPETA)

from datos import VEREDICTOS, cargar, etiqueta_base, frase  # noqa: E402
from marcado import CABEZA, ESTILO_GRAFICA, escapar, grafica, pesos, rumbo  # noqa: E402

ESTILO = """
:root { --papel:#f7f7f4; --tarjeta:#ffffff; --tinta:#14201b; --suave:#6d7a74;
        --borde:#e4e3dc; --verde:#0f7a4d; --verde-suave:#e6f4ec; --rojo:#b5362b;
        --rojo-suave:#fbecea; --ambar:#8a6a10; --ambar-suave:#fbf1d9; }
* { box-sizing:border-box; }
body { margin:0; background:var(--papel); color:var(--tinta);
       font:16px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",sans-serif;
       -webkit-font-smoothing:antialiased; }
.ancho { max-width:1120px; margin:0 auto; padding:0 20px 72px; }
header { padding:34px 0 10px; }
h1 { margin:0; font-size:clamp(1.6rem,3vw,2.1rem); letter-spacing:-.02em; }
.lede { margin:8px 0 0; color:var(--suave); max-width:62ch; font-size:.95rem; }
.cifras { display:flex; gap:28px; flex-wrap:wrap; margin:22px 0 4px;
       padding:16px 20px; background:var(--tarjeta); border:1px solid var(--borde);
       border-radius:14px; }
.cifra .n { font-size:1.45rem; font-weight:650; font-variant-numeric:tabular-nums; }
.cifra .e { color:var(--suave); font-size:.78rem; text-transform:uppercase;
       letter-spacing:.07em; margin-top:2px; }
.pestanas { display:flex; gap:8px; flex-wrap:wrap; margin:26px 0 6px; }
.pestana { border:1px solid var(--borde); background:var(--tarjeta); border-radius:999px;
       padding:8px 15px; font-size:.86rem; display:flex; align-items:center; gap:8px; }
.pestana.activa { border-color:var(--tinta); }
.punto { width:8px; height:8px; border-radius:50%; display:inline-block; }
.punto.viva { background:var(--verde); } .punto.parcial { background:var(--ambar); }
.punto.estancada { background:var(--rojo); } .punto.sin_medir { background:#b9bdb8; }
.buscador { width:100%; margin:14px 0 4px; padding:12px 16px; border-radius:12px;
       border:1px solid var(--borde); background:var(--tarjeta); font-size:.95rem;
       color:var(--tinta); }
.banda { margin:18px 0 6px; padding:13px 16px; border-radius:12px; font-size:.88rem;
       line-height:1.5; border:1px solid var(--borde); background:var(--tarjeta);
       color:var(--suave); }
.banda.estancada { background:var(--rojo-suave); border-color:#f0cfc9; color:#7d2b22; }
.banda.sin_medir { background:var(--papel); }
.banda b { color:inherit; }
h2 { font-size:1.05rem; margin:34px 0 2px; }
.sub { color:var(--suave); font-size:.85rem; margin:3px 0 0; }
.rejilla { display:grid; gap:12px; margin-top:16px;
       grid-template-columns:repeat(auto-fill,minmax(258px,1fr)); }
.tarjeta { background:var(--tarjeta); border:1px solid var(--borde); border-radius:14px;
       padding:15px 16px 13px; }
.tarjeta .nom { font-weight:600; font-size:1rem; line-height:1.25; }
.tarjeta .meta { color:var(--suave); font-size:.79rem; margin-top:3px; }
.precio { display:flex; align-items:baseline; gap:9px; margin-top:12px;
       justify-content:space-between; }
.precio .n { font-size:1.65rem; font-weight:650; font-variant-numeric:tabular-nums;
       letter-spacing:-.02em; }
.precio .u { color:var(--suave); font-size:.76rem; display:block; margin-top:1px; }
.precio .izq { display:flex; align-items:baseline; gap:8px; flex-wrap:wrap; }
.chip { border-radius:999px; padding:2px 8px; font-size:.76rem; font-weight:600;
       font-variant-numeric:tabular-nums; }
.chip.sube { background:var(--verde-suave); color:var(--verde); }
.chip.baja { background:var(--rojo-suave); color:var(--rojo); }
.chip.quieto { background:#eeeeea; color:var(--suave); }
.barra { margin-top:13px; }
.barra .riel { position:relative; height:4px; border-radius:3px; background:#eceae4; }
.barra .marca { position:absolute; top:-3px; width:2px; height:10px; background:var(--tinta);
       border-radius:1px; }
.barra .pie { display:flex; justify-content:space-between; color:var(--suave);
       font-size:.72rem; margin-top:5px; font-variant-numeric:tabular-nums; }
.linea { margin-top:11px; display:flex; align-items:center; gap:9px; color:var(--suave);
       font-size:.74rem; }
.linea svg, .linea .sin-serie { flex:none; }
.grafica { color:#2f6fae; width:100%; height:auto; margin-top:12px; }
.pie-grafica { color:var(--suave); font-size:.72rem; margin-top:4px; }
.sin-serie { color:#b9bdb8; font-size:.72rem; }
footer { margin-top:52px; border-top:1px solid var(--borde); padding-top:16px;
       color:var(--suave); font-size:.82rem; max-width:84ch; }
footer p { margin:0 0 8px; }
"""

FILTRO = """
document.querySelectorAll('.buscador').forEach(function (campo) {
  campo.addEventListener('input', function () {
    var texto = campo.value.trim().toLowerCase();
    document.querySelectorAll('.tarjeta').forEach(function (tarjeta) {
      tarjeta.style.display = tarjeta.dataset.busca.indexOf(texto) === -1 ? 'none' : '';
    });
  });
});
"""


def barra(fila):
    minimo, maximo, frecuente = fila["min"], fila["max"], fila["frec"]
    if None in (minimo, maximo, frecuente) or maximo <= minimo:
        posicion = 50.0
    else:
        posicion = max(0.0, min(100.0, (frecuente - minimo) / (maximo - minimo) * 100))
    return (
        '<div class="barra"><div class="riel">'
        f'<span class="marca" style="left:calc({posicion:.1f}% - 1px)"></span></div>'
        f'<div class="pie"><span>{pesos(minimo)}</span>'
        "<span>rango publicado del dia</span>"
        f"<span>{pesos(maximo)}</span></div></div>"
    )


def construir(salida=None, ruta_base=None):
    fuentes, bloques = cargar(ruta_base)
    generado = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")
    hoy = date.today().isoformat()
    total = sum(len(bloque["filas"]) for bloque in bloques)
    ultimo = max(bloque["fecha"] for bloque in bloques)

    partes = [
        CABEZA,
        "<title>Propuesta B · mercado</title>",
        f"<style>{ESTILO}{ESTILO_GRAFICA}</style></head><body><div class='ancho'>",
        "<header><h1>Precios de hoy</h1>",
        '<p class="lede">Lo que se paga por mayoreo en la plaza de destino. No es precio en '
        "finca: entre este numero y lo que recibe quien cosecha estan el flete, la merma y el "
        "margen de quien compra.</p></header>",
        '<div class="cifras">',
        f'<div class="cifra"><div class="n">{len(bloques)}</div><div class="e">plazas</div></div>',
        f'<div class="cifra"><div class="n">{total}</div><div class="e">cotizaciones</div></div>',
        f'<div class="cifra"><div class="n">{escapar(ultimo)}</div>'
        '<div class="e">corte mas reciente</div></div>',
        f'<div class="cifra"><div class="n">{escapar(generado[-5:])}</div>'
        '<div class="e">pagina generada hoy</div></div>',
        "</div>",
        '<div class="pestanas">',
    ]

    for indice, bloque in enumerate(bloques):
        veredicto = bloque["pulso"]["veredicto"] if bloque["pulso"] else "sin_medir"
        activa = " activa" if indice == 0 else ""
        partes.append(
            f'<span class="pestana{activa}"><span class="punto {veredicto}"></span>'
            f'{escapar(bloque["mercado"])}</span>'
        )
    partes.append("</div>")
    partes.append('<input class="buscador" type="search" placeholder="Buscar producto, '
                  'presentacion u origen">')

    for bloque in bloques:
        pulso = bloque["pulso"]
        veredicto = pulso["veredicto"] if pulso else "sin_medir"
        retraso = " · no es de hoy" if bloque["fecha"] != hoy else ""
        partes.append(f"<h2>{escapar(bloque['mercado'])}</h2>")
        partes.append(
            f'<p class="sub">Corte del {escapar(bloque["fecha"])}{retraso} · '
            f'{escapar(etiqueta_base(bloque["filas"]))} · '
            f'{escapar(bloque["fuente"]["atribucion"])}</p>'
        )
        if pulso:
            partes.append(
                f'<div class="banda {veredicto}"><b>{escapar(VEREDICTOS[veredicto])}.</b> '
                f"{escapar(frase(pulso))}. Esto mide el movimiento real de los numeros, no la "
                "fecha que la fuente declara.</div>"
            )
        partes.append('<div class="rejilla">')
        for fila in bloque["filas"]:
            clase, texto = rumbo(fila["variacion"])
            chip = (
                f'<span class="chip {clase}">{texto}</span>'
                if texto
                else '<span class="chip quieto">sin dia previo</span>'
            )
            unidad = (
                "pesos por kilogramo"
                if fila["base"] == "kilogramo"
                else f"pesos por {fila['presentacion'].lower()}"
            )
            busca = " ".join(
                parte.lower()
                for parte in (fila["producto"], fila["presentacion"], fila["origen"])
            )
            partes.append(
                f'<div class="tarjeta" data-busca="{escapar(busca)}">'
                f'<div class="nom">{escapar(fila["producto"])}</div>'
                f'<div class="meta">{escapar(fila["presentacion"])} · origen '
                f'{escapar(fila["origen"])} · {escapar(fila["calidad"].lower())}</div>'
                f'<div class="precio"><span class="izq">'
                f'<span class="n">{pesos(fila["frec"])}</span>'
                f'<span class="u">{escapar(unidad)}</span></span>{chip}</div>'
                f"{barra(fila)}"
                f'{grafica(fila["serie"], ancho=250, alto=96)}'
                f'<div class="pie-grafica">{len(fila["serie"])} dias publicados · '
                "la banda gris es el rango del dia</div></div>"
            )
        partes.append("</div>")

    partes.append("<footer>")
    partes.append(
        "<p>El numero grande es el precio frecuente del dia en esa plaza, que es el que la "
        "fuente reporta como mas repetido. La barra muestra el rango publicado del mismo dia: "
        "no es un rango de transacciones con hora ni volumen, es lo que la fuente publica.</p>"
    )
    partes.append(
        "<p>La grafica es el precio frecuente de cada dia publicado dentro de la ventana, un "
        "valor por dia, sobre la dispersion del mismo dia en gris. El eje son dias publicados: "
        "un domingo sin publicacion no deja hueco ni se rellena con el valor del viernes.</p>"
        "<p>La variacion compara contra el dia publicado anterior, no contra las 24 horas. "
        "Si una plaza no publico el fin de semana, la comparacion salta ese hueco y lo dice.</p>"
    )
    partes.append(
        "<p>Sin graficas de velas a proposito: el dato publicado no trae apertura, cierre, "
        "volumen ni calidad homogenea que las sostengan.</p>"
    )
    for clave in sorted(fuentes):
        partes.append(f"<p>{escapar(fuentes[clave]['atribucion'])}.</p>")
    partes.append("</footer></div>")
    partes.append(f"<script>{FILTRO}</script></body></html>")

    destino = salida or os.path.join(CARPETA, "propuesta_b_mercado.html")
    with open(destino, "w", encoding="utf-8") as archivo:
        archivo.write("\n".join(partes))
    return destino


if __name__ == "__main__":
    print(construir())
