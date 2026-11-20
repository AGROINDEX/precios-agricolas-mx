"""Imprime la estructura de la tabla de resultados del SNIIM.

Uso: python tools/ver_resultados.py "<url completa>" [filas]
"""
import re
import sys

import web_util

if __name__ == "__main__":
    url = sys.argv[1]
    limite = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    pagina = web_util.traer(url, tiempo=60)
    print("bytes:", len(pagina))

    titulos = re.findall(r"<h\d[^>]*>(.*?)</h\d>", pagina, re.S | re.I)
    for titulo in titulos[:6]:
        print("TITULO", web_util.sin_acentos(web_util.plano(titulo))[:120])

    tablas = re.findall(r"<table.*?</table>", pagina, re.S | re.I)
    print("tablas:", len(tablas))
    for indice, tabla in enumerate(tablas):
        filas = re.findall(r"<tr.*?</tr>", tabla, re.S | re.I)
        if len(filas) < 2:
            continue
        print(f"\n=== tabla {indice} · {len(filas)} filas ===")
        for fila in filas[:limite]:
            celdas = [web_util.sin_acentos(web_util.plano(c))[:28] for c in re.findall(r"<t[dh].*?</t[dh]>", fila, re.S | re.I)]
            if celdas:
                print(" | ".join(celdas))

    texto = web_util.plano(pagina)
    for aviso in ("No se encontraron", "no existe", "error", "Error"):
        if aviso in texto:
            posicion = texto.find(aviso)
            print("AVISO:", web_util.sin_acentos(texto[max(0, posicion - 90) : posicion + 110]))
            break
