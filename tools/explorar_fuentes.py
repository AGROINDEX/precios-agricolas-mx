"""Exploracion de la forma de consulta del SNIIM y del visor de la FICEDA.

Diagnostico de una sola vez: imprime robots.txt, los enlaces de consulta del
SNIIM y los campos de cada formulario. No guarda datos de precio.
"""
import html
import re
import sys
import urllib.error
import urllib.request

UA = "precios-agricolas/0.1 (ingesta incremental con atribucion)"


def traer(url):
    peticion = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(peticion, timeout=30) as respuesta:
        crudo = respuesta.read()
    for codificacion in ("utf-8", "cp1252", "latin-1"):
        try:
            return crudo.decode(codificacion)
        except UnicodeDecodeError:
            continue
    return crudo.decode("utf-8", "replace")


def sin_acentos(texto):
    tabla = str.maketrans("áéíóúÁÉÍÓÚñÑüÜ", "aeiouAEIOUnNuU")
    return texto.translate(tabla)


def imprimir(etiqueta, texto):
    print(f"--- {etiqueta} ---")
    print(sin_acentos(texto))


def enlaces(pagina, patron):
    vistos = []
    for href, texto in re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', pagina, re.S | re.I):
        plano = html.unescape(re.sub(r"<[^>]+>", "", texto)).strip()
        if re.search(patron, href + " " + plano, re.I) and href not in [v[0] for v in vistos]:
            vistos.append((href, plano[:70]))
    return vistos


def campos(pagina):
    salida = []
    for etiqueta in re.findall(r"<(?:input|select)[^>]*>", pagina, re.I):
        nombre = re.search(r'name="([^"]+)"', etiqueta, re.I)
        tipo = re.search(r'type="([^"]+)"', etiqueta, re.I)
        valor = re.search(r'value="([^"]*)"', etiqueta, re.I)
        if nombre:
            salida.append(
                f"{nombre.group(1)} tipo={tipo.group(1) if tipo else 'select'} "
                f"valor={valor.group(1)[:30] if valor else ''}"
            )
    return salida


if __name__ == "__main__":
    base = "https://www.economia-sniim.gob.mx"
    imprimir("robots.txt", traer(base + "/robots.txt"))

    inicio = traer(base + "/nuevo/")
    print("--- enlaces de consulta en el home del SNIIM ---")
    encontrados = enlaces(inicio, r"frutas|hortaliza|consulta|precio")
    if not encontrados:
        print("(ningun enlace coincidio con el patron · se listan todos)")
        encontrados = enlaces(inicio, r".")
    for href, texto in encontrados[:60]:
        print(f"{href}  ::  {sin_acentos(texto)}")

    for ruta in sys.argv[1:]:
        url = ruta if ruta.startswith("http") else base + ruta
        print(f"\n=== {url} ===")
        try:
            pagina = traer(url)
        except urllib.error.HTTPError as error:
            print(f"HTTP {error.code}")
            continue
        formas = re.findall(r"<form[^>]*>", pagina, re.I)
        print("formularios:", [sin_acentos(f[:160]) for f in formas])
        print("campos:")
        for campo in campos(pagina)[:60]:
            print("  ", sin_acentos(campo))
        opciones = re.findall(r"<select[^>]+name=\"([^\"]+)\"[^>]*>(.*?)</select>", pagina, re.S | re.I)
        for nombre, bloque in opciones:
            valores = re.findall(r'<option[^>]*value="([^"]*)"[^>]*>(.*?)</option>', bloque, re.S | re.I)
            print(f"  select {nombre}: {len(valores)} opciones, primeras 6 ->")
            for valor, texto in valores[:6]:
                print("     ", valor, "::", sin_acentos(html.unescape(re.sub(r'<[^>]+>', '', texto)).strip())[:50])
