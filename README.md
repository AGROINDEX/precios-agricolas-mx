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

El vigilante diario avisa cuando una plaza DEJA de moverse, no mientras sigue
quieta: una plaza quieta conocida queda como nota y solo la transicion pone la
corrida en rojo. Para saber como estaba antes no guarda estado, vuelve a medir
recortando la base al dia publicado anterior, asi que el aviso de cualquier dia
se puede recalcular.

```powershell
python ingesta/check_plazas_quietas.py
```

**Cadencia MEDIDA por plaza, no escrita a mano.** Son 42 plazas: 38 publican
cada dia habil, Cuernavaca publica los lunes y Colima y Oaxaca publican martes
y viernes. El silencio de una
plaza solo se puede juzgar contra su propia cadencia: con el umbral diario, la
plaza semanal se declararia muerta cada martes, y con el umbral semanal una
plaza diaria podria estar tres dias caida sin que nadie avisara. Con 41 plazas, teclear eso a mano es una invitacion al error, y una cadencia
mal declarada es peor que ninguna, asi que se mide: `ingesta/medir_cadencia.py`
consulta el catalogo real, mide las 49 plazas del desplegable y genera
`ingesta/cadencias.py`. Una plaza cuya cadencia no se entiende queda SIN
declarar, con su motivo escrito, en vez de recibir una inventada. Y hay un
vigilante POR PLAZA,
porque el de fuentes congeladas mide la fuente entera: mientras Iztapalapa
publique, el SNIIM se ve sano aunque una plaza lleve un ano muerta. Asi se
murio la Central de Abasto de Cuautla, el 31 de octubre de 2025, sin que nadie
lo notara.

**Los festivos se leen de la fuente, no de un calendario.** Un dia en que
NINGUNA plaza publico es un dia en que la fuente no publico, y entonces no es
cita de nadie. Sin esto, el vigilante daba por faltante a la plaza que publica
los lunes cuando ese lunes era festivo nacional. Un calendario habria que
mantenerlo a mano y se desactualiza; el silencio de 42 plazas a la vez no.

```powershell
python ingesta/check_cadencia.py
```

A la plaza semanal se le pregunta igual todos los dias, aunque seis de cada
siete devuelvan vacio. Dejar de preguntar ahorraria peticiones y costaria lo
unico que importa: enterarse el dia en que cambie de cadencia. Lo que cambia no
es la consulta, es como se juzga el silencio.

**La ingesta pide rangos, no dias.** Llenar la ventana con una peticion por dia
serian 3,780 peticiones; por rango son 42, una por plaza. Y leer por rango
obliga a leer la fecha de cada fila en vez de asumir la del dia pedido, asi que
una publicacion tardia llega con su fecha correcta.

**La base no se versiona.** Con 42 plazas pesa 130 MB y comitearla cada dia
haria crecer el repositorio eso diario. Como cada corrida reconstruye la ventana
desde la fuente, la base es cache reconstruible y vive en la cache del corredor
de CI. Lo que si se versiona es la memoria que no se puede reconstruir, el
reporte de fetch y el registro de sondas, que pesan kilobytes. Si la cache
falta, el flujo de publicacion falla y no publica, asi que la ultima pagina
buena sigue en vivo.

**Una pagina por plaza, y un indice.** 42 plazas por sesenta cotizaciones por
una grafica cada una serian miles de SVG en una sola pagina. El indice lleva una
fila por plaza, pesa 19 KiB y dice de un golpe quien publico hoy; el detalle con
graficas vive en la pagina de cada plaza.

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

## Historico publicado

Cada producto muestra su serie de precios de los dias publicados dentro de la
ventana declarada, con la dispersion del dia detras. No hay mediana movil en la
vista: el calculo derivado se conserva en la base, que es lo que sostiene el
gate del articulo 108, pero la columna que el usuario mira es la serie cruda.

La ventana se relleno desde la fuente con `python ingesta/sniim.py --dias 90`,
que es lo mismo que hace la ingesta diaria pero hacia atras y nunca mas alla de
la ventana declarada en `ingesta/comun.py`.
