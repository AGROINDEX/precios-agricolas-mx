"""B14 · el aviso de plaza quieta falla en la transicion, no en el estado.

TRES CONTROLES, cada uno en su base temporal, cada uno con un desenlace
distinto. Si los tres no se distinguen, el aviso no sirve:

  se_estanca   plaza que venia moviendose y hoy republica los valores de ayer.
               Tiene que FALLAR, porque ese es el dia en que algo se rompio.
  quieta       plaza que lleva diez dias publicando los mismos numeros. NO debe
               fallar: ya se sabia, y una alerta diaria por un estado conocido
               es la alerta que nadie mira. Debe quedar reportada.
  viva         plaza que cambia precios todos los dias. Ni falla ni reporta.

Se mide por codigo de salida y por el texto del aviso, corriendo el vigilante
como lo corre el CI, no importando sus funciones.
"""
import os
import subprocess
import sys
import tempfile
from datetime import date, timedelta

import gate_util
from gate_util import exigir, ruta

MARCADOR = "aviso de plaza quieta verificado · falla en la transicion y no en el estado persistente"
VIGILANTE = ruta("ingesta", "check_plazas_quietas.py")

DIAS = 10
PRODUCTOS = 12


def fila(fecha, mercado, indice, precio):
    return {
        "fuente": "SNIIM_FYH",
        "fecha_dato": fecha,
        "hora_dato": None,
        "categoria": "Hortalizas",
        "producto": f"Producto de control {indice}",
        "calidad": "Primera",
        "presentacion": "Kilogramo",
        "origen": "Control",
        "mercado": mercado,
        "observaciones": "",
        "precio_min": precio - 1,
        "precio_max": precio + 1,
        "precio_frec": precio,
        "moneda": "MXN",
        "base_precio": "kilogramo",
        "alcance": "mayoreo",
        "consulta_url": "https://www.economia-sniim.gob.mx/control",
        "capturado_en": f"{fecha}T12:00:00+00:00",
    }


def construir(caso, carpeta):
    import comun

    base = os.path.join(carpeta, f"{caso}.db")
    conexion = comun.conectar(base)
    hoy = date.today()
    mercado = f"Plaza de control {caso}"
    filas = []
    for atras in range(DIAS):
        fecha = (hoy - timedelta(days=atras)).isoformat()
        for indice in range(PRODUCTOS):
            if caso == "quieta":
                precio = 11.0 + indice
            elif caso == "viva":
                precio = 11.0 + indice + atras * 0.75
            else:  # se_estanca: se movia hasta ayer y hoy repite el valor de ayer
                dias_movidos = max(atras - 1, 0)
                precio = 11.0 + indice + dias_movidos * 0.75
            filas.append(fila(fecha, mercado, indice, round(precio, 2)))
    comun.guardar(conexion, filas)
    conexion.close()
    return base


def correr(base):
    resultado = subprocess.run(
        [sys.executable, VIGILANTE, "--base", base],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
    )
    return resultado.returncode, (resultado.stdout or "") + (resultado.stderr or "")


def verificar():
    detalles = []
    carpeta = tempfile.mkdtemp(prefix="gate_plaza_quieta_")

    codigo, salida = correr(construir("se_estanca", carpeta))
    exigir(
        codigo != 0,
        "la plaza que dejo de moverse no hizo fallar al vigilante: no avisa de la transicion",
    )
    exigir("dejo de moverse" in salida, "el aviso no nombra la transicion")
    exigir("Plaza de control se_estanca" in salida, "el aviso no nombra la plaza")
    detalles.append("plaza que se estanca: falla, con el aviso nombrando la plaza")

    codigo, salida = correr(construir("quieta", carpeta))
    exigir(
        codigo == 0,
        "la plaza quieta desde siempre hizo fallar al vigilante: eso es gritar todos los dias"
        " lo mismo, que es como se entrena a ignorarlo",
    )
    exigir("quieta conocida" in salida, "la plaza quieta conocida no quedo reportada")
    exigir("::error::" not in salida, "el estado conocido se reporto como error")
    detalles.append("plaza quieta desde siempre: no falla y queda reportada como estado conocido")

    codigo, salida = correr(construir("viva", carpeta))
    exigir(codigo == 0, "la plaza que se mueve hizo fallar al vigilante")
    exigir("quieta conocida" not in salida, "la plaza que se mueve quedo marcada como quieta")
    exigir("::error::" not in salida, "la plaza que se mueve genero un error")
    detalles.append("plaza viva: ni falla ni reporta")

    # El vigilante en vivo tiene que poder correr sobre la base real sin romperse.
    codigo, salida = correr(ruta("datos", "pista_b", "precios.db"))
    exigir(
        "movimiento verificado" in salida or "PLAZAS QUE EMPEORARON" in salida,
        f"el vigilante no produjo veredicto sobre la base real: {salida.strip()[-200:]}",
    )
    detalles.append(f"sobre la base real: {salida.strip().splitlines()[-1][:110]}")

    # Y tiene que estar cableado en el flujo del vigilante, no solo existir.
    with open(ruta(".github", "workflows", "vigilante-diario.yml"), encoding="utf-8") as archivo:
        flujo = archivo.read()
    exigir(
        "check_plazas_quietas.py" in flujo,
        "el aviso de plaza quieta no corre en el flujo del vigilante",
    )
    detalles.append("cableado en vigilante-diario.yml")
    return detalles


if __name__ == "__main__":
    sys.exit(gate_util.correr(verificar, MARCADOR))
