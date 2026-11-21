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
from datetime import date, datetime, timedelta

import comun_bootstrap  # noqa: F401  (pone el paquete en el path)
from sondas import anotar as anotar_sonda
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

# El catalogo de plazas, el piloto y la lista de vigilancia vienen MEDIDOS del
# censo generado, no escritos a mano. Son 49 plazas en el desplegable, 41 que
# publicaron en la ventana y 8 que no. Se regenera con
# `python ingesta/medir_cadencia.py --escribir`.
from cadencias import PILOTO, PLAZAS, VIGILANCIA  # noqa: E402,F401

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


def url_consulta(desde, hasta, plaza_id):
    """Una peticion por plaza para TODO el rango.

    POR QUE POR RANGO. Llenar la ventana de 90 dias con una peticion por dia
    serian 90 por 41 plazas, o sea 3,690 peticiones. Por rango son 41. El
    endpoint acepta `fechaInicio` distinto de `fechaFinal` desde siempre y no lo
    estabamos usando.

    El parametro `Destino`, el del nombre, es decorativo: el servidor rotula la
    plaza a partir de `DestinoId`. Se manda fijo para no depender de que el
    nombre coincida caracter por caracter con el del catalogo.
    """
    return (
        FUENTES[CLAVE]["url_base"]
        + f"?fechaInicio={desde.strftime('%d/%m/%Y')}&fechaFinal={hasta.strftime('%d/%m/%Y')}"
        + "&ProductoId=-1&OrigenId=-1&Origen=Todos"
        + f"&DestinoId={plaza_id}&Destino=Todos"
        + "&PreciosPorId=2&RegistrosPorPagina=100000"
    )


def extraer(pagina, dia, plaza_nombre, url, capturado_en):
    """Saca las filas de la tabla de resultados.

    DOS FORMAS DE LA MISMA TABLA. Pedida por un solo dia, el encabezado empieza
    en Producto. Pedida por rango, trae una columna Fecha al frente y todas las
    demas corridas una posicion. Se detecta por el encabezado y se LEE la fecha
    de cada fila en vez de asumir la del dia pedido, que ademas es mejor por si
    solo: si la fuente publica tarde, la fila llega con su fecha correcta.

    La pagina trae once tablas de maquetacion. La buena es la unica cuyo
    encabezado empieza con Producto, o con Fecha y luego Producto, y dentro de
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
        if len(encabezado) >= 8 and tuple(encabezado[:4]) == ENCABEZADO:
            desfase = 0
        elif len(encabezado) >= 9 and tuple(encabezado[1:5]) == ENCABEZADO:
            desfase = 1
        else:
            continue
        for fila in filas[1:]:
            celdas = [limpiar(c) for c in re.findall(r"<t[dh].*?</t[dh]>", fila, re.S | re.I)]
            if not celdas:
                continue
            utiles = [c for c in celdas if c]
            if len(utiles) == 1:
                categoria = utiles[0]
                continue
            if len(celdas) < 7 + desfase:
                continue
            fecha_fila = dia
            if desfase:
                if not re.match(r"\d{2}/\d{2}/\d{4}", celdas[0]):
                    continue
                dia_s, mes_s, anio_s = celdas[0].split("/")
                fecha_fila = date(int(anio_s), int(mes_s), int(dia_s))
            celdas = celdas[desfase:]
            producto, calidad, presentacion, origen = celdas[0], celdas[1], celdas[2], celdas[3]
            if not producto:
                continue
            filas_salida.append(
                {
                    "fuente": CLAVE,
                    "fecha_dato": fecha_fila.isoformat(),
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


def plazas_por_defecto():
    """A quien se le pregunta en una corrida normal.

    Las del piloto porque publican, y las de vigilancia porque dejaron de
    publicar y la unica forma de notar que vuelven es seguir preguntando. De
    estas ultimas no se guardan filas: se guarda el intento.
    """
    return list(PILOTO) + list(VIGILANCIA)


def dias_a_pedir(conexion, ventana, reciente=10):
    """Cuantos dias hacia atras pedir, mirando lo que ya hay en la base.

    POR QUE SE DECIDE Y NO SE FIJA. La base ya no se versiona: vive en la cache
    del corredor de CI, y una cache se puede perder. Si se perdio, hay que
    rellenar la ventana completa; si esta ahi, basta con los ultimos dias, que
    ademas recoge las publicaciones tardias y las plazas de cadencia semanal.
    Pedir siempre la ventana completa serian unos 160 MB diarios a un servidor
    de 2003, y pedir siempre pocos dias dejaria la vista historica vacia el dia
    que la cache se pierda.
    """
    fila = conexion.execute(
        "SELECT COUNT(*), MAX(fecha_dato) FROM precios WHERE fuente = ?", (CLAVE,)
    ).fetchone()
    if not fila or not fila[0] or not fila[1]:
        return ventana, "base vacia"
    ultimo = datetime.strptime(fila[1], "%Y-%m-%d").date()
    atraso = (date.today() - ultimo).days
    if atraso > reciente:
        return ventana, f"la base venia {atraso} dias atrasada"
    return reciente, f"la base esta al dia, ultimo corte {fila[1]}"


def correr(desde, hasta, plazas, ruta_base=None, ruta_reporte=None, ruta_sondas=None):
    from comun import ahora

    conexion = conectar(ruta_base)
    capturado_en = ahora()
    total_nuevas = 0
    total_filas = 0
    detalles = []
    error = None
    for plaza_id in plazas:
        nombre = PLAZAS[plaza_id]
        url = url_consulta(desde, hasta, plaza_id)
        try:
            # Una respuesta de 90 dias de una plaza grande pesa varios MB y el
            # servidor tarda. El tiempo de espera por defecto no alcanza.
            pagina = traer(url, tiempo=180)
        except Exception as fallo:  # noqa: BLE001
            error = f"{plaza_id}: {type(fallo).__name__} {fallo}"
            detalles.append(error)
            continue
        filas = extraer(pagina, hasta, nombre, url, capturado_en)
        if plaza_id in VIGILANCIA:
            # Se anota el intento ANTES de guardar: lo que esta sonda vigila es
            # si la plaza respondio con filas, no si esas filas eran nuevas.
            _registro, reaparecio = anotar_sonda(CLAVE, plaza_id, nombre, len(filas), ruta_sondas)
            if reaparecio:
                detalles.append(f"{plaza_id}: REAPARECIO con {len(filas)} filas")
            # De una plaza en vigilancia no se guardan filas aunque las traiga:
            # primero hay que medirle la cadencia nueva y promoverla al piloto.
            # Guardarlas en silencio seria meter al tablero una plaza cuya
            # cadencia nadie declaro.
            if filas:
                detalles.append(f"{plaza_id}: {len(filas)} filas NO guardadas, esta en vigilancia")
            continue
        nuevas, repetidas = guardar(conexion, filas)
        total_nuevas += nuevas
        total_filas += len(filas)
        if len(filas) or plaza_id in plazas[:5]:
            detalles.append(f"{plaza_id}: {len(filas)} filas, {nuevas} nuevas, {repetidas} repetidas")
    podadas = podar(conexion, CLAVE)
    dias_base = conexion.execute(
        "SELECT COUNT(DISTINCT fecha_dato) FROM precios WHERE fuente = ?", (CLAVE,)
    ).fetchone()[0]
    conexion.close()

    # Un fetch bueno exige filas. Un 200 con la tabla vacia no cuenta, que es
    # justo el modo en que una fuente se congela sin avisar. Las plazas en
    # vigilancia no cuentan: estan muertas a proposito y exigirles filas
    # pondria la ingesta en rojo todos los dias, que es como se entrena a
    # cualquiera a ignorar una alerta.
    exito = total_filas > 0 and error is None
    anotar_fetch(CLAVE, exito, total_nuevas, " · ".join(detalles[:12]), ruta_reporte)
    print(
        f"SNIIM {desde.isoformat()} a {hasta.isoformat()} · {len(plazas)} plazas · "
        f"{total_filas} filas leidas · {total_nuevas} nuevas · {podadas} podadas · "
        f"{dias_base} dias en la base"
    )
    for detalle in detalles:
        print("  ", detalle)
    return 0 if exito else 1


if __name__ == "__main__":
    lector = argparse.ArgumentParser(description="Ingesta del SNIIM por rango de fechas")
    lector.add_argument("--hasta", default=date.today().isoformat())
    lector.add_argument(
        "--dias",
        default="auto",
        help="dias hacia atras desde --hasta, o auto para decidirlo mirando la base",
    )
    lector.add_argument("--plazas", default=",".join(plazas_por_defecto()))
    lector.add_argument("--base")
    lector.add_argument("--reporte")
    lector.add_argument("--sondas")
    argumentos = lector.parse_args()

    hasta = datetime.strptime(argumentos.hasta, "%Y-%m-%d").date()
    ventana = FUENTES[CLAVE]["ventana_dias"]

    if argumentos.dias == "auto":
        conexion_previa = conectar(argumentos.base)
        dias, motivo = dias_a_pedir(conexion_previa, ventana)
        conexion_previa.close()
        print(f"pidiendo {dias} dias: {motivo}")
    else:
        dias = int(argumentos.dias)
        if dias > ventana:
            raise SystemExit(f"--dias {dias} excede la ventana declarada de {ventana} dias")

    sys.exit(
        correr(
            hasta - timedelta(days=dias),
            hasta,
            [p for p in argumentos.plazas.split(",") if p],
            argumentos.base,
            argumentos.reporte,
            argumentos.sondas,
        )
    )
