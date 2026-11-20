"""Grafica historica compartida por la pagina publicada y por las propuestas.

Vive en ingesta/ porque la dibujan dos consumidores distintos, la pagina de
web/ y las maquetas de diseno/, y duplicarla seria garantizar que un dia digan
cosas distintas sobre los mismos datos.
"""


def grafica(puntos, ancho=300, alto=104, etiquetas=True, banda=True):
    """Historico del precio de un producto, dibujado desde las filas crudas.

    QUE DIBUJA. La linea es el precio frecuente de cada dia publicado. La banda
    clara detras es el rango que la fuente publico ese mismo dia, que no es el
    recorrido de un precio de transaccion sino la dispersion de las
    cotizaciones encuestadas en la plaza. Por eso va detras y en gris, no como
    si fuera una vela.

    EL EJE X SON DIAS PUBLICADOS, no dias de calendario: si la plaza no publico
    el domingo, no hay hueco inventado. Las dos fechas de los extremos quedan
    escritas para que nadie lea diez dias publicados como diez dias corridos.
    """
    serie = [punto for punto in puntos if punto.get("frec") is not None]
    if len(serie) < 2:
        return '<span class="sin-serie">sin historico suficiente</span>'

    izquierda = 38 if etiquetas else 2
    abajo = 15 if etiquetas else 2
    x0, x1 = izquierda, ancho - 4
    y0, y1 = 8, alto - abajo

    valores = []
    for punto in serie:
        valores.append(punto["frec"])
        if banda:
            valores += [v for v in (punto.get("min"), punto.get("max")) if v is not None]
    piso, techo = min(valores), max(valores)
    if techo == piso:
        techo = piso + 1
        plano = True
    else:
        plano = False

    paso = (x1 - x0) / (len(serie) - 1)

    def coordenada(indice, valor):
        x = x0 + indice * paso
        y = y1 - (valor - piso) / (techo - piso) * (y1 - y0)
        return x, y

    piezas = [
        f'<svg class="grafica" viewBox="0 0 {ancho} {alto}" width="{ancho}" height="{alto}"'
        f' role="img" aria-label="precio frecuente publicado de los ultimos'
        f' {len(serie)} dias con dato">'
    ]

    if banda and not plano:
        arriba_puntos, abajo_puntos = [], []
        for indice, punto in enumerate(serie):
            alto_valor = punto.get("max") or punto["frec"]
            bajo_valor = punto.get("min") or punto["frec"]
            ax, ay = coordenada(indice, alto_valor)
            bx, by = coordenada(indice, bajo_valor)
            arriba_puntos.append(f"{ax:.1f},{ay:.1f}")
            abajo_puntos.append(f"{bx:.1f},{by:.1f}")
        forma = " ".join(arriba_puntos + list(reversed(abajo_puntos)))
        piezas.append(f'<polygon class="banda" points="{forma}"/>')

    linea = " ".join(
        "{:.1f},{:.1f}".format(*coordenada(indice, punto["frec"]))
        for indice, punto in enumerate(serie)
    )
    piezas.append(f'<polyline class="linea" points="{linea}" fill="none"/>')

    ultimo_x, ultimo_y = coordenada(len(serie) - 1, serie[-1]["frec"])
    piezas.append(f'<circle class="punta" cx="{ultimo_x:.1f}" cy="{ultimo_y:.1f}" r="2.6"/>')

    if etiquetas:
        piezas.append(
            f'<text class="eje" x="2" y="{y0 + 4:.0f}">{techo:,.0f}</text>'
            f'<text class="eje" x="2" y="{y1:.0f}">{piso:,.0f}</text>'
            f'<text class="eje" x="{x0:.0f}" y="{alto - 3}">{serie[0]["fecha"][5:]}</text>'
            f'<text class="eje fin" x="{x1:.0f}" y="{alto - 3}" text-anchor="end">'
            f'{serie[-1]["fecha"][5:]}</text>'
        )
    piezas.append("</svg>")
    return "".join(piezas)


ESTILO_GRAFICA = """
.grafica { display:block; overflow:visible; }
.grafica .banda { fill:currentColor; opacity:.14; stroke:none; }
.grafica .linea { stroke:currentColor; stroke-width:1.6; stroke-linejoin:round; }
.grafica .punta { fill:currentColor; }
.grafica .eje { font-size:8.5px; font-family:ui-monospace,Consolas,monospace;
        fill:currentColor; opacity:.55; }
"""
