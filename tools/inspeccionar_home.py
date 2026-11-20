"""Busca en Home.aspx del SNIIM la ruta real del contenido de consulta.

Uso: python tools/inspeccionar_home.py [url]
"""
import re
import sys

import web_util

URL = (
    "https://www.economia-sniim.gob.mx/Nuevo/Home.aspx?opcion=Consultas/MercadosNacionales/"
    "PreciosDeMercado/Agricolas/ConsultaFrutasYHortalizas.aspx?SubOpcion=4"
)

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else URL
    pagina = web_util.traer(url)
    print("bytes:", len(pagina))

    for etiqueta in ("iframe", "frame", "form"):
        for encontrado in re.findall(rf"<{etiqueta}[^>]*>", pagina, re.I):
            print(etiqueta.upper(), web_util.sin_acentos(encontrado[:220]))

    print("--- rutas .aspx y .asp mencionadas ---")
    rutas = sorted(set(re.findall(r"[A-Za-z0-9_./\-]+\.asp[x]?", pagina)))
    for ruta in rutas[:60]:
        print("  ", ruta)

    print("--- scripts externos ---")
    for src in sorted(set(re.findall(r'<script[^>]+src="([^"]+)"', pagina, re.I))):
        print("  ", src)

    print("--- menciones de ajax o load ---")
    for linea in pagina.splitlines():
        if re.search(r"\.load\(|ajax|XMLHttpRequest|fetch\(", linea, re.I):
            print("  ", web_util.sin_acentos(linea.strip()[:180]))
