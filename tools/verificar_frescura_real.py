"""B13 · la frescura real por plaza esta medida sobre el movimiento, no sobre la fecha.

TRES MITADES, y las tres hacen falta:

1. Recalculo independiente. El verificador vuelve a calcular, con SQL directo y
   sin usar el modulo que se evalua, cuantos productos cambiaron de precio en el
   ultimo corte y cuantos nunca cambiaron en la ventana. Si el modulo y el
   recalculo no coinciden, el gate falla.
2. Control de plaza estancada. Se arma en una base temporal una plaza que
   republica los mismos valores diez dias seguidos con fecha nueva cada dia, que
   es justo el modo en que una fuente parece fresca sin serlo, y se exige que el
   veredicto sea estancada. Sin este control, un medidor que siempre dijera
   viva pasaria igual.
3. La medida esta a la vista. La pagina publica el veredicto de cada plaza con
   datos y dice que mide movimiento y no fecha declarada.

Uso:
  python tools/verificar_frescura_real.py --control-estancado
"""
import argparse
import os
import sys
import tempfile

import gate_util
from gate_util import exigir

MARCADOR = "frescura real verificada · recalculo coincide y plaza estancada detectada"


def recalcular(conexion, fuente, mercado):
    """Mismas dos cifras, por otro camino: SQL directo sobre precios."""
    fechas = [
        fila[0]
        for fila in conexion.execute(
            "SELECT DISTINCT fecha_dato FROM precios WHERE fuente = ? AND mercado = ?"
            " AND precio_frec IS NOT NULL ORDER BY fecha_dato",
            (fuente, mercado),
        )
    ]
    if len(fechas) < 2:
        return None, None
    ultimo, anterior = fechas[-1], fechas[-2]

    movieron = conexion.execute(
        """
        SELECT SUM(CASE WHEN ABS(u.v - a.v) > 0.005 THEN 1 ELSE 0 END), COUNT(*)
        FROM (SELECT producto, AVG(precio_frec) v FROM precios
              WHERE fuente = ? AND mercado = ? AND fecha_dato = ? AND precio_frec IS NOT NULL
              GROUP BY producto) u
        JOIN (SELECT producto, AVG(precio_frec) v FROM precios
              WHERE fuente = ? AND mercado = ? AND fecha_dato = ? AND precio_frec IS NOT NULL
              GROUP BY producto) a ON a.producto = u.producto
        """,
        (fuente, mercado, ultimo, fuente, mercado, anterior),
    ).fetchone()
    prop_movio = (movieron[0] or 0) / movieron[1] if movieron[1] else None

    planos = conexion.execute(
        """
        SELECT SUM(CASE WHEN distintos = 1 THEN 1 ELSE 0 END), COUNT(*)
        FROM (SELECT producto, COUNT(DISTINCT ROUND(v, 2)) distintos, COUNT(*) dias
              FROM (SELECT producto, fecha_dato, AVG(precio_frec) v FROM precios
                    WHERE fuente = ? AND mercado = ? AND precio_frec IS NOT NULL
                    GROUP BY producto, fecha_dato)
              GROUP BY producto HAVING dias >= 5)
        """,
        (fuente, mercado),
    ).fetchone()
    prop_planos = (planos[0] or 0) / planos[1] if planos[1] else None
    return prop_movio, prop_planos


def construir_plaza_estancada(ruta_base):
    """Una plaza que republica los mismos numeros con fecha nueva cada dia."""
    import comun

    from datetime import date, timedelta

    conexion = comun.conectar(ruta_base)
    hoy = date.today()
    filas = []
    for atras in range(10):
        fecha = (hoy - timedelta(days=atras)).isoformat()
        for indice in range(12):
            filas.append(
                {
                    "fuente": "SNIIM_FYH",
                    "fecha_dato": fecha,
                    "hora_dato": None,
                    "categoria": "Hortalizas",
                    "producto": f"Producto de control {indice}",
                    "calidad": "Primera",
                    "presentacion": "Kilogramo",
                    "origen": "Control",
                    "mercado": "Plaza de control estancada",
                    "observaciones": "",
                    "precio_min": 10.0 + indice,
                    "precio_max": 12.0 + indice,
                    "precio_frec": 11.0 + indice,
                    "moneda": "MXN",
                    "base_precio": "kilogramo",
                    "alcance": "mayoreo",
                    "consulta_url": "https://www.economia-sniim.gob.mx/control",
                    "capturado_en": f"{fecha}T12:00:00+00:00",
                }
            )
    comun.guardar(conexion, filas)
    return conexion


def verificar(con_control):
    import comun
    from frescura_real import medir, medir_plaza, series_por_plaza

    detalles = []
    conexion = comun.conectar()
    medidas = medir(conexion)
    exigir(medidas, "no hay ninguna plaza medida")

    medidas_utiles = 0
    for fuente, plazas in medidas.items():
        for mercado, medida in plazas.items():
            prop_movio, prop_planos = recalcular(conexion, fuente, mercado)
            if prop_movio is None:
                exigir(
                    medida["veredicto"] == "sin_medir",
                    f"{mercado} no tiene dia anterior publicado y aun asi recibio veredicto"
                    f" {medida['veredicto']}: eso afirma lo que no se sabe",
                )
                detalles.append(f"{mercado}: sin dia anterior, declarada sin medir")
                continue
            medidas_utiles += 1
            exigir(
                abs(medida["prop_movio_ultimo"] - prop_movio) < 0.005,
                f"{mercado}: el modulo dice {medida['prop_movio_ultimo']} de movimiento y el"
                f" recalculo da {prop_movio:.4f}",
            )
            exigir(
                abs(medida["prop_planos"] - prop_planos) < 0.005,
                f"{mercado}: el modulo dice {medida['prop_planos']} de planos y el recalculo"
                f" da {prop_planos:.4f}",
            )
            exigir(
                medida["mediana_edad_valor"] is not None,
                f"{mercado} no trae edad del valor, que es la mitad de la medida",
            )
            detalles.append(
                f"{mercado}: {medida['veredicto']} · movimiento {prop_movio * 100:.0f} por ciento"
                f" · planos {prop_planos * 100:.0f} por ciento"
                f" · edad mediana {medida['mediana_edad_valor']:.0f} dias"
            )
    conexion.close()
    exigir(medidas_utiles > 0, "ninguna plaza tiene dos dias publicados: no se midio nada")

    if con_control:
        carpeta = tempfile.mkdtemp(prefix="gate_frescura_real_")
        base = os.path.join(carpeta, "control.db")
        conexion_control = construir_plaza_estancada(base)
        series = series_por_plaza(conexion_control)
        clave = ("SNIIM_FYH", "Plaza de control estancada")
        exigir(clave in series, "no se pudo construir la plaza de control")
        medida = medir_plaza(series[clave])
        conexion_control.close()
        exigir(
            medida["veredicto"] == "estancada",
            f"la plaza de control republica los mismos numeros diez dias y el veredicto fue"
            f" {medida['veredicto']}: el medidor no sirve",
        )
        exigir(
            medida["prop_planos"] == 1.0,
            f"la plaza de control deberia dar 100 por ciento de planos y dio {medida['prop_planos']}",
        )
        exigir(
            medida["mediana_edad_valor"] >= 9,
            f"la edad mediana del valor de control deberia ser de al menos nueve dias y fue"
            f" {medida['mediana_edad_valor']}",
        )
        detalles.append(
            "control: plaza que republica diez dias con fecha nueva marcada como estancada,"
            " con 100 por ciento de planos"
        )

    # La medida tiene que estar a la vista, no solo calculada. La vista son
    # ahora el indice y una pagina por plaza, asi que se leen todas: mirar solo
    # el indice dejaria de comprobar lo que dice cada plaza de si misma.
    pagina = ""
    for camino in gate_util.paginas_generadas():
        with open(camino, encoding="utf-8") as archivo:
            pagina += archivo.read()
    exigir('class="pulso' in pagina, "la pagina no publica el veredicto de movimiento por plaza")
    exigir(
        "no la fecha que la fuente declara" in pagina,
        "la pagina no dice que esto mide movimiento y no fecha declarada",
    )
    for fuente, plazas in medidas.items():
        for mercado, medida in plazas.items():
            if medida["veredicto"] == "estancada":
                exigir(
                    "casi no se mueve" in pagina,
                    f"{mercado} esta estancada y la pagina no lo dice",
                )
    detalles.append("veredicto por plaza visible en la pagina publicada")
    return detalles


if __name__ == "__main__":
    lector = argparse.ArgumentParser(description="Verifica la frescura real por plaza")
    lector.add_argument("--control-estancado", action="store_true")
    argumentos = lector.parse_args()
    sys.exit(gate_util.correr(lambda: verificar(argumentos.control_estancado), MARCADOR))
