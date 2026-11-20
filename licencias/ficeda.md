# Ficha de licencia · Central de Abasto de la Ciudad de Mexico (FICEDA)

- **Clave en la ingesta:** `FICEDA_CDMX`
- **Veredicto:** amarillo
- **Fecha de la verificacion:** 20 de noviembre de 2026
- **Atribucion obligatoria:** Fuente: Central de Abasto de la Ciudad de Mexico, FICEDA

## Que se integra

Precios de mayoreo por producto, calidad, presentacion y origen, con la fecha
del corte en cada fila, del visor publico

```
http://201.99.114.63:81/central-abasto/visor_mayoreo.php
```

Cuatro tablas renderizadas en servidor: abarrotes, hortalizas, frutas de
temporada y frutas. Verificado en vivo el 20 de noviembre de 2026, con corte
publicado del 19 de noviembre, es decir con un dia de rezago.

## Que dice el texto legal

No se localizo aviso legal ni terminos de reutilizacion en el visor. La propia
FICEDA pide atribucion con formato citado, lo que confirma que la publicacion es
para consulta publica pero **no constituye autorizacion expresa de
redistribucion comercial**. De ahi el amarillo.

Aplica el mismo limite de la Ley Federal del Derecho de Autor, articulo 108:

> Las bases de datos que no sean originales quedan, sin embargo, protegidas en
> su uso exclusivo por quien las haya elaborado, durante un lapso de 5 anos.

Y el articulo 107, que excluye de esa proteccion a los datos en si mismos. Dato
puntual citado, si. Espejo del visor, no.

## Riesgo tecnico que queda anotado

El visor se sirve por HTTP sin cifrado y en un puerto no estandar. La peticion no
lleva ningun dato propio, asi que no hay secreto expuesto, pero la respuesta
viaja en claro: un intermediario podria alterar precios en transito y la ingesta
no tendria forma de notarlo. Mitigacion parcial: el vigilante de frescura detecta
la caida, y la amplitud relativa delata valores imposibles. Mitigacion real:
pedir a la FICEDA un endpoint por HTTPS.

## Pendiente

Peticion escrita de permiso de uso con atribucion, dirigida a la FICEDA. Texto
en `correspondencia/permiso_ficeda.md`. Mientras no haya respuesta, el veredicto
sigue en amarillo.
