# Decisiones del fundador · bitácora

## Resueltas

**20 de noviembre de 2026 · Marca y dominio aparte** de agropatent.com, con
infraestructura compartida. El comprador corporativo de inteligencia de
propiedad intelectual y el usuario del tablero de precios se estorban en el
mismo sitio, pero el dato y la maquinaria sí se comparten. Elegir el nombre y
comprar el dominio entra a la ruta crítica, porque condiciona el despliegue, el
correo y la cuenta de cobro.

**20 de noviembre de 2026 · Paga el comprador, no el productor.** De ahí sale
un modelo de dos lados que resuelve a la vez el problema del dato y el del
ingreso:

- Lado vendedor, no paga y es la fuente: productores y comerciantes consultan
  gratis y a cambio publican su propio precio en origen, que es justo lo que
  ninguna fuente oficial cubre y lo que separa esto de los dos competidores
  mexicanos que ya existen.
- Lado comprador, paga por el agregado: mayoristas, exportadores, cadenas,
  servicio de alimentos y agroindustria compran saber dónde está el producto, a
  qué precio, en qué volumen y con qué calidad.
- Marcas de insumos patrocinan para alcanzar al lado vendedor, que además es el
  comprador de la fase 2.

Lo que esta decisión manda sobre el ledger: el piloto de la pista A mide **dos
lados con dos métricas distintas**, oferta de dato del lado vendedor y
disposición a pagar del lado comprador, en dos conversaciones separadas y con
dos cohortes separadas.

Lo que manda sobre el discurso: no se cuenta como "salvamos al productor del
coyote", porque se le cobra al lado que captura el margen. Se cuenta como
inteligencia de origen para quien compra, con el acceso gratuito del productor
como la contraparte honesta del trato. Misma disciplina de declarar el límite
que hizo creíble el deck anterior.

Lo que manda sobre la fase 3: cuando se abra el marketplace, los dos lados ya
están dentro y ya se conocen.

## La mediana móvil sale de la vista, el histórico entra

Decidida el 20 de noviembre de 2026, a petición del fundador: la mediana de 7
días no le sirve, lo que sirve es ver el histórico.

La mediana se **quita** de la vista en vez de dejarla al lado. Una columna que
nadie usa ocupa el lugar de la que sí, y en una tabla de once columnas ese
lugar es caro. El cálculo derivado **se conserva en la base**: es lo que
sostiene el gate B5 del artículo 108, donde la defensa es que publicamos
indicadores propios y no un espejo del acervo.

Para que la gráfica tuviera de dónde dibujarse se rellenó la ventana declarada
desde la fuente, 90 días de calendario que son 62 días publicados por plaza. No
es ampliar la ventana: es llenar la que ya estaba declarada, y la poda sigue
cortando todo lo que la rebase.

Lo que esta decisión manda sobre el ledger: gates B15, profundidad de la
ventana, y B16, la gráfica es la serie recalculada desde las filas crudas y no
un adorno.

## Abiertas

| Decisión | Por qué importa | Dueño |
|---|---|---|
| Repositorio nuevo o carpeta dentro del actual | Afecta al CI y al tamaño del despliegue, que ya está cerca del límite | fundador |
| Qué es Mormex | Seis búsquedas con variantes no encontraron la entidad. Hace falta la escritura exacta, el canal donde publica y qué producto o plaza cubre | fundador, preguntando al contacto |
| Arrancar solo con fuentes verdes o esperar la autorización escrita del SNIIM | Mi recomendación es arrancar con las verdes y mandar la consulta el primer día, porque la respuesta tarda y el expediente vale | fundador |
| Nombre y dominio concretos | Ruta crítica del despliegue, el correo y la cuenta de cobro | fundador |

## La plaza semanal entra al piloto, y la cadencia se declara

20 de noviembre de 2026.

El Mercado Adolfo Lopez Mateos de Cuernavaca entra al piloto como tercera plaza
del SNIIM, con 626 filas en 11 publicaciones dentro de la ventana declarada.

**Como se encontro, y el error que lo escondia.** Se habia concluido que las dos
plazas de Morelos del SNIIM publican cero. Era falso. La sonda preguntaba por
dias sueltos, y esta plaza publica solo los lunes: un dia suelto cae en lunes
una vez cada siete, asi que la plaza se veia muerta seis de cada siete veces que
se la miraba. La Central de Abasto de Cuautla, DestinoId 170, si publica cero:
su ultimo dia con dato es el 16 de octubre de 2025 y quedo fuera de la ventana.

**Por que no basta con agregarla.** Nada en el sistema se habria enterado si
esta plaza se muriera. El vigilante de fuentes congeladas mide por FUENTE, y el
SNIIM seguiria bajando todos los dias gracias a Iztapalapa. Es exactamente como
murio Cuautla sin que nadie lo notara. Por eso la plaza no entra sola: entra con
una tabla de cadencias declaradas y un vigilante por plaza que juzga el silencio
de cada una contra su propia cita.

**Por que se le sigue preguntando los dias que no le toca.** Consultarla solo
los lunes ahorraria seis peticiones de siete. Tambien garantizaria no enterarse
nunca de que cambio de cadencia, que es la forma mas probable en que esta plaza
se va a romper. Se consulta igual todos los dias; lo que depende de la cadencia
no es la consulta, es como se juzga el silencio.

**Por que la antiguedad del precio se cuenta en publicaciones.** La edad del
valor se media en dias de calendario. En una plaza semanal, un precio que
cambio en la ultima publicacion tiene siete dias de edad, y decir "la mitad de
los precios lleva siete dias sin moverse" describiria como estancada a una plaza
que esta al dia. Para la plaza semanal se cuenta en publicaciones y para las
diarias se sigue contando en dias, con un control que lo comprueba en los dos
sentidos.

**Lo que la plaza resulto ser, que no era lo esperado.** Se integro esperando
algo parecido a un precio de origen, por estar en un estado productor. Sale
28.6 por ciento MAS CARA que Iztapalapa, en 11 de 11 semanas. Es un mercado de
consumo local, el eslabon de despues de Iztapalapa y no el de antes. Es la
segunda vez que la geografia no sirve de sustituto del origen, despues de
Morelia. Se queda en el piloto igual, porque es la plaza que mas se mueve de las
cuatro: 87 por ciento de sus productos cambio de precio en su ultimo corte,
contra 0 por ciento en Morelia.

**Lo que esta plaza trae de regalo y de advertencia.** Falto a 2 de sus ultimos
3 lunes, incluido el 16 de noviembre. El vigilante nuevo nace en rojo por eso, y
esta bien que nazca en rojo: es la pieza funcionando. Si sigue faltando, esta
plaza va por el mismo camino que Cuautla, y ahora si nos vamos a enterar.

## Cuautla queda en vigilancia de reaparicion, no en el piloto normal

20 de noviembre de 2026.

**Lo que la medicion corrigio.** Se habia dicho que Cuautla publicaba poco y que
su ultimo dia con dato era el 16 de octubre de 2025. Las dos cosas estaban mal,
y por el mismo motivo de siempre: se habia sondeado dias sueltos en vez de un
rango. Con el rango completo, Cuautla era una plaza DIARIA y sana, 98 dias
publicados en cinco meses, de lunes a viernes sin faltar, 5,702 filas, y murio
de golpe el 31 de octubre de 2025. De noviembre de 2025 a marzo de 2026: cero.

**Por que no entra al piloto normal.** Porque no tiene ni una fila, y todo lo
que este producto mide por plaza recorre las filas de `precios`. Una plaza
muerta es invisible para la frescura, para la cadencia y para la pagina. Meterla
al piloto normal y ya habria sido ponerle un asiento vacio en la mesa.

**Lo que se guarda es el intento, no la fila.** La vigilancia escribe en
`_sondas.json` cuantas veces se le pregunto, cuando fue el ultimo intento y
cuantos intentos seguidos devolvieron cero. Es la misma leccion del vigilante de
fuentes congeladas, que mide dias desde el ultimo fetch BUENO y no la antiguedad
del archivo: lo que hay que registrar es la prueba de que se pregunto.

**El vigilante nuevo interrumpe con una buena noticia.** Sale en rojo el dia en
que Cuautla vuelva a traer filas, y el mensaje aclara con todas sus letras que
no es una falla sino una reaparicion, y que lo que toca es promoverla al piloto,
medir su cadencia nueva y rellenar su ventana. Rojo en CI es lo unico que GitHub
notifica, y el flujo del vigilante no despliega, asi que fallar ahi no deja el
tablero sin actualizar. Mientras siga muerta se reporta como nota, no como
fallo, que es la regla de la casa: interrumpe la transicion, no el estado.

**Tres controles, porque dos no bastaban.** El positivo simula la reaparicion y
exige rojo. El negativo simula el silencio continuo y exige verde, porque sin el
un vigilante que gritara siempre pasaria el positivo. Y el tercero cubre el caso
que los separa: una plaza cuyo PRIMER intento ya trae filas no es una
reaparicion, porque nunca se la conocio muerta. Sin ese control, el aviso
saldria cada vez que se agrega cualquier plaza nueva.

## Las 41 plazas entran, y fuerzan cuatro cambios de arquitectura

21 de noviembre de 2026.

El piloto pasa de 3 plazas del SNIIM a 41, mas el visor de la Central de Abasto:
42 plazas, 133,946 filas en la ventana de 90 dias. Antes se usaba el 8 por
ciento de lo que la fuente publica.

Agregar plazas era de dos lineas. Lo que costo, y lo que valio, es lo que las 41
dejaron ver.

### La cadencia se genera midiendo, no se escribe a mano

Con tres plazas, teclear la cadencia era razonable. Con 41 es una invitacion al
error, y una cadencia declarada mal es PEOR que ninguna: el vigilante juzga el
silencio contra una cita equivocada y da por muerta una plaza viva. Ahora
`ingesta/medir_cadencia.py` consulta el catalogo real del formulario, mide las
49 plazas con una peticion de rango cada una, clasifica y escribe
`ingesta/cadencias.py`, que es archivo generado y lo dice en su cabecera.

El censo: **38 diarias, 3 no diarias, 8 muertas**. Las no diarias son Cuernavaca
los lunes, y Colima y Oaxaca los martes y viernes. Esas dos ultimas no estaban
en el radar de nadie: habrian aparecido como muertas cinco dias de cada siete.

Y la clasificacion se niega a adivinar. Una plaza que no encaja en diaria ni en
semanal con regularidad del 60 por ciento queda **sin declarar**, con su motivo
escrito, en vez de recibir una cadencia inventada.

### Los festivos se leen de la fuente, no de un calendario

Este es el hallazgo que corrige un error propio. El vigilante decia que el
Mercado de Cuernavaca habia faltado a 2 de sus ultimas 3 citas, y de ahi se
escribio que iba por el camino de Cuautla. Era falso.

Con las 41 plazas quedo a la vista que **Iztapalapa tampoco publico el 2 ni el
16 de noviembre**, ni el 16 de septiembre: son los tres unicos dias habiles que
falta en 90 dias, y son los tres festivos nacionales. Los dos lunes que
Cuernavaca "falto" eran dias en que el SNIIM entero estaba cerrado. La plaza
cumplio 11 de 11.

La correccion no necesita un calendario de festivos, que habria que mantener a
mano y se desactualiza. Un dia en que NINGUNA plaza de la fuente publico es un
dia en que la fuente no publico, y entonces no es cita de nadie. **La fuente
declara sus propios festivos con su silencio.** Con dos plazas esa señal no se
podia afirmar; con 41 es inequivoca. Es la primera vez que agregar dato mejora
una medida en vez de solo aumentarla.

### La ingesta pide rangos, no dias

Llenar la ventana con una peticion por dia serian 90 por 42, o sea 3,780
peticiones. Por rango son 42. El endpoint acepta `fechaInicio` distinto de
`fechaFinal` desde siempre y no lo estabamos usando.

Y leer por rango obliga a leer la fecha de CADA FILA en vez de asumir la del dia
pedido, que es mejor por si solo: si la fuente publica tarde, la fila llega con
su fecha correcta en vez de con la de hoy. Esa suposicion llevaba ahi desde el
primer dia y nadie la habia tocado.

La corrida normal pide los ultimos 10 dias; si la base viene vacia o atrasada,
pide la ventana completa sola. Eso lo decide `dias_a_pedir`, mirando la base.

### La base sale de git

Con 42 plazas la base pesa **130 MB**, y el flujo diario la comiteaba entera: el
repositorio habria crecido eso cada dia. La salida no es comprimir ni podar mas,
es que la base **deje de ser memoria**. Si cada corrida reconstruye la ventana
con una peticion de rango por plaza, la base es cache reconstruible y no hay
nada que versionar. Vive en la cache del corredor de CI, que es exactamente para
lo que la cache existe.

Lo que si se sigue versionando es la memoria que NO se puede reconstruir, y pesa
kilobytes: `_fetch_report.json`, que sabe cuando fue la ultima descarga buena, y
`_sondas.json`, que sabe cuantas veces se le pregunto a una plaza muerta.

La resiliencia no se pierde. Si la cache falta, el flujo de publicacion **falla y
no publica**, asi que la ultima pagina buena sigue en vivo y la siguiente
ingesta repuebla la cache. Antes se habria publicado una pagina con dato viejo
presentado como de hoy, que es peor. Y el flujo de publicacion NO ingiere a
proposito: si lo hiciera seria a la vez publicador y medidor, y la separacion
que protege el gate B10 dejaria de ser legible.

Queda pendiente declarado, no olvidado: `consulta_url` es el 66 por ciento del
texto de la base, con 42 urls distintas para 133,946 filas. Normalizarla
ahorraria unos 45 MB. Se aplaza porque el motivo que la hacia urgente, comitear
la base cada dia, ya no existe.

### Una pagina por plaza, y un indice

42 plazas por unas sesenta cotizaciones por una grafica cada una son del orden de
2,500 SVG en linea: varios megabytes en una sola pagina, que en una conexion de
campo no se abre. Ahora el indice lleva una fila por plaza con su corte, su
cadencia y su veredicto de movimiento, y el detalle con graficas vive en la
pagina de cada plaza.

El indice pesa **19 KiB**, 4 comprimido, y la plaza mas pesada 242 KiB, contra un
presupuesto declarado de 700. Y el indice resulto ser lo que de verdad hacia
falta: ver de un golpe quien publico hoy y quien no.

### Dos bugs que la escala destapo

**`prop_planos` mentia.** El calculo de cuantos productos nunca cambiaron de
precio excluia a los que no aparecian en el ultimo corte, contra su propia
definicion escrita. Con dos plazas la diferencia era invisible; con 42, el
recalculo independiente del gate B13 la destapo de inmediato: el modulo decia 2
por ciento y el recalculo 7.

**Un verificador que saltaba en silencio.** La comprobacion de que la pagina
declara la cadencia de cada plaza buscaba el nombre crudo, y los nombres con
comillas van escapados en el HTML. No lo encontraba, y entonces **saltaba esa
plaza**, justo la que importaba. Un verificador que salta lo que no entiende es
decorativo. Ahora no encontrar una plaza es una falla.
