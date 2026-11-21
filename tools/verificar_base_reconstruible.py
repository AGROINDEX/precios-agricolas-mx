"""B23 · la base no se versiona y se reconstruye desde la fuente.

EL PROBLEMA QUE ESTO RESUELVE. Con 42 plazas la base pesa del orden de 130 MB,
y el flujo diario la comiteaba entera: el repositorio crecia eso cada dia. La
salida no es comprimir ni podar mas, es que la base deje de ser memoria. Si
cada corrida reconstruye la ventana con una peticion de rango por plaza, la
base es cache reconstruible y no hay nada que versionar.

QUE SE COMPRUEBA

1. La base esta ignorada por git Y no esta en el indice. Las dos cosas: un
   `.gitignore` no saca del indice un archivo que ya estaba versionado.
2. El flujo de ingesta no la comitea, y si la guarda en la cache del corredor.
3. Lo que SI se versiona es la memoria que no se puede reconstruir: el reporte
   de fetch y el registro de sondas. Si alguien los sacara del commit, se
   perderia saber cuando fue la ultima descarga buena y cuantas veces se le
   pregunto a una plaza muerta.
4. Es de verdad reconstruible: en una base VACIA se rellena la ventana de una
   plaza desde la fuente y se exige profundidad suficiente para la vista.
5. El flujo de publicacion no publica con la base vacia, y lo dice.

Uso:
  python tools/verificar_base_reconstruible.py
"""
import os
import subprocess
import sys
import tempfile
from datetime import date, timedelta

import gate_util
from gate_util import exigir, ruta

MARCADOR = "base reconstruible verificada · no versionada y ventana rellenable desde la fuente"

PLAZA = "100"
# Dias que se piden en la prueba de reconstruccion. No se pide la ventana
# entera: lo que hay que demostrar es que una base vacia se llena desde la
# fuente, y para eso bastan tres semanas. Pedir noventa aqui castigaria a la
# fuente en cada verificacion.
DIAS = 21
DIAS_UTILES_MINIMOS = 10

VERSIONADOS = ("datos/pista_b/_fetch_report.json", "datos/pista_b/_sondas.json")


def git(*argumentos):
    return subprocess.run(
        ["git", *argumentos],
        cwd=gate_util.RAIZ,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )


def verificar():
    sys.path.insert(0, ruta("ingesta"))
    import sniim

    detalles = []
    relativa = "datos/pista_b/precios.db"

    # 1. Ignorada y fuera del indice.
    ignorada = git("check-ignore", relativa)
    exigir(
        ignorada.returncode == 0,
        f"{relativa} no esta ignorada por git: el repositorio crecera 130 MB al dia",
    )
    indexada = git("ls-files", "--error-unmatch", relativa)
    exigir(
        indexada.returncode != 0,
        f"{relativa} sigue en el indice de git. Un .gitignore no saca del indice un"
        " archivo que ya estaba versionado: hace falta git rm --cached",
    )
    detalles.append(f"{relativa} ignorada y fuera del indice de git")

    # 2 y 3. El flujo de ingesta.
    with open(ruta(".github", "workflows", "ingesta-diaria.yml"), encoding="utf-8") as mano:
        flujo = mano.read()
    linea_add = [linea for linea in flujo.splitlines() if "git add" in linea]
    exigir(linea_add, "el flujo de ingesta no tiene ninguna linea de git add")
    agregado = " ".join(linea_add)
    exigir(
        relativa not in agregado,
        f"el flujo de ingesta sigue comiteando {relativa}: {agregado.strip()}",
    )
    for archivo in VERSIONADOS:
        exigir(
            archivo in agregado,
            f"el flujo de ingesta dejo de comitear {archivo}, que es memoria que no se"
            " puede reconstruir desde la fuente",
        )
        en_indice = git("ls-files", "--error-unmatch", archivo)
        exigir(
            en_indice.returncode == 0,
            f"{archivo} no esta versionado y es memoria que no se reconstruye",
        )
    exigir(
        "actions/cache" in flujo and relativa in flujo,
        "el flujo de ingesta no guarda la base en la cache del corredor: cada corrida"
        " empezaria vacia y bajaria la ventana completa",
    )
    detalles.append(
        "el flujo no comitea la base, la guarda en cache, y sigue versionando el reporte"
        " de fetch y el registro de sondas"
    )

    # 5. El flujo de publicacion se niega a publicar en vacio.
    with open(ruta(".github", "workflows", "publicar-pagina.yml"), encoding="utf-8") as mano:
        publicacion = mano.read()
    exigir(
        "actions/cache" in publicacion,
        "el flujo de publicacion no recupera la base de la cache: construiria en vacio",
    )
    exigir(
        "la pagina anterior sigue en vivo" in publicacion,
        "el flujo de publicacion no dice que al fallar deja publicada la pagina anterior",
    )
    exigir(
        "ingesta/sniim.py" not in publicacion,
        "el flujo de publicacion ingiere: seria a la vez publicador y medidor, y la"
        " separacion que protege el gate B10 dejaria de ser legible",
    )
    detalles.append("el flujo de publicacion recupera la cache y se niega a publicar en vacio")

    # 4. Reconstruccion real desde la fuente, en una base vacia.
    carpeta = tempfile.mkdtemp(prefix="gate_reconstruible_")
    base = os.path.join(carpeta, "vacia.db")
    reporte = os.path.join(carpeta, "reporte.json")
    exigir(not os.path.exists(base), "la base de la prueba no estaba vacia")

    hasta = date.today()
    codigo = sniim.correr(hasta - timedelta(days=DIAS), hasta, [PLAZA], base, reporte)
    exigir(codigo == 0, "la reconstruccion desde la fuente fallo")

    import sqlite3

    conexion = sqlite3.connect(base)
    dias, filas = conexion.execute(
        "SELECT COUNT(DISTINCT fecha_dato), COUNT(*) FROM precios"
    ).fetchone()
    conexion.close()
    exigir(
        dias >= DIAS_UTILES_MINIMOS,
        f"una base vacia se relleno con solo {dias} dias publicados en {DIAS} de ventana:"
        f" por debajo de {DIAS_UTILES_MINIMOS} la vista historica no tendria de donde"
        " dibujarse y perder la cache seria perder el producto",
    )
    detalles.append(
        f"base vacia reconstruida desde la fuente: {filas} filas en {dias} dias publicados"
        f" con una sola peticion"
    )
    return detalles


if __name__ == "__main__":
    sys.exit(gate_util.correr(verificar, MARCADOR))
