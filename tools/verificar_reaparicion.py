"""B20 · la plaza muerta queda vigilada y su regreso interrumpe.

QUE SE COMPRUEBA

1. La plaza muerta esta en el piloto Y en la lista de vigilancia, asi que se le
   pregunta todos los dias igual que a una viva.
2. El INTENTO queda registrado aunque devuelva cero filas. Es el punto entero
   de esta pieza: una plaza sin filas es invisible para todo lo demas, asi que
   lo unico que prueba que se pregunto es el registro del intento.
3. CONTROL POSITIVO. Se simula la reaparicion y se exige que el vigilante la
   detecte y salga en rojo.
4. CONTROL NEGATIVO. Se simula el silencio continuo y se exige que NO grite.
   Sin este control, un vigilante que gritara siempre pasaria el punto 3.
5. Y el caso que separa a los dos: una plaza cuyo PRIMER intento ya trae filas
   no es una reaparicion, porque nunca se la conocio muerta. Si eso se
   reportara como regreso, el aviso saldria el dia que se agrega cualquier
   plaza nueva.

Uso:
  python tools/verificar_reaparicion.py --control-reaparicion
"""
import argparse
import os
import sys
import tempfile

import gate_util
from gate_util import exigir, ruta

MARCADOR = (
    "vigilancia de reaparicion verificada · reaparicion detectada y silencio continuo tolerado"
)

MUERTA = "Morelos: Central de Abasto de Cuautla"
FIXTURE = ruta("fixtures", "pista_b", "sondas_reaparicion.json")


def verificar(con_control):
    import sniim
    from check_reaparicion import evaluar
    from comun import CADENCIAS, cadencia
    from sondas import anotar, leer

    detalles = []

    # 1. La plaza muerta se consulta como una viva.
    identificadores = [pid for pid, nombre in sniim.PLAZAS.items() if nombre == MUERTA]
    exigir(identificadores, f"{MUERTA} no esta en sniim.PLAZAS")
    plaza_id = identificadores[0]
    exigir(
        plaza_id in sniim.VIGILANCIA,
        f"{MUERTA} no esta en vigilancia: su intento no se registraria y su regreso"
        " pasaria inadvertido",
    )
    exigir(
        plaza_id not in sniim.PILOTO,
        f"{MUERTA} esta en el piloto y no publica nada: seria un asiento vacio en la mesa",
    )
    # Lo que importa no es en que lista esta, sino que la ingesta le pregunte
    # en una corrida normal, sin que nadie se acuerde de pedirlo.
    exigir(
        plaza_id in sniim.plazas_por_defecto(),
        f"una corrida normal de la ingesta no le pregunta a {MUERTA}: su regreso"
        " pasaria inadvertido otro ano",
    )
    exigir(
        MUERTA in CADENCIAS,
        f"{MUERTA} no declara la cadencia que tenia, que es contra la que habria que"
        " juzgarla el dia en que vuelva",
    )
    detalles.append(
        f"plaza {plaza_id} en el piloto y en vigilancia, con cadencia declarada"
        f" {cadencia(MUERTA)['cadencia']}"
    )

    # 2. El intento con cero filas queda registrado, en el registro real.
    vivo = leer()
    llave = f"SNIIM_FYH:{plaza_id}"
    exigir(
        llave in vivo.get("plazas", {}),
        f"no hay ningun intento registrado para {MUERTA} en el registro de sondas",
    )
    registro = vivo["plazas"][llave]
    exigir(
        registro["intentos"] >= 1,
        f"{MUERTA} aparece en el registro con {registro['intentos']} intentos",
    )
    exigir(
        registro["intentos_sin_filas"] >= 1 and registro["filas_ultimo_intento"] == 0,
        f"{MUERTA} figura como que trae filas y la medicion dice que publica cero:"
        f" {registro}",
    )
    detalles.append(
        f"{registro['intentos']} intentos registrados, {registro['intentos_sin_filas']}"
        " seguidos sin filas, con el ultimo intento sellado"
    )

    if con_control:
        carpeta = tempfile.mkdtemp(prefix="gate_reaparicion_")
        archivo = os.path.join(carpeta, "sondas.json")

        # Silencio continuo: tres intentos vacios seguidos.
        for paso in range(3):
            _r, reaparecio = anotar(
                "SNIIM_FYH", plaza_id, MUERTA, 0, archivo, momento=f"2026-11-2{paso}T13:00:00+00:00"
            )
            exigir(
                not reaparecio,
                f"el intento vacio numero {paso + 1} se reporto como reaparicion",
            )
        _reaparecidas, muertas, _sin = evaluar(leer(archivo))
        exigir(
            MUERTA in {r["nombre"] for r in muertas},
            "la plaza con tres intentos vacios no quedo clasificada como muerta",
        )

        # Reaparicion: el cuarto intento trae filas.
        _r, reaparecio = anotar(
            "SNIIM_FYH", plaza_id, MUERTA, 57, archivo, momento="2026-11-24T13:00:00+00:00"
        )
        exigir(reaparecio, "el intento con 57 filas despues de tres vacios no se detecto")
        reaparecidas, muertas, _sin = evaluar(leer(archivo))
        exigir(
            MUERTA in {r["nombre"] for r in reaparecidas},
            "la plaza que volvio a traer filas no quedo clasificada como reaparecida",
        )

        # Plaza nueva cuyo primer intento ya trae filas: NO es una reaparicion.
        nuevo = os.path.join(carpeta, "sondas_nueva.json")
        _r, reaparecio = anotar(
            "SNIIM_FYH", "140", "Plaza nueva que si publica", 80, nuevo,
            momento="2026-11-24T13:00:00+00:00",
        )
        exigir(
            not reaparecio,
            "una plaza cuyo primer intento ya trae filas se reporto como reaparicion:"
            " el aviso saldria cada vez que se agrega una plaza",
        )
        detalles.append(
            "control: 3 intentos vacios sin aviso, el cuarto con filas detectado como"
            " reaparicion, y plaza nueva con filas no confundida con un regreso"
        )

        # El vigilante completo, por su codigo de salida, contra el fixture.
        import subprocess

        exigir(os.path.exists(FIXTURE), f"falta el fixture de control en {FIXTURE}")
        corrida = subprocess.run(
            [sys.executable, ruta("ingesta", "check_reaparicion.py"), "--sondas", FIXTURE],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        exigir(
            corrida.returncode == 1,
            f"el vigilante no salio en rojo con el fixture de reaparicion:"
            f" codigo {corrida.returncode}",
        )
        exigir(
            "REAPARECIO" in corrida.stdout,
            f"el vigilante no dijo que la plaza reaparecio: {corrida.stdout[:300]}",
        )
        exigir(
            "NO es una falla" in corrida.stdout,
            "el aviso de reaparicion no aclara que no es una falla, y rojo en CI se lee"
            " como falla",
        )
        exigir(
            "sigue muerta" in corrida.stdout,
            "el vigilante no reporto como nota a la plaza de control que sigue muerta",
        )
        corrida_viva = subprocess.run(
            [sys.executable, ruta("ingesta", "check_reaparicion.py")],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        exigir(
            corrida_viva.returncode == 0,
            f"el vigilante salio en rojo con el registro real, donde nada reaparecio:"
            f" {corrida_viva.stdout[:300]}",
        )
        detalles.append(
            "control por codigo de salida: rojo con el fixture de reaparicion, verde con"
            " el registro real"
        )

    return detalles


if __name__ == "__main__":
    lector = argparse.ArgumentParser(description="Verifica la vigilancia de reaparicion")
    lector.add_argument("--control-reaparicion", action="store_true")
    argumentos = lector.parse_args()
    sys.exit(gate_util.correr(lambda: verificar(argumentos.control_reaparicion), MARCADOR))
