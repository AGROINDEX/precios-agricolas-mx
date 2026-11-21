"""Propuesta A · Terminal.

REFERENCIA: la vista profesional de un exchange (Binance pro, la terminal de
Bloomberg): densidad alta, numeros tabulares monoespaciados, variacion a color,
cinta de los que mas se movieron, todo sobre fondo oscuro para mirar la pantalla
muchas horas.

QUE SE TOMA Y QUE NO. Se toma la densidad, la cinta de movimientos y la
jerarquia del numero sobre el adorno. No se toman las velas: no hay apertura,
cierre ni volumen que las sostenga. La linea de diez dias es el precio
frecuente publicado, un dato por dia, y se dice asi.
"""
import os
import sys
from datetime import date, datetime, timezone

CARPETA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CARPETA)

from datos import VEREDICTOS, cargar, etiqueta_base, frase  # noqa: E402
from marcado import CABEZA, ESTILO_GRAFICA, escapar, grafica, pesos, rumbo  # noqa: E402

ESTILO = """
:root { --fondo:#0a0d0c; --panel:#111614; --panel2:#161d1a; --borde:#1f2b26;
        --tinta:#e8eeea; --suave:#7f8f88; --verde:#35c37d; --rojo:#ff5f56;
        --ambar:#e3a92b; --azul:#5aa9e6; }
* { box-sizing:border-box; }
body { margin:0; background:var(--fondo); color:var(--tinta);
       font:14px/1.5 ui-sans-serif,system-ui,"Segoe UI",sans-serif; }
.mono, td.num, th.num { font-family:ui-monospace,"Cascadia Mono",Consolas,monospace;
       font-variant-numeric:tabular-nums; }
header.barra { display:flex; align-items:center; gap:18px; flex-wrap:wrap;
       padding:12px 20px; border-bottom:1px solid var(--borde); background:var(--panel); }
.marca { font-weight:700; letter-spacing:.14em; font-size:13px; }
.marca span { color:var(--verde); }
.dato-barra { color:var(--suave); font-size:12px; }
.dato-barra b { color:var(--tinta); font-weight:600; }
.cinta { display:flex; gap:0; overflow-x:auto; border-bottom:1px solid var(--borde);
       background:var(--panel2); }
.cinta .item { display:flex; align-items:baseline; gap:8px; padding:9px 18px;
       border-right:1px solid var(--borde); white-space:nowrap; font-size:12.5px; }
.cinta .nom { color:var(--suave); }
.cinta .val { font-family:ui-monospace,Consolas,monospace; }
.cinta .sube { color:var(--verde); } .cinta .baja { color:var(--rojo); }
.lienzo { display:grid; grid-template-columns:238px 1fr; min-height:calc(100vh - 92px); }
aside { border-right:1px solid var(--borde); background:var(--panel); padding:16px 0; }
aside h3 { font-size:10.5px; letter-spacing:.16em; text-transform:uppercase;
       color:var(--suave); margin:0 0 8px; padding:0 16px; font-weight:600; }
.plaza { display:block; padding:10px 16px; border-left:2px solid transparent; cursor:default; }
.plaza.activa { background:var(--panel2); border-left-color:var(--verde); }
.plaza .nombre { font-size:13px; }
.plaza .pie { color:var(--suave); font-size:11.5px; margin-top:3px;
       display:flex; align-items:center; gap:6px; }
.punto { width:7px; height:7px; border-radius:50%; display:inline-block; flex:none; }
.punto.viva { background:var(--verde); }
.punto.parcial { background:var(--ambar); }
.punto.estancada { background:var(--rojo); }
.punto.sin_medir { background:var(--suave); }
.aviso-lateral { margin:16px; padding:11px 12px; border:1px solid var(--borde);
       border-left:2px solid var(--ambar); border-radius:4px; color:var(--suave);
       font-size:11.5px; line-height:1.45; }
main { padding:0 0 60px; min-width:0; }
.envoltura { overflow-x:auto; -webkit-overflow-scrolling:touch; }
.envoltura table { min-width:860px; }
.titulo { padding:18px 20px 10px; display:flex; align-items:baseline; gap:14px; flex-wrap:wrap; }
.titulo h2 { margin:0; font-size:17px; font-weight:650; }
.etq { border:1px solid var(--borde); border-radius:3px; padding:2px 7px; font-size:11px;
       color:var(--suave); }
.etq.viva { color:var(--verde); border-color:#1f4d38; }
.etq.estancada { color:var(--rojo); border-color:#4d2320; }
.etq.parcial { color:var(--ambar); border-color:#4d3c15; }
.etq.sin_medir { color:var(--suave); }
.sublinea { padding:0 20px 12px; color:var(--suave); font-size:12px; max-width:92ch; }
table { width:100%; border-collapse:collapse; font-size:13px; }
thead th { position:sticky; top:0; background:var(--fondo); text-align:left;
       padding:8px 14px; font-size:10.5px; letter-spacing:.1em; text-transform:uppercase;
       color:var(--suave); font-weight:600; border-bottom:1px solid var(--borde); }
th.num, td.num { text-align:right; }
tbody td { padding:7px 14px; border-bottom:1px solid #141b18; white-space:nowrap; }
tbody tr:hover { background:var(--panel); }
td.prod { font-weight:500; }
td.sec { color:var(--suave); font-size:12.5px; }
td.frec { font-weight:600; }
.sube { color:var(--verde); } .baja { color:var(--rojo); } .quieto { color:var(--suave); }
.grafica { color:var(--azul); }
.sin-serie { color:#3a4a44; font-size:11px; }
td.historia { padding:4px 14px; }
footer { margin:28px 20px 0; padding-top:14px; border-top:1px solid var(--borde);
       color:var(--suave); font-size:11.5px; max-width:100ch; }
footer p { margin:0 0 7px; }
@media (max-width:900px) { .lienzo { grid-template-columns:1fr; }
       aside { border-right:0; border-bottom:1px solid var(--borde); } }
"""


def cinta(bloques, cantidad=9):
    movidos = []
    for bloque in bloques:
        for fila in bloque["filas"]:
            if fila["variacion"] is not None and abs(fila["variacion"]) >= 0.01:
                movidos.append((abs(fila["variacion"]), fila, bloque))
    movidos.sort(key=lambda par: par[0], reverse=True)
    piezas = ['<div class="cinta">']
    for _peso, fila, bloque in movidos[:cantidad]:
        clase, texto = rumbo(fila["variacion"])
        piezas.append(
            f'<div class="item"><span class="nom">{escapar(fila["producto"])}</span>'
            f'<span class="val">{pesos(fila["frec"])}</span>'
            f'<span class="val {clase}">{texto}</span></div>'
        )
    if not movidos:
        piezas.append('<div class="item"><span class="nom">ningun producto se movio '
                      "en el ultimo corte</span></div>")
    piezas.append("</div>")
    return "".join(piezas)


def construir(salida=None, ruta_base=None):
    fuentes, bloques = cargar(ruta_base)
    generado = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")
    hoy = date.today().isoformat()
    total = sum(len(bloque["filas"]) for bloque in bloques)
    ultimo = max(bloque["fecha"] for bloque in bloques)

    partes = [
        CABEZA,
        "<title>Propuesta A · terminal</title>",
        f"<style>{ESTILO}{ESTILO_GRAFICA}</style></head><body>",
        '<header class="barra">',
        '<div class="marca">PRECIOS <span>MX</span></div>',
        f'<div class="dato-barra">corte mas reciente <b class="mono">{escapar(ultimo)}</b></div>',
        f'<div class="dato-barra">plazas <b class="mono">{len(bloques)}</b></div>',
        f'<div class="dato-barra">cotizaciones <b class="mono">{total}</b></div>',
        f'<div class="dato-barra">pagina generada <b class="mono">{escapar(generado)}</b></div>',
        "</header>",
        cinta(bloques),
        '<div class="lienzo"><aside><h3>Plazas</h3>',
    ]

    for indice, bloque in enumerate(bloques):
        pulso = bloque["pulso"]
        veredicto = pulso["veredicto"] if pulso else "sin_medir"
        activa = " activa" if indice == 0 else ""
        retraso = " · no es de hoy" if bloque["fecha"] != hoy else ""
        partes.append(
            f'<div class="plaza{activa}"><div class="nombre">{escapar(bloque["mercado"])}</div>'
            f'<div class="pie"><span class="punto {veredicto}"></span>'
            f'{escapar(VEREDICTOS[veredicto])} · {escapar(bloque["fecha"])}{retraso}</div></div>'
        )

    partes.append(
        '<div class="aviso-lateral">Mayoreo en plaza de destino. No es precio en finca: '
        "entre este numero y lo que recibe quien cosecha estan el flete, la merma y el "
        "margen de quien compra.</div></aside><main>"
    )

    for bloque in bloques:
        pulso = bloque["pulso"]
        veredicto = pulso["veredicto"] if pulso else "sin_medir"
        partes.append('<div class="titulo">')
        partes.append(f"<h2>{escapar(bloque['mercado'])}</h2>")
        partes.append(f'<span class="etq">corte {escapar(bloque["fecha"])}</span>')
        partes.append(f'<span class="etq {veredicto}">{escapar(VEREDICTOS[veredicto])}</span>')
        partes.append(f'<span class="etq">{escapar(etiqueta_base(bloque["filas"]))}</span>')
        partes.append(f'<span class="etq">{escapar(bloque["cadencia"])}</span>')
        partes.append("</div>")
        detalle = frase(pulso) + ". " if pulso else ""
        partes.append(
            f'<p class="sublinea">{escapar(detalle)}'
            f'{escapar(bloque["fuente"]["atribucion"])} · ventana publicada de '
            f'{bloque["fuente"]["ventana"]} dias.</p>'
        )
        partes.append(
            '<div class="envoltura">'
            "<table><thead><tr><th>Producto</th><th>Presentacion</th><th>Origen</th>"
            "<th>Historico publicado</th><th class='num'>Min</th><th class='num'>Frec</th>"
            "<th class='num'>Max</th>"
            "<th class='num'>Var. 1d</th><th class='num'>Amplitud</th></tr></thead><tbody>"
        )
        for fila in bloque["filas"]:
            clase, texto = rumbo(fila["variacion"])
            amplitud = "" if fila["amplitud"] is None else f"{fila['amplitud'] * 100:.0f}%"
            partes.append(
                f'<tr><td class="prod">{escapar(fila["producto"])}</td>'
                f'<td class="sec">{escapar(fila["presentacion"])}</td>'
                f'<td class="sec">{escapar(fila["origen"])}</td>'
                f'<td class="historia">{grafica(fila["serie"], ancho=168, alto=42, etiquetas=False)}</td>'
                f'<td class="num sec">{pesos(fila["min"])}</td>'
                f'<td class="num frec">{pesos(fila["frec"])}</td>'
                f'<td class="num sec">{pesos(fila["max"])}</td>'
                f'<td class="num {clase}">{texto}</td>'
                f'<td class="num sec">{amplitud}</td></tr>'
            )
        partes.append("</tbody></table></div>")

    partes.append("<footer>")
    partes.append(
        "<p>El color sigue la direccion del precio en la plaza: verde es alza y rojo es baja. "
        "Si usted compra, el verde le cuesta. Si usted vende, el verde le conviene.</p>"
    )
    partes.append(
        "<p>La grafica une el precio frecuente de cada dia publicado dentro de la ventana, "
        "un valor por dia, con la dispersion del dia en gris detras. El eje son dias "
        "publicados, no dias de calendario: un domingo sin publicacion no deja hueco ni se "
        "rellena con el valor del viernes. No son velas: no existe apertura, cierre, maximo "
        "intradia ni volumen que las sostenga.</p>"
    )
    partes.append(
        "<p>La variacion contra el dia publicado anterior y la amplitud son calculo propio "
        "sobre la ventana, no dato de la fuente. El precio puntual se cita con su fecha y su "
        "fuente, y el acervo historico completo se consulta en la fuente, que es quien lo "
        "elaboro.</p>"
    )
    for clave in sorted(fuentes):
        partes.append(f"<p>{escapar(fuentes[clave]['atribucion'])}.</p>")
    partes.append("</footer></main></div></body></html>")

    destino = salida or os.path.join(CARPETA, "propuesta_a_terminal.html")
    with open(destino, "w", encoding="utf-8") as archivo:
        archivo.write("\n".join(partes))
    return destino


if __name__ == "__main__":
    print(construir())
