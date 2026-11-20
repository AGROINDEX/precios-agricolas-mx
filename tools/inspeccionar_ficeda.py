"""Busca el endpoint de datos del visor de mayoreo de la FICEDA.

Uso: python tools/inspeccionar_ficeda.py [url]
"""
import re
import sys

import web_util

URL = "http://201.99.114.63:81/central-abasto/visor_mayoreo.php"

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else URL
    pagina = web_util.traer(url)
    print("bytes:", len(pagina))

    print("--- rutas .php y .json mencionadas ---")
    for ruta in sorted(set(re.findall(r"[A-Za-z0-9_./\-]+\.(?:php|json)", pagina))):
        print("  ", ruta)

    print("--- llamadas de datos ---")
    for linea in pagina.splitlines():
        if re.search(r"ajax|\.get\(|\.post\(|fetch\(|XMLHttpRequest|url\s*:", linea, re.I):
            print("  ", web_util.sin_acentos(linea.strip()[:220]))

    print("--- selects y formularios ---")
    for forma in re.findall(r"<form[^>]*>", pagina, re.I):
        print("  FORMA", web_util.sin_acentos(forma[:200]))
    for nombre, lista in web_util.opciones(pagina).items():
        print(f"  SELECT {nombre}: {len(lista)} opciones")
        for valor, texto in lista[:6]:
            print("     ", valor, "::", web_util.sin_acentos(texto)[:50])
    for nombre, tipo, valor in web_util.campos(pagina)[:30]:
        print(f"  CAMPO {nombre} tipo={tipo} valor={web_util.sin_acentos(valor[:30])}")
