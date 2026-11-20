# Ficha de licencia · SNIIM, Secretaria de Economia

- **Clave en la ingesta:** `SNIIM_FYH`
- **Veredicto:** amarillo
- **Fecha de la verificacion:** 20 de noviembre de 2026
- **Atribucion obligatoria:** Fuente: SNIIM, Secretaria de Economia (economia-sniim.gob.mx)

## Que se integra

Precios de mayoreo de frutas y hortalizas por producto, calidad, presentacion,
origen y plaza de destino, un dia por peticion, mediante GET sin autenticacion a

```
https://www.economia-sniim.gob.mx/Nuevo/Consultas/MercadosNacionales/PreciosDeMercado/Agricolas/ResultadosConsultaFechaFrutasYHortalizas.aspx
```

La ruta sin el segmento `Nuevo/Consultas/` devuelve 404, y es la que traia el
paquete de arranque. Corregido tras verificar en vivo.

## Que dice el texto legal

El sitio no publica terminos propios de reutilizacion. Los terminos generales de
gob.mx indican uso personal y no comercial, asi que **no hay autorizacion
expresa para monetizar el acervo**, y de ahi el amarillo.

Lo que si esta claro es el limite del derecho de base de datos. La Ley Federal
del Derecho de Autor, articulo 108:

> Las bases de datos que no sean originales quedan, sin embargo, protegidas en
> su uso exclusivo por quien las haya elaborado, durante un lapso de 5 anos.

Y el articulo 107 acota el alcance de esa proteccion:

> La proteccion a que se refiere el articulo anterior no se extendera a los
> datos y materiales en si mismos.

El articulo 14 fraccion X deja fuera de la proteccion del derecho de autor a
los hechos y datos en si. De ahi la arquitectura: el dato puntual citado con su
fecha y su fuente es usable, el acervo completo no.

**Correccion a un supuesto previo del proyecto:** el articulo 14 fraccion VIII,
sobre textos legislativos y administrativos, **no** es el gancho correcto para
una tabla de precios. No se vuelve a citar asi.

## Que se respeta en la ingesta

- `robots.txt` del sitio prohibe `/Analisis/`, `*.xls`, `/2010/` y `/Sicia*`.
  Verificado el 20 de noviembre de 2026. La ingesta no toca ninguna de esas
  rutas: solo la pagina de resultados de consulta, que no esta restringida.
- Ventana declarada de 90 dias en la base. Nada de historico desde 1998.
- Indicadores derivados propios, calculados por nosotros, como unico agregado
  publicado.
- Atribucion visible en la pagina y en el boletin.

## Pendiente que bloquea la monetizacion del acervo

Consulta escrita a `info.sniim@economia.gob.mx` pidiendo autorizacion expresa
para uso comercial del dato con atribucion. Texto en
`correspondencia/consulta_sniim.md`. Mientras no haya respuesta, el veredicto
sigue en amarillo y el dato se usa como referencia citada, no como acervo
redistribuido.
