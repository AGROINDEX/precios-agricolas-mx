"""Prueba variantes de ruta del SNIIM hasta ubicar la consulta viva.

Uso: python tools/probar_variantes.py
"""
import urllib.error

import web_util

BASE = "https://www.economia-sniim.gob.mx"

VARIANTES = [
    "/MercadosNacionales/PreciosDeMercado/Agricolas/ConsultaFrutasYHortalizas.aspx",
    "/MercadosNacionales/PreciosDeMercado/Agricolas/ConsultaFrutasYHortalizas.aspx?SubOpcion=4",
    "/Nuevo/MercadosNacionales/PreciosDeMercado/Agricolas/ConsultaFrutasYHortalizas.aspx?SubOpcion=4",
    "/Nuevo/Home.aspx?opcion=Consultas/MercadosNacionales/PreciosDeMercado/Agricolas/ConsultaFrutasYHortalizas.aspx?SubOpcion=4",
    "/SNIIM-Frutas-Y-Hortalizas/ConsultasFrutasYHortalizas.asp",
    "/MercadosNacionales/PreciosDeMercado/Agricolas/ResultadosConsultaFechaFrutasYHortalizas.aspx",
    "/Nuevo/MercadosNacionales/PreciosDeMercado/Agricolas/ResultadosConsultaFechaFrutasYHortalizas.aspx",
]

if __name__ == "__main__":
    for ruta in VARIANTES:
        url = BASE + ruta
        try:
            pagina = web_util.traer(url, tiempo=30)
            titulo = ""
            inicio = pagina.lower().find("<title>")
            if inicio != -1:
                titulo = web_util.plano(pagina[inicio : inicio + 200])[:70]
            print(f"OK   {len(pagina):>7} bytes  {ruta}  :: {web_util.sin_acentos(titulo)}")
        except urllib.error.HTTPError as error:
            print(f"HTTP {error.code:>7}        {ruta}")
        except Exception as error:  # noqa: BLE001
            print(f"FALLO {type(error).__name__}  {ruta}  {error}")
