"""B1 · el esquema rechaza el duplicado por llave natural.

Mide sobre una base temporal, no sobre la de produccion: un gate no debe
cambiar el artefacto que evalua.
"""
import os
import sqlite3
import sys
import tempfile

import gate_util
from gate_util import exigir

MARCADOR = "esquema verificado · duplicado rechazado por llave natural"

LLAVE = ("fuente", "fecha_dato", "producto", "calidad", "presentacion", "origen", "mercado")


def fila_base():
    return {
        "fuente": "SNIIM_FYH",
        "fecha_dato": "2026-11-19",
        "hora_dato": None,
        "categoria": "Frutas",
        "producto": "Limon con semilla",
        "calidad": "Primera",
        "presentacion": "Arpilla de 15 kg.",
        "origen": "Michoacan",
        "mercado": "DF: Central de Abasto de Iztapalapa DF",
        "observaciones": "",
        "precio_min": 15.2,
        "precio_max": 15.47,
        "precio_frec": 15.33,
        "moneda": "MXN",
        "base_precio": "kilogramo",
        "alcance": "mayoreo",
        "consulta_url": "https://ejemplo/consulta",
        "capturado_en": "2026-11-20T10:00:00+00:00",
    }


def verificar():
    import comun

    detalles = []
    carpeta = tempfile.mkdtemp(prefix="gate_esquema_")
    base = os.path.join(carpeta, "prueba.db")
    conexion = comun.conectar(base)

    fila = fila_base()
    primera = comun.guardar(conexion, [fila])
    exigir(primera == (1, 0), f"la primera insercion debio ser nueva y fue {primera}")

    segunda = comun.guardar(conexion, [dict(fila)])
    exigir(segunda == (0, 1), f"la fila identica debio rechazarse y dio {segunda}")

    total = conexion.execute("SELECT COUNT(*) FROM precios").fetchone()[0]
    exigir(total == 1, f"la tabla debio quedar con una fila y tiene {total}")
    detalles.append(f"fila identica rechazada · total en tabla: {total}")

    # Cambiar un solo campo de la llave si debe producir una fila nueva: sin
    # esto, un UNIQUE demasiado ancho pasaria el gate sin distinguir nada.
    for campo in LLAVE:
        distinta = dict(fila)
        if campo == "fecha_dato":
            distinta[campo] = "2026-11-18"
        elif campo == "fuente":
            # La fuente no se puede inventar: es llave foranea. Se usa la otra
            # fuente real del catalogo, que es la variacion legitima del campo.
            distinta[campo] = "FICEDA_CDMX"
        else:
            distinta[campo] = (fila[campo] or "x") + "-variante"
        resultado = comun.guardar(conexion, [distinta])
        exigir(
            resultado == (1, 0),
            f"cambiar {campo} debio producir una fila nueva y dio {resultado}",
        )
    detalles.append(f"los {len(LLAVE)} campos de la llave natural discriminan")

    # La restriccion tiene que estar en el esquema, no solo en el codigo que
    # inserta: manana alguien puede insertar con otro cliente.
    definicion = conexion.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'precios'"
    ).fetchone()[0]
    exigir("UNIQUE" in definicion.upper(), "el esquema de precios no declara UNIQUE")
    for campo in LLAVE:
        exigir(campo in definicion, f"la definicion no menciona {campo}")
    detalles.append("UNIQUE declarado en el esquema y no solo en la ingesta")

    directa = sqlite3.connect(base)
    try:
        directa.execute(
            "INSERT INTO precios (fuente, fecha_dato, producto, calidad, presentacion, origen,"
            " mercado, observaciones, base_precio, alcance, consulta_url, capturado_en)"
            " VALUES ('SNIIM_FYH','2026-11-19','Limon con semilla','Primera','Arpilla de 15 kg.',"
            "'Michoacan','DF: Central de Abasto de Iztapalapa DF','','kilogramo','mayoreo','u','t')"
        )
        raise gate_util.Fallo("un INSERT directo duplicado no fue rechazado por la base")
    except sqlite3.IntegrityError:
        detalles.append("INSERT directo duplicado rechazado por la base")
    finally:
        directa.close()
        conexion.close()

    return detalles


if __name__ == "__main__":
    sys.exit(gate_util.correr(verificar, MARCADOR))
