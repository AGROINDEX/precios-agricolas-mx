"""Lista enlaces, formularios y campos de una pagina, para ubicar la consulta.

Uso: python tools/listar_enlaces.py <url> [patron]
"""
import re
import sys

import web_util

if __name__ == "__main__":
    url = sys.argv[1]
    patron = sys.argv[2] if len(sys.argv) > 2 else "."
    pagina = web_util.traer(url)
    print(f"bytes: {len(pagina)}")
    for href, texto in web_util.enlaces(pagina, patron)[:120]:
        print(f"ENLACE {href}  ::  {web_util.sin_acentos(texto)}")
    for forma in re.findall(r"<form[^>]*>", pagina, re.I):
        print("FORMA", web_util.sin_acentos(forma[:200]))
    for nombre, tipo, valor in web_util.campos(pagina)[:60]:
        print(f"CAMPO {nombre} tipo={tipo} valor={web_util.sin_acentos(valor[:40])}")
    for nombre, lista in web_util.opciones(pagina).items():
        print(f"SELECT {nombre}: {len(lista)} opciones")
        for valor, texto in lista[:8]:
            print(f"   {valor} :: {web_util.sin_acentos(texto)[:60]}")
