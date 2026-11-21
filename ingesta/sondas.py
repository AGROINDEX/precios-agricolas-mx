"""Registro de INTENTOS por plaza, para vigilar plazas muertas.

POR QUE EL INTENTO Y NO LA FILA. Una plaza muerta no tiene ni una fila en la
base, y todo lo que este producto mide por plaza recorre las filas de `precios`.
En el sistema normal, una plaza muerta es invisible: no aparece en la frescura,
no aparece en la cadencia, no aparece en la pagina. Para enterarse del dia en
que vuelve hay que guardar la prueba de que se pregunto, no solo la respuesta.

Es la misma leccion del vigilante de fuentes congeladas, que mide dias desde el
ultimo fetch BUENO y no la antiguedad del archivo. Aqui se guarda, por plaza:

  intentos                 cuantas veces se le pregunto desde que se vigila
  ultimo_intento           cuando se le pregunto por ultima vez
  intentos_sin_filas       cuantos intentos seguidos devolvieron cero filas
  ultimo_intento_con_filas cuando devolvio filas por ultima vez, si alguna vez
  filas_ultimo_intento     cuantas filas trajo el ultimo intento

El archivo se versiona, igual que `_fetch_report.json`: el corredor de CI es
efimero y sin versionarlo cada corrida empezaria sin memoria y la vigilancia no
podria distinguir una plaza muerta de una recien observada.
"""
import json
import os

from comun import RAIZ, ahora

SONDAS = os.path.join(RAIZ, "datos", "pista_b", "_sondas.json")


def leer(ruta=None):
    destino = ruta or SONDAS
    if not os.path.exists(destino):
        return {"plazas": {}}
    with open(destino, encoding="utf-8") as archivo:
        return json.load(archivo)


def anotar(clave, plaza_id, nombre, filas, ruta=None, momento=None):
    """Registra un intento. Devuelve (registro, reaparecio).

    `reaparecio` es True solo en la TRANSICION: el intento trae filas y el
    anterior no traia ninguna. Asi el aviso sale el dia que la plaza vuelve y
    no todos los dias desde entonces.
    """
    destino = ruta or SONDAS
    datos = leer(destino)
    llave = f"{clave}:{plaza_id}"
    registro = datos["plazas"].get(llave) or {
        "fuente": clave,
        "plaza_id": plaza_id,
        "nombre": nombre,
        "intentos": 0,
        "intentos_sin_filas": 0,
        "primer_intento": None,
        "ultimo_intento": None,
        "ultimo_intento_con_filas": None,
        "filas_ultimo_intento": 0,
    }

    venia_vacia = registro["intentos"] > 0 and registro["intentos_sin_filas"] > 0
    sello = momento or ahora()

    registro["nombre"] = nombre
    registro["intentos"] += 1
    registro["primer_intento"] = registro["primer_intento"] or sello
    registro["ultimo_intento"] = sello
    registro["filas_ultimo_intento"] = filas

    if filas > 0:
        registro["ultimo_intento_con_filas"] = sello
        registro["intentos_sin_filas"] = 0
    else:
        registro["intentos_sin_filas"] += 1

    reaparecio = filas > 0 and venia_vacia

    datos["plazas"][llave] = registro
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2, sort_keys=True)
    return registro, reaparecio
