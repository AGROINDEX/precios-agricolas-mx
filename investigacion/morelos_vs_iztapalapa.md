# Morelos contra Iztapalapa, 90 dias de ventana declarada

Medido el 20 de noviembre de 2026. La pregunta era comparar Mor-Mex contra el
SNIIM en 90 dias distintos. No se pudo hacer, y lo que si se pudo medir cambia
dos cosas que este repositorio daba por ciertas.

## Lo que no existe

**No hay precio de Mor-Mex.** No lo publica el SNIIM, no lo publica Morelos, no
aparece en ningun lado consultable. Sin una sola observacion no hay un dia que
comparar, menos noventa. El unico camino es levantarlo en campo.

**No hay 90 dias en el lado del SNIIM tampoco.** La Central de Abasto de
Cuautla, DestinoId 170, publica **cero filas** en toda la ventana. Su ultimo dia
con dato es el 16 de octubre de 2025, fuera de la ventana declarada.

## Dos errores propios, corregidos

**Uno.** Se habia concluido que las plazas de Morelos del SNIIM publican cero.
Es falso para Cuernavaca: el Mercado "Adolfo Lopez Mateos", DestinoId 172,
publica **todos los lunes**. Las sondas anteriores fallaron porque preguntaban
por dias sueltos, y un dia suelto cae en lunes una vez cada siete. Una plaza
semanal se declara muerta si se la sondea a diario sin mirar el dia de la
semana.

**Dos.** Comparar exigiendo la MISMA presentacion, que fue el arreglo correcto
para Morelia, aqui tiraba 40 de 56 comparaciones validas. Iztapalapa cotiza el
aguacate en "Caja de 9 kg." y Cuernavaca en "Kilogramo", pero con
`PreciosPorId=2` **la fuente ya entrego las dos en pesos por kilogramo
calculado**. La regla defendible es por unidad y no por cadena de texto:

- las dos presentaciones basadas en peso, se compara
- las dos la misma unidad por pieza, se compara
- una por peso contra una por pieza, se descarta y se cuenta

Lo tercero es lo que evita la trampa de la pina por pieza contra pina por kilo,
porque ahi la fuente no pudo dividir. Son 2 descartes por dia.

## La tabla

Cuernavaca ALM contra Iztapalapa, un renglon por dia publicado. La brecha es
positiva cuando Morelos esta mas caro.

| fecha | dia | filas Morelos | comparables | descartadas por unidad | brecha mediana | min | max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-08-24 | lunes | 58 | 41 | 2 | +19.0% | -41.8% | +233.3% |
| 2026-08-31 | lunes | 57 | 40 | 2 | +27.9% | -46.7% | +300.0% |
| 2026-09-07 | lunes | 57 | 40 | 2 | +49.2% | -60.0% | +185.7% |
| 2026-09-14 | lunes | 57 | 41 | 2 | +25.0% | -39.3% | +257.1% |
| 2026-09-21 | lunes | 57 | 41 | 2 | +28.6% | -39.7% | +284.6% |
| 2026-09-28 | lunes | 56 | 39 | 2 | +35.7% | -40.0% | +221.4% |
| 2026-10-05 | lunes | 57 | 41 | 2 | +38.9% | -40.0% | +177.8% |
| 2026-10-12 | lunes | 57 | 41 | 2 | +28.5% | -43.3% | +114.3% |
| 2026-10-19 | lunes | 57 | 41 | 2 | +34.1% | -28.6% | +188.9% |
| 2026-10-26 | lunes | 57 | 41 | 2 | +34.1% | -42.9% | +199.9% |
| 2026-11-09 | lunes | 56 | 40 | 2 | +21.4% | -50.0% | +157.1% |

El 2 de noviembre falta: ese lunes la fuente no publico. Tampoco publico el 16
de noviembre, que es el lunes siguiente al ultimo renglon de la tabla. Dicho
completo: la plaza cumplio 11 de sus 13 citas, y falto a 2 de las ultimas 3. Si
sigue asi va por el mismo camino que Cuautla.

Mediana de las 11 medianas semanales: **+28.6%**. Semanas con Morelos mas caro:
**11 de 11**.

## Que significa

Una plaza dentro de un estado productor sale **28.6 por ciento mas cara** que la
referencia nacional de mayoreo, sin una sola semana en contra. El signo es lo
que importa: si el dato de Morelos fuera precio de origen tendria que estar por
debajo, porque el flete y el margen no son gratis. Estar arriba de forma
sostenida significa que el Adolfo Lopez Mateos es un mercado de consumo local,
el eslabon de DESPUES de Iztapalapa y no el de antes.

Es el mismo resultado que dio Morelia por otro camino. Dos veces ya, la
geografia no sirve de sustituto del origen: **estar en una region productora no
hace que una plaza cotice como origen**. Nada de lo que publica el SNIIM es
precio de origen, y por eso el hueco sigue siendo el hueco.

## Que se hizo con esto

La plaza entro al piloto el mismo dia, con su cadencia declarada y un vigilante
por plaza que juzga su silencio contra su propio lunes. Las 626 filas estan en
la base, dentro de la ventana. El detalle y el porque estan en `DECISIONES.md`,
seccion "La plaza semanal entra al piloto, y la cadencia se declara".

## Articulo 108

Las 626 filas de Cuernavaca caen dentro de la ventana declarada de 90 dias, asi
que integrarlas seria legitimo bajo la misma regla que ya rige a las otras
plazas. La medicion de esta tabla corrio **en memoria y no escribio en `precios.db`**.
La integracion posterior si escribio, por la via normal de la ingesta y con la
poda de ventana corriendo en cada corrida, que es lo que mantiene la base dentro
de los noventa dias declarados. La tabla de arriba es indicador derivado propio
y no un espejo del acervo.
