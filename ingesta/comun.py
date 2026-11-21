"""Capa comun de la ingesta: base, upsert idempotente, reporte de fetch y poda.

Solo stdlib a proposito: la ingesta corre en CI sin instalar nada, igual que en
AgroPatentIndex.
"""
import json
import os
import sqlite3
import urllib.request
from datetime import date, datetime, timedelta, timezone

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(RAIZ, "datos", "pista_b", "precios.db")
ESQUEMA = os.path.join(RAIZ, "esquema", "schema.sql")
REPORTE = os.path.join(RAIZ, "datos", "pista_b", "_fetch_report.json")

UA = "precios-agricolas/0.1 (ingesta incremental diaria con atribucion)"

# Catalogo de fuentes. El veredicto de licencia vive aqui y en su ficha, y la
# ingesta se niega a escribir una fuente en rojo.
FUENTES = {
    "SNIIM_FYH": {
        "nombre": "SNIIM · Secretaria de Economia, frutas y hortalizas",
        "url_base": (
            "https://www.economia-sniim.gob.mx/Nuevo/Consultas/MercadosNacionales/"
            "PreciosDeMercado/Agricolas/ResultadosConsultaFechaFrutasYHortalizas.aspx"
        ),
        "atribucion": "Fuente: SNIIM, Secretaria de Economia (economia-sniim.gob.mx)",
        "licencia_veredicto": "amarillo",
        "licencia_ficha": "licencias/sniim.md",
        "alcance": "mayoreo",
        "critica": 1,
        "ventana_dias": 90,
    },
    "FICEDA_CDMX": {
        "nombre": "Central de Abasto de la Ciudad de Mexico · FICEDA",
        "url_base": "http://201.99.114.63:81/central-abasto/visor_mayoreo.php",
        "atribucion": "Fuente: Central de Abasto de la Ciudad de Mexico, FICEDA",
        "licencia_veredicto": "amarillo",
        "licencia_ficha": "licencias/ficeda.md",
        "alcance": "mayoreo",
        "critica": 1,
        "ventana_dias": 90,
    },
}

# Cadencia de publicacion DECLARADA por plaza, con el umbral de silencio que le
# corresponde.
#
# POR QUE EXISTE. El silencio de una plaza solo se puede juzgar contra su propia
# cadencia. La Central de Abasto de Cuautla dejo de publicar el 16 de octubre de
# 2025 y nadie lo noto, porque el vigilante mide por FUENTE y el SNIIM seguia
# bajando todos los dias gracias a Iztapalapa. Y al revez: el Mercado Adolfo
# Lopez Mateos publica solo los lunes, asi que juzgarlo con el umbral diario lo
# declararia muerto cada martes.
#
# `dias` usa la numeracion de datetime.weekday(): lunes 0, domingo 6. En una
# plaza diaria es None y se asume la semana habil, porque el SNIIM no publica
# sabados ni domingos.
CADENCIAS = {
    "DF: Central de Abasto de Iztapalapa DF": {
        "cadencia": "diaria",
        "dias": None,
        "umbral_dias": 3,
    },
    "Michoacan: Mercado de Abasto de Morelia": {
        "cadencia": "diaria",
        "dias": None,
        "umbral_dias": 3,
    },
    "Morelos: Mercado Adolfo Lopez Mateos de Cuernavaca": {
        "cadencia": "semanal",
        "dias": [0],
        # Diez dias son el lunes esperado mas la misma holgura de tres dias que
        # se le da a una plaza diaria. Menos que eso grita cada semana.
        "umbral_dias": 10,
    },
    # Medida, no supuesta: publico de lunes a viernes sin faltar, 98 dias en
    # cinco meses, y murio de golpe el 31 de octubre de 2025. Se declara con la
    # cadencia que TENIA, porque es contra esa que habria que juzgarla el dia en
    # que reaparezca.
    "Morelos: Central de Abasto de Cuautla": {
        "cadencia": "diaria",
        "dias": None,
        "umbral_dias": 3,
    },
    "DF: Central de Abasto de Iztapalapa (FICEDA)": {
        "cadencia": "diaria",
        "dias": None,
        "umbral_dias": 3,
    },
}

# Una plaza sin cadencia declarada se trata como diaria y se DICE que no esta
# declarada, en vez de inventarle una cadencia que la haga ver sana.
CADENCIA_SIN_DECLARAR = {"cadencia": "sin declarar", "dias": None, "umbral_dias": 3}


def cadencia(mercado):
    return CADENCIAS.get(mercado, CADENCIA_SIN_DECLARAR)


def toca_publicar(mercado, dia):
    """Le toca publicar a esta plaza ese dia, segun su cadencia declarada."""
    regla = cadencia(mercado)
    if regla["dias"] is not None:
        return dia.weekday() in regla["dias"]
    return dia.weekday() < 5  # el SNIIM no publica sabados ni domingos


def frase_cadencia(mercado):
    """Como se le dice al usuario, sin jerga."""
    regla = cadencia(mercado)
    if regla["cadencia"] == "semanal":
        nombres = ["los lunes", "los martes", "los miercoles", "los jueves",
                   "los viernes", "los sabados", "los domingos"]
        dias = " y ".join(nombres[d] for d in regla["dias"])
        return f"esta plaza publica una vez por semana, {dias}"
    if regla["cadencia"] == "diaria":
        return "esta plaza publica cada dia habil"
    return "cadencia de esta plaza todavia sin declarar"


CAMPOS = (
    "fuente",
    "fecha_dato",
    "hora_dato",
    "categoria",
    "producto",
    "calidad",
    "presentacion",
    "origen",
    "mercado",
    "observaciones",
    "precio_min",
    "precio_max",
    "precio_frec",
    "moneda",
    "base_precio",
    "alcance",
    "consulta_url",
    "capturado_en",
)


def ahora():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def conectar(ruta=None):
    destino = ruta or BASE
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    conexion = sqlite3.connect(destino)
    conexion.execute("PRAGMA foreign_keys = ON")
    with open(ESQUEMA, encoding="utf-8") as archivo:
        conexion.executescript(archivo.read())
    migrar(conexion)
    sembrar_fuentes(conexion)
    return conexion


def migrar(conexion):
    """Migraciones chicas e idempotentes, para bases creadas antes de un cambio."""
    columnas = {fila[1] for fila in conexion.execute("PRAGMA table_info(precios)")}
    if "base_precio" not in columnas:
        conexion.execute("ALTER TABLE precios ADD COLUMN base_precio TEXT NOT NULL DEFAULT ''")
        conexion.execute("UPDATE precios SET base_precio = 'kilogramo' WHERE fuente = 'SNIIM_FYH'")
        conexion.execute("UPDATE precios SET base_precio = 'presentacion' WHERE fuente = 'FICEDA_CDMX'")
        conexion.commit()


def sembrar_fuentes(conexion):
    for clave, datos in FUENTES.items():
        conexion.execute(
            """
            INSERT INTO fuentes (clave, nombre, url_base, atribucion, licencia_veredicto,
                                 licencia_ficha, alcance, critica, ventana_dias)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT (clave) DO UPDATE SET
                nombre = excluded.nombre,
                url_base = excluded.url_base,
                atribucion = excluded.atribucion,
                licencia_veredicto = excluded.licencia_veredicto,
                licencia_ficha = excluded.licencia_ficha,
                alcance = excluded.alcance,
                critica = excluded.critica,
                ventana_dias = excluded.ventana_dias
            """,
            (
                clave,
                datos["nombre"],
                datos["url_base"],
                datos["atribucion"],
                datos["licencia_veredicto"],
                datos["licencia_ficha"],
                datos["alcance"],
                datos["critica"],
                datos["ventana_dias"],
            ),
        )
    conexion.commit()


def traer(url, tiempo=60):
    peticion = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(peticion, timeout=tiempo) as respuesta:
        crudo = respuesta.read()
    for codificacion in ("utf-8", "cp1252", "latin-1"):
        try:
            return crudo.decode(codificacion)
        except UnicodeDecodeError:
            continue
    return crudo.decode("utf-8", "replace")


def guardar(conexion, filas):
    """Inserta solo lo nuevo. Devuelve (insertadas, repetidas).

    La idempotencia no se logra comparando a mano: la da la llave natural del
    esquema mas INSERT OR IGNORE. Si manana cambia el parser y produce la misma
    fila, no se duplica.
    """
    insertadas = 0
    repetidas = 0
    marcadores = ", ".join("?" for _ in CAMPOS)
    sentencia = f"INSERT OR IGNORE INTO precios ({', '.join(CAMPOS)}) VALUES ({marcadores})"
    for fila in filas:
        if FUENTES[fila["fuente"]]["licencia_veredicto"] == "rojo":
            raise SystemExit(f"fuente {fila['fuente']} esta en rojo: no se integra")
        cursor = conexion.execute(sentencia, tuple(fila.get(campo) for campo in CAMPOS))
        if cursor.rowcount == 1:
            insertadas += 1
        else:
            repetidas += 1
    conexion.commit()
    return insertadas, repetidas


def podar(conexion, clave_fuente):
    """Deja solo la ventana declarada. Esto es el articulo 108 hecho codigo."""
    ventana = FUENTES[clave_fuente]["ventana_dias"]
    corte = (date.today() - timedelta(days=ventana)).isoformat()
    cursor = conexion.execute(
        "DELETE FROM precios WHERE fuente = ? AND fecha_dato < ?", (clave_fuente, corte)
    )
    conexion.execute(
        "DELETE FROM derivados WHERE fuente = ? AND fecha_dato < ?", (clave_fuente, corte)
    )
    conexion.commit()
    return cursor.rowcount


def leer_reporte(ruta=None):
    destino = ruta or REPORTE
    if not os.path.exists(destino):
        return {"fuentes": {}}
    with open(destino, encoding="utf-8") as archivo:
        return json.load(archivo)


def anotar_fetch(clave_fuente, exito, filas_nuevas, detalle="", ruta=None):
    """Memoria entre corridas. Se versiona, igual que en AgroPatentIndex.

    Lo que importa no es la fecha del archivo sino `ultimo_fetch_bueno`: una
    fuente puede responder 200 con cero filas y eso no es un fetch bueno.
    """
    destino = ruta or REPORTE
    reporte = leer_reporte(destino)
    entrada = reporte["fuentes"].get(clave_fuente, {})
    entrada["nombre"] = FUENTES[clave_fuente]["nombre"]
    entrada["critical"] = bool(FUENTES[clave_fuente]["critica"])
    entrada["ultimo_intento"] = ahora()
    entrada["ultimo_detalle"] = detalle
    if exito:
        entrada["ultimo_fetch_bueno"] = ahora()
        entrada["filas_ultimo_fetch"] = filas_nuevas
    reporte["fuentes"][clave_fuente] = entrada
    reporte["actualizado_en"] = ahora()
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8") as archivo:
        json.dump(reporte, archivo, ensure_ascii=False, indent=2, sort_keys=True)
    return entrada


def numero(texto):
    limpio = (texto or "").replace("$", "").replace(",", "").strip()
    try:
        return float(limpio)
    except ValueError:
        return None
