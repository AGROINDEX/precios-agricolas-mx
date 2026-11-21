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
