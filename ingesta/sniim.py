"""Ingesta incremental del SNIIM, frutas y hortalizas, por dia y por plaza.

RUTA REAL. La consulta no vive donde el paquete de arranque suponia. Las rutas
sin el segmento `Nuevo/Consultas/` devuelven 404: la pagina publica es un
Home.aspx con un iframe, y el contenido real esta en

  /Nuevo/Consultas/MercadosNacionales/PreciosDeMercado/Agricolas/
      ResultadosConsultaFechaFrutasYHortalizas.aspx

Acepta GET con parametros, sin autenticacion y sin viewstate, lo que permite
ingesta incremental limpia. Verificado el 20 de noviembre de 2026.

QUE SE PIDE Y QUE NO. Se pide un dia y una plaza por peticion, con
ProductoId=-1 para traer todos los productos de esa plaza en una sola llamada.
No se recorre el historico: `robots.txt` del sitio prohibe /Analisis/, *.xls,
/2010/ y /Sicia*, y el articulo 108 de la LFDA prohibe replicar el acervo. Lo
que se guarda es la ventana declarada en `comun.FUENTES`.

Uso:
  python ingesta/sniim.py                      # hoy, plazas del piloto
  python ingesta/sniim.py --fecha 2026-11-19
  python ingesta/sniim.py --plazas 100,160 --base otra.db
"""
import argparse
import re
import sys
from datetime import date, datetime

import comun_bootstrap  # noqa: F401  (pone el paquete en el path)
from comun import (
    FUENTES,
    anotar_fetch,
    conectar,
    guardar,
    numero,
    podar,
    traer,
)

CLAVE = "SNIIM_FYH"

# Plazas del piloto. Iztapalapa es la referencia nacional de mayoreo y Morelia
# es la plaza que mas cerca queda del precio en origen de Michoacan, que es el
# diferenciador del producto.
PLAZAS = {
    "100": "DF: Central de Abasto de Iztapalapa DF",
    "160": "Michoacan: Mercado de Abasto de Morelia",
    "140": "Jalisco: Mercado de Abasto de Guadalajara",
}

PILOTO = ["100", "160"]

ENCABEZADO = ("producto", "calidad", "presentacion", "origen")


def limpiar(fragmento):
    import html

    texto = html.unescape(re.sub(r"<[^>]+>", " ", fragmento))
    return re.sub(r"\s+", " ", texto.replace("\xa0", " ")).strip()


def plegar(texto):
    """Minusculas sin acentos, solo para comparar encabezados.

    El encabezado real dice Presentacion con acento, y comparar con el texto
    crudo fue lo que hizo que la primera version leyera cero filas.
    """
    tabla = str.maketrans("áéíóúÁÉÍÓÚñÑüÜ", "aeiouAEIOUnNuU")
    return texto.translate(tabla).lower()


def url_consulta(dia, plaza_id, plaza_nombre):
    fecha = dia.strftime("%d/%m/%Y")
    return (
        FUENTES[CLAVE]["url_base"]
        + f"?fechaInicio={fecha}&fechaFinal={fecha}"
        + "&ProductoId=-1&OrigenId=-1&Origen=Todos"
        + f"&DestinoId={plaza_id}&Destino={plaza_nombre.replace(' ', '%20')}"
        + "&PreciosPorId=2&RegistrosPorPagina=3000"
    )


def extraer(pagina, dia, plaza_nombre, url, capturado_en):
    """Saca las filas de la tabla de resultados.

    La pagina trae once tablas de maquetacion. La buena es la unica cuyo
    encabezado empieza con Producto, Calidad, Presentacion y Origen, y dentro de
    ella hay filas de una sola celda que son el nombre de la categoria, Frutas u
    Hortalizas, no datos.
    """
    filas_salida = []
    categoria = None
    for tabla in re.findall(r"<table.*?</table>", pagina, re.S | re.I):
        filas = re.findall(r"<tr.*?</tr>", tabla, re.S | re.I)
        if len(filas) < 2:
            continue
        encabezado = [plegar(limpiar(c)) for c in re.findall(r"<t[dh].*?</t[dh]>", filas[0], re.S | re.I)]
        if len(encabezado) < 8 or tuple(encabezado[:4]) != ENCABEZADO:
            continue
        for fila in filas[1:]:
            celdas = [limpiar(c) for c in re.findall(r"<t[dh].*?</t[dh]>", fila, re.S | re.I)]
            if not celdas:
                continue
            utiles = [c for c in celdas if c]
            if len(utiles) == 1:
                categoria = utiles[0]
                continue
            if len(celdas) < 7:
                continue
            producto, calidad, presentacion, origen = celdas[0], celdas[1], celdas[2], celdas[3]
            if not producto:
                continue
            filas_salida.append(
                {
                    "fuente": CLAVE,
                    "fecha_dato": dia.isoformat(),
                    "hora_dato": None,  # el SNIIM publica por dia, sin hora
                    "categoria": categoria,
                    "producto": producto,
                    "calidad": calidad,
                    "presentacion": presentacion,
                    "origen": origen,
                    "mercado": plaza_nombre,
                    "observaciones": celdas[7] if len(celdas) > 7 else "",
                    "precio_min": numero(celdas[4]),
                    "precio_max": numero(celdas[5]),
                    "precio_frec": numero(celdas[6]),
                    "moneda": "MXN",
                    # PreciosPorId=2 en la consulta: kilogramo calculado.
                    "base_precio": "kilogramo",
                    "alcance": "mayoreo",
                    "consulta_url": url,
                    "capturado_en": capturado_en,
                }
            )
    return filas_salida


def correr(dia, plazas, ruta_base=None, ruta_reporte=None):
    from comun import ahora

    conexion = conectar(ruta_base)
    capturado_en = ahora()
    total_nuevas = 0
    total_filas = 0
    detalles = []
    error = None
    for plaza_id in plazas:
        nombre = PLAZAS[plaza_id]
        url = url_consulta(dia, plaza_id, nombre)
        try:
            pagina = traer(url)
        except Exception as fallo:  # noqa: BLE001
            error = f"{plaza_id}: {type(fallo).__name__} {fallo}"
            detalles.append(error)
            continue
        filas = extraer(pagina, dia, nombre, url, capturado_en)
        nuevas, repetidas = guardar(conexion, filas)
        total_nuevas += nuevas
        total_filas += len(filas)
        detalles.append(f"{plaza_id}: {len(filas)} filas, {nuevas} nuevas, {repetidas} repetidas")
    podadas = podar(conexion, CLAVE)
    conexion.close()

    # Un fetch bueno exige filas. Un 200 con la tabla vacia no cuenta, que es
    # justo el modo en que una fuente se congela sin avisar.
    exito = total_filas > 0 and error is None
    anotar_fetch(CLAVE, exito, total_nuevas, " · ".join(detalles), ruta_reporte)
    print(f"SNIIM {dia.isoformat()} · {total_filas} filas leidas · {total_nuevas} nuevas · {podadas} podadas")
    for detalle in detalles:
        print("  ", detalle)
    return 0 if exito else 1


if __name__ == "__main__":
    lector = argparse.ArgumentParser(description="Ingesta incremental del SNIIM")
    lector.add_argument("--fecha", default=date.today().isoformat())
    lector.add_argument("--plazas", default=",".join(PILOTO))
    lector.add_argument(
        "--dias",
        type=int,
        default=1,
        help="dias hacia atras a partir de --fecha, dentro de la ventana declarada",
    )
    lector.add_argument("--base")
    lector.add_argument("--reporte")
    argumentos = lector.parse_args()
    dia_pedido = datetime.strptime(argumentos.fecha, "%Y-%m-%d").date()

    ventana = FUENTES[CLAVE]["ventana_dias"]
    if argumentos.dias > ventana:
        raise SystemExit(f"--dias {argumentos.dias} excede la ventana declarada de {ventana} dias")

    # De mas viejo a mas nuevo a proposito: la ultima anotacion del reporte de
    # fetch debe ser la del dia mas reciente, porque es la que mide la frescura.
    # Un sabado sin publicacion no es una fuente congelada, asi que el codigo de
    # salida lo decide el ultimo dia pedido, no el relleno.
    from datetime import timedelta

    codigo = 0
    for atras in range(argumentos.dias - 1, -1, -1):
        codigo = correr(
            dia_pedido - timedelta(days=atras),
            argumentos.plazas.split(","),
            argumentos.base,
            argumentos.reporte,
        )
    sys.exit(codigo)
