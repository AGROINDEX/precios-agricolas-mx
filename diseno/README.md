# Propuestas de diseno

Tres maquetas vivas de la misma pagina, dibujadas sobre la base real de la
pista B. Ningun numero esta escrito a mano: si la base cambia, la maqueta
cambia. Una maqueta con datos de relleno miente sobre lo dificil, que es
cuantos productos hay, que tan largos son los nombres y cuantos valores faltan.

```
python diseno/propuesta_a_terminal.py
python diseno/propuesta_b_mercado.py
python diseno/propuesta_c_brecha.py
```

Cada script escribe su `.html` al lado. Las capturas de las tres estan en
`diseno/capturas/`, junto a la pagina que hoy esta publicada.

| Archivo | Referencia | Para quien |
| --- | --- | --- |
| `propuesta_a_terminal.py` | vista profesional de exchange, terminal oscura | comprador que mira muchas plazas al dia |
| `propuesta_b_mercado.py` | vista de consumidor de exchange, tarjetas claras | productor o comprador chico, en el telefono |
| `propuesta_c_brecha.py` | vista de arbitraje entre exchanges | quien decide a donde mandar la fruta |

## El historico en lugar de la mediana

Las tres propuestas dibujan el historico publicado de cada producto y ninguna
muestra ya la mediana movil de 7 dias. La grafica es una linea del precio
frecuente de cada dia publicado, con la dispersion del mismo dia en gris
detras. El eje son dias publicados y no dias de calendario: un domingo sin
publicacion no deja hueco ni se rellena con el valor del viernes.

Para que hubiera historico que dibujar se relleno la ventana declarada desde la
fuente: 90 dias de calendario, que en las dos plazas del SNIIM son 62 dias
publicados. La misma grafica esta en la pagina publicada.

## Lo que se toma del diseno de exchange y lo que no

Se toma la densidad, la jerarquia del numero sobre el adorno, la variacion a
color, la cinta de movimientos y la comparacion entre dos plazas.

No se toman las velas. Un exchange las dibuja porque tiene apertura, cierre,
maximo intradia y volumen. Aqui existe un valor por dia publicado, asi que una
vela seria inventar cuatro numeros donde hay uno. La linea del historico es ese
valor unico unido en el tiempo, y se dice asi en la pagina.

Tampoco se toma la promesa implicita del exchange, que es "este es el precio al
que usted opera". Esto es mayoreo en plaza de destino, no precio en finca, y
cada propuesta lo dice arriba y no en una nota al pie.

## Dos trampas que las maquetas dejaron ver

La propuesta C comparaba de inicio 53 productos entre Morelia e Iztapalapa.
Eran 53 porque bastaba con que las dos filas declararan base kilogramo, y el
SNIIM declara base kilogramo incluso cuando la presentacion es una pieza o un
rollo de 25 piezas. Pina por pieza contra pina por kilogramo da una brecha
inventada. Exigiendo la misma presentacion en las dos plazas quedan 17
comparables, y la pagina dice cuantos quedaron fuera y por que.

La misma plaza publica a veces dos cotizaciones del mismo producto y la misma
presentacion con precios distintos, sin un campo que diga cual es cual. Esas
claves se marcan ambiguas y no se comparan.

## Una decision de encuadre que queda abierta

Morelia no es precio en finca ni es exactamente origen: es una central de
abasto que esta en una region productora. Llamarla "plaza de origen" en la
interfaz seria comodo y seria falso, asi que en la propuesta C aparece como
"plaza en region productora" frente a "plaza de consumo".
