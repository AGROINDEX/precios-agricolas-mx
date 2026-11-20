"""Banco de pruebas de los verificadores de la pista A.

POR QUE EXISTE. Los gates A3 a A7 estan en rojo porque todavia no hay cohortes
ni bitacora reales. Un verificador que hoy siempre falla podria estar roto y
nadie lo notaria hasta el dia en que el fundador cargue a quince personas y el
gate siga en rojo sin razon.

Este banco arma datos sinteticos en una carpeta temporal, con el desvio
`PRECIOS_DATOS_PISTA_A`, y exige dos cosas de cada verificador:

  1. Con datos completos y validos, se pone en verde.
  2. Con un solo defecto introducido a proposito, vuelve a rojo.

No toca los registros reales y no cierra ningun gate: es la prueba de que los
gates de la pista A pueden cerrarse.

Uso:
  python tools/autoprueba_pista_a.py
"""
import json
import os
import subprocess
import sys
import tempfile
from datetime import date, timedelta

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERRAMIENTAS = os.path.join(RAIZ, "tools")

HOY = date.today()
INICIO = HOY - timedelta(days=6)


def cohorte_vendedor(n=15):
    return {
        "lado": "vendedor",
        "registros": [
            {
                "id": f"v{indice:02d}",
                "nombre": f"Productora sintetica {indice}",
                "rol": "productor",
                "cultivo": "aguacate hass",
                "plaza": "Michoacan: Mercado de Abasto de Morelia",
                "canal": "whatsapp",
                "contacto": f"+52 443 000 00{indice:02d}",
                "fuente_del_contacto": "banco de pruebas, no es una persona real",
                "consentimiento": {
                    "fecha": INICIO.isoformat(),
                    "medio": "mensaje de whatsapp",
                    "texto": "si, mandenmelo todos los dias por favor",
                },
            }
            for indice in range(1, n + 1)
        ],
    }


def cohorte_comprador(n=3):
    tipos = ["mayorista", "exportador", "cadena"]
    return {
        "lado": "comprador",
        "registros": [
            {
                "id": f"c{indice:02d}",
                "empresa": f"Comercializadora sintetica {indice}",
                "persona": f"Responsable de compras {indice}",
                "cargo": "compras",
                "tipo": tipos[(indice - 1) % len(tipos)],
                "contacto": f"compras{indice}@comercializadora{indice}.mx",
                "fecha_conversacion": (INICIO + timedelta(days=indice)).isoformat(),
                "fuente_del_contacto": "banco de pruebas, no es una empresa real",
            }
            for indice in range(1, n + 1)
        ],
    }


def bitacora(boletin_relativo):
    envios = []
    for dia in range(7):
        fecha = (INICIO + timedelta(days=dia)).isoformat()
        envios.append(
            {
                "fecha": fecha,
                "lado": "vendedor",
                "boletin": boletin_relativo,
                "canal": "whatsapp",
                "destinatarios": [f"v{indice:02d}" for indice in range(1, 16)],
                "lecturas": 9,
            }
        )
    respuestas = [
        {
            "fecha": (INICIO + timedelta(days=2)).isoformat(),
            "lado": "vendedor",
            "contacto": "v03",
            "tipo": "precio_propio",
            "texto": "aqui en el huerto me estan pagando 28.50 el kilo",
            "precio": {
                "producto": "Aguacate Hass",
                "precio": 28.5,
                "plaza": "huerto, Tacambaro",
                "base": "kilogramo",
            },
        }
    ]
    for indice in range(1, 4):
        respuestas.append(
            {
                "fecha": (INICIO + timedelta(days=3 + indice)).isoformat(),
                "lado": "comprador",
                "contacto": f"c{indice:02d}",
                "tipo": "disposicion_a_pagar",
                "precio_puesto": 1500 + indice * 250,
                "periodo": "mensual",
                "texto": "respuesta sintetica suficientemente larga para el gate",
                "clasificacion": ["pagaria", "condicionada", "no_pagaria"][indice - 1],
            }
        )
    return {"envios": envios, "respuestas": respuestas}


def correr(argumentos, carpeta):
    entorno = dict(os.environ, PRECIOS_DATOS_PISTA_A=carpeta, PYTHONIOENCODING="utf-8")
    resultado = subprocess.run(
        [sys.executable] + argumentos,
        cwd=RAIZ,
        env=entorno,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )
    return resultado.returncode, (resultado.stdout or "") + (resultado.stderr or "")


def escribir(carpeta, nombre, datos):
    with open(os.path.join(carpeta, nombre), "w", encoding="utf-8") as archivo:
        json.dump(datos, archivo, ensure_ascii=False, indent=2)


CASOS = (
    (["tools/verificar_cohortes.py", "--lado", "vendedor", "--minimo", "15"], "cohorte vendedor"),
    (["tools/verificar_cohortes.py", "--lado", "comprador", "--minimo", "3"], "cohorte comprador"),
    (["tools/verificar_bitacora_envio.py", "--dias", "7"], "bitacora"),
    (["tools/verificar_metricas.py", "--lado", "vendedor"], "metrica vendedor"),
    (["tools/verificar_metricas.py", "--lado", "comprador"], "metrica comprador"),
)

# Un defecto por verificador, para comprobar que no se pone en verde con
# cualquier cosa.
def romper_consentimiento(datos):
    datos["cohorte_vendedor.json"]["registros"][4]["consentimiento"]["texto"] = ""


def romper_tipo(datos):
    datos["cohorte_comprador.json"]["registros"][1]["tipo"] = "amigo"


def romper_racha(datos):
    datos["bitacora.json"]["envios"].pop(3)


def romper_lecturas(datos):
    for envio in datos["bitacora.json"]["envios"]:
        envio.pop("lecturas", None)


def romper_clasificacion(datos):
    for respuesta in datos["bitacora.json"]["respuestas"]:
        if respuesta.get("tipo") == "disposicion_a_pagar":
            respuesta["clasificacion"] = "tal vez"


DEFECTOS = (romper_consentimiento, romper_tipo, romper_racha, romper_lecturas, romper_clasificacion)


def main():
    boletin = os.path.join(RAIZ, "boletin", "ultimo.md")
    if not os.path.exists(boletin):
        print("FALLO · no existe boletin/ultimo.md, que es lo que la bitacora sintetica cita")
        return 1

    fallos = []
    for (argumentos, etiqueta), defecto in zip(CASOS, DEFECTOS):
        carpeta = tempfile.mkdtemp(prefix="autoprueba_a_")
        datos = {
            "cohorte_vendedor.json": cohorte_vendedor(),
            "cohorte_comprador.json": cohorte_comprador(),
            "bitacora.json": bitacora("boletin/ultimo.md"),
        }
        for nombre, contenido in datos.items():
            escribir(carpeta, nombre, contenido)

        codigo, salida = correr(argumentos, carpeta)
        if codigo != 0:
            fallos.append(f"{etiqueta}: con datos validos salio en rojo · {salida.strip().splitlines()[-1]}")
            continue

        defecto(datos)
        for nombre, contenido in datos.items():
            escribir(carpeta, nombre, contenido)
        codigo_roto, salida_rota = correr(argumentos, carpeta)
        if codigo_roto == 0:
            fallos.append(f"{etiqueta}: con el defecto introducido siguio en verde")
            continue
        print(f"ok   {etiqueta}: verde con dato valido, rojo con el defecto · {salida_rota.strip().splitlines()[-1][:90]}")

    if fallos:
        for linea in fallos:
            print(f"FALLO · {linea}")
        return 1
    print("autoprueba de la pista A superada · los cinco verificadores distinguen dato valido de defecto")
    return 0


if __name__ == "__main__":
    sys.exit(main())
