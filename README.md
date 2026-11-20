# Precios agricolas de Mexico · referencia de precio en origen

Plataforma de precios para productores, comerciantes y compradores del sector
agroalimentario mexicano. El dato oficial de mayoreo es la espina dorsal y el
contraste; el producto que se esta construyendo es la **referencia de precio en
origen**, que ninguna fuente publica cubre.

**En vivo:** https://agroindex.github.io/precios-agricolas-mx/

Nombre y dominio definitivos pendientes. El hosting en GitHub Pages es
provisional por la misma razon: cuando se compre el dominio, la publicacion se
mueve a Cloudflare Pages sin tocar la ingesta ni el generador. Este repositorio
se renombra cuando se decida la marca.

## Como esta armado

```
ingesta/     fetchers incrementales, indicadores propios y vigilante de frescura
esquema/     esquema normalizado, portable de SQLite a Postgres
web/         pagina estatica de precios de hoy, generada desde la base
boletin/     boletin diario del piloto y su runbook
licencias/   una ficha por fuente, con veredicto de semaforo y cita legal
competencia/ desmontaje de los competidores
tools/       verificadores de los gates
datos/       base, reporte de fetch y registros del piloto
```

Corre con Python 3.12 y solo biblioteca estandar. No hay nada que instalar.

```powershell
python ingesta/sniim.py; python ingesta/ficeda.py; python ingesta/derivados.py; python web/construir.py
```

## Las reglas que condicionan el diseno

**Ingesta incremental, nunca espejo del acervo.** El articulo 108 de la Ley
Federal del Derecho de Autor protege las bases de datos no originales en uso
exclusivo de quien las elaboro durante cinco anos. El dato puntual es libre por
los articulos 14 fraccion X y 107; el acervo no. Por eso la base guarda una
ventana declarada de noventa dias por fuente, poda en cada corrida y publica
indicadores calculados por nosotros.

**Licencia verificada por fuente antes de integrar**, con la cita del texto que
la respalda. Las fichas estan en `licencias/`. Hoy las dos fuentes estan en
amarillo: usables con atribucion visible, pendientes de autorizacion expresa
para monetizar el acervo. Las consultas escritas estan en `correspondencia/`.

**Frescura real, no solo la declarada.** La fecha de un corte la pone la
fuente, y una fuente puede republicar el mismo numero con la fecha de hoy. Cada
plaza lleva en la pagina su veredicto de movimiento, calculado sobre cuantos
productos cambiaron de precio contra el dia publicado anterior y cuantos dias
lleva cada valor sin moverse. Hoy Iztapalapa se mueve y Morelia casi no: 70 por
ciento de sus productos no cambio ni una vez en la ventana y la mitad de sus
precios lleva catorce dias o mas quieto, aunque su corte diga que es de hoy.

```powershell
python ingesta/frescura_real.py
```

**Frescura declarada siempre.** Cada precio lleva su fecha y su fuente. Si una
fuente se congela, la pagina lo dice en la cara del usuario en vez de mostrar el
ultimo dato bueno como si fuera de hoy. El vigilante corre en su propio flujo de
CI y prueba su propio control positivo antes de medir en vivo.

**No se promete precio en finca cuando el dato es de mayoreo.** Es lo que se
paga en la plaza de destino, no lo que recibe quien cosecha.

**Nada de cuentas falsas, scraping con sesion iniciada ni grupos cerrados.**

## Fuentes

| Fuente | Que da | Licencia | Atribucion |
|---|---|---|---|
| SNIIM, Secretaria de Economia | Mayoreo diario de frutas y hortalizas por producto, calidad, presentacion, origen y plaza | Amarillo, sin terminos propios de reutilizacion | Fuente: SNIIM, Secretaria de Economia (economia-sniim.gob.mx) |
| Central de Abasto de la CDMX, FICEDA | Mayoreo diario con corte propio por fila | Amarillo, sin aviso legal localizado | Fuente: Central de Abasto de la Ciudad de Mexico, FICEDA |

Los precios del SNIIM se consultan por kilogramo calculado y los de la FICEDA
por presentacion comercial. La base lo declara fila por fila en `base_precio` y
la pagina lo dice en cada bloque: sin eso, 34.44 y 310.00 del mismo aguacate
parecen precios distintos.

## Gates

El trabajo se acepta contra un ledger, no contra un reporte de avance.

```powershell
node $env:USERPROFILE\.claude\skills\unlazy\scripts\gate-check.mjs --status --root . GATES_pista_A.md GATES_pista_B.md GATES_raiz.md
```

Los registros del piloto con datos personales no se versionan, por eso
`datos/pista_a/` solo trae su README con el formato.
