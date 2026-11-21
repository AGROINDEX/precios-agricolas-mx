"""B19 · una plaza semanal no se presenta como dato detenido, y la pagina dice su cadencia.

EL PROBLEMA QUE ESTE GATE VIGILA. La edad del valor se mide en dias de
calendario. En una plaza que publica cada lunes, un precio que cambio en la
ultima publicacion tiene siete dias de edad, y decirle al usuario que "la mitad
de los precios lleva siete dias sin moverse" describe como estancada a una plaza
que esta al dia. La unidad correcta para esa plaza es la publicacion.

CUATRO COMPROBACIONES:

1. La frase de una plaza semanal habla en publicaciones y no en dias.
2. La frase de una plaza diaria SIGUE hablando en dias. Sin esto, cambiar la
   unidad para todos pasaria el punto 1 y romperia el caso normal.
3. La pagina dice la cadencia de cada plaza junto a su corte. Control positivo:
   una pagina que presenta la plaza semanal como diaria es rechazada.
4. Una plaza semanal que esta al dia no recibe aviso de falta, y una plaza
   diaria callada varios dias si queda reportada. Se arman las dos en una base
   de control, porque la plaza real puede estar en cualquiera de los dos
   estados el dia que corra el gate.

Uso:
  python tools/verificar_frescura_cadencia.py --control-positivo
"""
import argparse
import os
import sys
import tempfile
from datetime import date, timedelta

import gate_util
from gate_util import exigir, ruta

# El constructor de la pagina vive en web/ y gate_util solo lo pone en el path
# cuando tiene que generar la pagina. Aqui se necesita siempre, porque el
# control arma una pagina desde una base de control.
sys.path.insert(0, ruta("web"))

MARCADOR = "frescura por cadencia verificada · control de plaza semanal como diaria rechazado"

SEMANAL = 'Morelos: Mercado "Adolfo López Mateos" de Cuernavaca'
DIARIA = "DF: Central de Abasto de Iztapalapa DF"


def citas_previas(mercado, cuantas, hoy=None):
    """Ultimos dias de cadencia estrictamente anteriores a hoy, de viejo a nuevo."""
    from comun import toca_publicar

    hoy = hoy or date.today()
    salida = []
    dia = hoy - timedelta(days=1)
    while len(salida) < cuantas:
        if toca_publicar(mercado, dia):
            salida.append(dia)
        dia -= timedelta(days=1)
    return list(reversed(salida))


def dice_la_cadencia(pagina, plazas_cadencias):
    """Toda plaza de la pagina trae su frase de cadencia. Funcion pura.

    DOS TRAMPAS QUE ESTA FUNCION YA TUVO. La primera: el nombre de varias
    plazas lleva comillas, y en la pagina va escapado como &quot;, asi que
    buscarlo crudo no lo encuentra nunca. La segunda, peor: si no se encuentra
    el nombre, saltar esa plaza en silencio convierte la comprobacion en
    decorativa justo para las plazas de nombre dificil, que resultaron ser las
    que importaban. Ahora no encontrar una plaza es una falla, no un salto.
    """
    import html as modulo_html

    faltantes = []
    for mercado, frase_esperada in plazas_cadencias.items():
        aguja = modulo_html.escape(mercado)
        if aguja not in pagina:
            faltantes.append(f"{mercado} (no aparece en la vista)")
            continue
        bloque = pagina.split(aguja, 1)[1][:1200]
        if frase_esperada not in bloque:
            faltantes.append(mercado)
    return faltantes


def verificar(con_control):
    import comun
    from comun import cadencia, frase_cadencia
    from frescura_real import frase, medir

    detalles = []

    conexion = comun.conectar()
    medidas = medir(conexion)
    plazas = {
        mercado: frase_cadencia(mercado)
        for plazas_fuente in medidas.values()
        for mercado in plazas_fuente
    }
    conexion.close()

    # 1 y 2. La unidad de la frase depende de la cadencia.
    semanales = [
        (fuente, mercado, medida)
        for fuente, plazas_fuente in medidas.items()
        for mercado, medida in plazas_fuente.items()
        if cadencia(mercado)["cadencia"] == "semanal"
    ]
    exigir(semanales, "no hay ninguna plaza semanal medida: este gate no mide nada")
    for _fuente, mercado, medida in semanales:
        if medida["prop_movio_ultimo"] is None:
            continue
        texto = frase(medida)
        exigir(
            "publicacion" in texto,
            f"{mercado} es semanal y su frase no habla de publicaciones: {texto}",
        )
        exigir(
            "dias o mas sin moverse" not in texto,
            f"{mercado} es semanal y su frase cuenta la antiguedad en dias de calendario,"
            f" que describe como detenida a una plaza al dia: {texto}",
        )
        exigir(
            medida["mediana_edad_publicaciones"] is not None,
            f"{mercado} no trae la edad del valor en publicaciones",
        )
        detalles.append(f"{mercado}: {texto}")

    diarias = [
        (mercado, medida)
        for plazas_fuente in medidas.values()
        for mercado, medida in plazas_fuente.items()
        if cadencia(mercado)["cadencia"] == "diaria" and medida["prop_movio_ultimo"] is not None
    ]
    exigir(diarias, "no hay ninguna plaza diaria medida: falta el control del caso normal")
    for mercado, medida in diarias:
        texto = frase(medida)
        exigir(
            "publicaciones semanales" not in texto,
            f"{mercado} es diaria y su frase habla de publicaciones semanales: {texto}",
        )
    detalles.append(f"{len(diarias)} plazas diarias siguen contando la antiguedad en dias")

    # 3. La pagina dice la cadencia de cada plaza.
    pagina = ""
    for camino in gate_util.paginas_generadas():
        with open(camino, encoding="utf-8") as archivo:
            pagina += archivo.read()
    faltantes = dice_la_cadencia(pagina, plazas)
    exigir(
        not faltantes,
        f"la pagina no dice la cadencia junto al corte de: {faltantes}",
    )
    detalles.append(f"la pagina declara la cadencia de las {len(plazas)} plazas")

    if con_control:
        # Control de la comprobacion 3: una pagina que presenta la plaza
        # semanal como diaria tiene que ser rechazada por la misma funcion.
        frase_semanal = frase_cadencia(SEMANAL)
        frase_diaria = "esta plaza publica cada dia habil"
        exigir(
            frase_semanal != frase_diaria,
            "las dos frases de cadencia son iguales: el control no prueba nada",
        )
        exigir(
            frase_semanal in pagina,
            f"la pagina real no trae la frase semanal, no hay nada que desfigurar: {frase_semanal}",
        )
        pagina_mentirosa = pagina.replace(frase_semanal, frase_diaria)
        rechazo = dice_la_cadencia(pagina_mentirosa, plazas)
        exigir(
            SEMANAL in rechazo,
            "la comprobacion acepto una pagina que presenta la plaza semanal como diaria:"
            " no esta mirando la cadencia",
        )
        detalles.append("control: pagina que presenta la plaza semanal como diaria, rechazada")

        # 4. Dos plazas de control en base aparte: una semanal al dia y una
        # diaria callada. La pagina de control no debe avisar de la primera y el
        # vigilante si debe reportar la segunda.
        from check_cadencia import evaluar
        import construir

        carpeta = tempfile.mkdtemp(prefix="gate_frescura_cadencia_")
        base = os.path.join(carpeta, "control.db")
        conexion = comun.conectar(base)
        from verificar_cadencia import sembrar

        sembrar(conexion, SEMANAL, citas_previas(SEMANAL, 3))
        sembrar(conexion, DIARIA, citas_previas(DIARIA, 3, date.today() - timedelta(days=5)))
        conexion.close()

        conexion = comun.conectar(base)
        faltaron, calladas, sanas = evaluar(conexion)
        conexion.close()
        nombres_sanas = {registro["mercado"] for registro in sanas}
        reportadas = {registro["mercado"] for registro in faltaron} | {
            registro["mercado"] for registro in calladas
        }
        exigir(
            SEMANAL in nombres_sanas,
            "la plaza semanal al dia no quedo como sana: se la esta juzgando con el umbral"
            " diario",
        )
        exigir(
            DIARIA in reportadas,
            "la plaza diaria callada cinco dias no quedo reportada: asi murio Cuautla sin"
            " que nadie lo notara",
        )

        salida = os.path.join(carpeta, "control.html")
        construir.construir(base, ruta("datos", "pista_b", "_fetch_report.json"), salida)
        with open(salida, encoding="utf-8") as archivo:
            control = archivo.read()
        import html as modulo_html

        bloque_semanal = control.split(modulo_html.escape(SEMANAL), 1)[1][:1500]
        exigir(
            "falto a su publicacion" not in bloque_semanal,
            "la pagina avisa que la plaza semanal falto a su publicacion cuando esta al dia",
        )
        exigir(
            frase_semanal in bloque_semanal,
            "la pagina de control no declara la cadencia de la plaza semanal",
        )
        detalles.append(
            "control: plaza semanal al dia sin aviso de falta, plaza diaria callada"
            " cinco dias reportada"
        )

    return detalles


if __name__ == "__main__":
    lector = argparse.ArgumentParser(description="Verifica la frescura segun la cadencia")
    lector.add_argument("--control-positivo", action="store_true")
    argumentos = lector.parse_args()
    sys.exit(gate_util.correr(lambda: verificar(argumentos.control_positivo), MARCADOR))
