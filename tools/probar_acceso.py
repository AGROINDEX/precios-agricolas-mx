"""Sonda de alcanzabilidad de las dos fuentes de la pista B.

Solo hace GET y reporta estado, tamano y tipo de contenido. No guarda nada.
Verificacion TLS activada: si una fuente no presenta certificado valido, eso
es un hallazgo del diagnostico y no algo que se deba silenciar.
"""
import time
import urllib.error
import urllib.request

PRUEBAS = [
    ("SNIIM home", "https://www.economia-sniim.gob.mx/nuevo/"),
    ("SNIIM consulta frutas", "https://www.economia-sniim.gob.mx/SNIIM-Frutas-Y-Hortalizas/ConsultasFrutasYHortalizas.asp"),
    ("SNIIM robots", "https://www.economia-sniim.gob.mx/robots.txt"),
    ("FICEDA visor", "http://201.99.114.63:81/central-abasto/visor_mayoreo.php"),
]

UA = "precios-agricolas/0.1 (ingesta incremental con atribucion)"

for nombre, url in PRUEBAS:
    inicio = time.time()
    try:
        peticion = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(peticion, timeout=30) as respuesta:
            cuerpo = respuesta.read()
        print(
            f"{nombre}: {respuesta.status} · {len(cuerpo)} bytes · "
            f"{time.time() - inicio:.1f}s · {respuesta.headers.get('Content-Type')}"
        )
    except urllib.error.HTTPError as error:
        print(f"{nombre}: HTTP {error.code} · {time.time() - inicio:.1f}s")
    except Exception as error:  # noqa: BLE001
        print(f"{nombre}: FALLO {type(error).__name__} · {error} · {time.time() - inicio:.1f}s")
