"""Utilidades compartidas de exploracion y descarga.

Se mantiene en stdlib a proposito: la ingesta corre en CI sin instalar nada.
"""
import html
import re
import urllib.request

UA = "precios-agricolas/0.1 (ingesta incremental con atribucion)"


def traer(url, datos=None, tiempo=40):
    peticion = urllib.request.Request(url, data=datos, headers={"User-Agent": UA})
    with urllib.request.urlopen(peticion, timeout=tiempo) as respuesta:
        crudo = respuesta.read()
    for codificacion in ("utf-8", "cp1252", "latin-1"):
        try:
            return crudo.decode(codificacion)
        except UnicodeDecodeError:
            continue
    return crudo.decode("utf-8", "replace")


def sin_acentos(texto):
    tabla = str.maketrans("áéíóúÁÉÍÓÚñÑüÜ°", "aeiouAEIOUnNuUo")
    return texto.translate(tabla)


def plano(fragmento):
    return html.unescape(re.sub(r"<[^>]+>", " ", fragmento)).replace("\xa0", " ").strip()


def enlaces(pagina, patron="."):
    salida = []
    vistos = set()
    for href, texto in re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', pagina, re.S | re.I):
        texto_plano = plano(texto)
        if href in vistos:
            continue
        if re.search(patron, href + " " + texto_plano, re.I):
            vistos.add(href)
            salida.append((href, texto_plano[:80]))
    return salida


def campos(pagina):
    salida = []
    for etiqueta in re.findall(r"<(?:input|select)[^>]*>", pagina, re.I):
        nombre = re.search(r'name="([^"]+)"', etiqueta, re.I)
        tipo = re.search(r'type="([^"]+)"', etiqueta, re.I)
        valor = re.search(r'value="([^"]*)"', etiqueta, re.I)
        if nombre:
            salida.append((nombre.group(1), tipo.group(1) if tipo else "select", valor.group(1) if valor else ""))
    return salida


def opciones(pagina):
    resultado = {}
    for nombre, bloque in re.findall(r'<select[^>]+name="([^"]+)"[^>]*>(.*?)</select>', pagina, re.S | re.I):
        resultado[nombre] = [
            (valor, plano(texto))
            for valor, texto in re.findall(r'<option[^>]*value="([^"]*)"[^>]*>(.*?)</option>', bloque, re.S | re.I)
        ]
    return resultado
