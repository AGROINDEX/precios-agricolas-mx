# Que mas se puede ingerir, y que conviene arreglar antes

Medido el 20 y 21 de noviembre de 2026. Tres investigaciones en paralelo, y
cada afirmacion que cambia una decision fue verificada otra vez a mano contra la
fuente. Lo que no se pudo verificar esta marcado como no verificado.

**La respuesta corta a la pregunta estrategica: Mexico NO publica precio de
origen diario.** Existio dos veces y las dos veces lo descontinuaron. Lo que si
hay es precio de origen ANUAL con 7 a 19 meses de rezago, y precio de
exportacion DIARIO del producto mexicano, publicado por Estados Unidos. De ahi
sale el plan.

---

## 1. El SNIIM es doce veces mas grande de lo que estamos usando

### Correccion de un numero que este repositorio traia mal

El desplegable de plazas **no tiene 474 opciones, tiene 50**: 49 plazas reales
mas "Todos". Las 474 salian de contar todos los `<option>` del formulario, que
incluye 223 productos, 36 origenes y tres copias del mismo desplegable de
destino. Contado bien, con un solo `<select name="ddlDestino">`: 50 valores.

### El censo

De las 49 plazas de frutas y hortalizas, **41 estan vivas y 8 muertas**. Entre
las 41 publican **133,866 filas en 90 dias**. Las 3 que ingerimos aportan unas
10,500, es decir **el 8 por ciento de lo que publica la fuente**.

Lo importante no es el tamano, es el costo marginal: bajar las 41 plazas con
rango de 90 dias cuesta del orden de dos minutos, porque el endpoint acepta
rangos. No hay nada que priorizar entre ellas: ingerir las diez mejores cuesta
casi lo mismo que ingerir las 41. Lo que si hay que decidir es el orden en que
se le presentan al usuario.

### Tres plazas mas que NO son diarias, verificadas aqui

Esto es lo que valida la pieza de cadencia que se construyo ayer, y la amplia:

| Plaza | Dias en 90 | Cadencia medida |
| --- | --- | --- |
| 172 Cuernavaca, Morelos | 11 | solo lunes |
| 80 Colima, centros de distribucion | 26 | **martes y viernes**, 13 y 13 |
| 200 Oaxaca, modulo de abasto | 26 | **martes y viernes**, 13 y 13 |

Las dos ultimas las volvi a medir yo mismo con una consulta de rango de 90
dias: 26 dias publicados cada una, repartidos exactamente en 13 martes y 13
viernes. Si se agregan sin declarar su cadencia, el vigilante las dara por
muertas cada miercoles, jueves, sabado, domingo y lunes.

En flores hay una cuarta: Morelia publica **solo jueves**.

### Ocho plazas muertas, y dos de ellas murieron hace poco

| Plaza | Ultimo dia con dato |
| --- | --- |
| 170 Cuautla, Morelos | 31 de octubre de 2025 |
| 311 Oxkutzcab, Yucatan | 28 de abril de 2026 |
| 71 Tapachula, 102 Durango, 112 Celaya, 111 Irapuato, 122 Chilpancingo, 231 Cancun | sin una sola fila en cuatro anos |

Oxkutzcab es el caso que mas conviene mirar: murio hace siete meses, dentro del
horizonte en que un producto de precios deberia haberse enterado. Es la segunda
plaza que se apaga sin aviso en un ano, y confirma que la vigilancia de
reaparicion no era una pieza de lujo.

Las seis que nunca tuvieron datos son entradas de catalogo, no plazas. No se
meten como pendientes: se meten como "sin serie" o no se meten.

---

## 2. Lo que el SNIIM tiene y no estamos tocando

El SNIIM no es solo frutas y hortalizas. Verificado entrando a cada endpoint:

| Familia | Endpoint | Como se consulta | Estado |
| --- | --- | --- | --- |
| Frutas y hortalizas | `ResultadosConsultaFechaFrutasYHortalizas.aspx` | rango de fechas | vivo, 41 plazas |
| **Insumos agricolas** | `ResultadosConsultaFechaInsumos.aspx` | **quincena, mes, anio** | **vivo, 26 estados** |
| Granos basicos | `ResultadosConsultaFechaGranos.aspx` | semana del mes | vivo, 40 plazas |
| Azucar | `ResultadosConsultaFechaAzucar.aspx` | rango de fechas | vivo, 36 ingenios |
| Flores | `ResultadosConsultaFechaFlores.aspx` | rango de fechas | vivo, 4 plazas |
| Aceites comestibles | `ResultadosConsultaFechaAceite.aspx` | semana del mes | vivo, es retail de abarrote |
| Volumenes de ingreso | `ResultadosConsultaFechaVolumenIngreso.aspx` | rango de fechas | solo Monterrey, pero es el unico con TONELADAS |
| Anden de subasta | `ResultadosConsultaFechaAndenSubasta.aspx` | rango de fechas | muerto desde 2019 |
| Pecuarios | `/SNIIM-Pecuarios-Nacionales/e_Pie.asp` y `e_Can.asp` | dia, mes, anio | vivo y al dia |
| Pesqueros | `/SNIIM-PESCA/` | formulario clasico | **no verificado**: ningun intento devolvio filas |

### Insumos agricolas es el hallazgo

Es el unico dato del SNIIM que habla del **lado del costo** del productor, y
nadie en Mexico lo publica consolidado. Verificado con medicion propia sobre la
quincena 1 de octubre de 2026, barriendo los 35 destinos del formulario:

- **26 estados con datos**, 456 filas en la quincena
- **54 productos**: Afalon, Ambush, glifosato, urea, cloruro de potasio y demas
- **37 municipios distintos**, no solo la capital del estado
- columnas: Fecha, Producto, Concentracion, Presentacion, **Fuente**,
  **Municipio**, Precio Min, Precio Max, Precio Frec, Obs.
- fila real: `15/10/2026 · Ambush 34 · 34 · Litro · Distribuidora · Guadalajara
  · 352.00 · 450.00 · 401.00 · 950 ml.`

Son unas 11,000 filas al ano y 26 peticiones cada quince dias. El costo de
integracion es de una tarde.

Por que importa para este producto: hoy publicamos lo que se paga por el
producto y no tenemos nada del costo de producirlo. Con insumos por estado se
puede hablar de **margen**, que es la pregunta que el comprador y el productor
tienen de verdad, y que ninguno de los dos competidores de paga responde.

Trampa de parametros que costo media hora: el mes va como **numero** en la URL
de resultados (`Mes=10`), aunque el formulario muestre el nombre. Mandar
`Mes=Octubre` devuelve error HTTP. Y un `DestinoId` que no existe devuelve cero
filas en silencio, sin error, que es la forma mas facil de concluir que un
endpoint esta muerto cuando no lo esta.

---

## 3. El campo Origen aguanta un indice ponderado

Medido sobre Iztapalapa, 4,626 filas en 90 dias:

- **Origen esta poblado en el 100 por ciento de las filas.** Cero vacios.
- 22 valores distintos: 21 estados y la categoria Importacion.
- 92.1 por ciento trae un estado, 7.9 por ciento trae Importacion.
- De los 4,316 pares dia-producto, **4,130 traen un solo origen y 186 traen
  dos. Ninguno trae tres.** Solo el 4.3 por ciento necesita desambiguar.

Conclusion: se puede construir un indice ponderado por origen. El sesgo a
cuidar no es la cobertura sino la concentracion, porque Puebla sola explica el
25.6 por ciento de Iztapalapa y Culiacan solo reporta tres origenes. Y la
ponderacion tendria que ser por conteo de cotizaciones, no por toneladas,
porque el volumen fisico solo existe para Monterrey.

**Hallazgo colateral: la columna Calidad no sirve.** En las 4,626 filas de
Iztapalapa tiene un unico valor, "Primera". La estamos guardando como dimension
y es una constante.

---

## 4. Lo legal, verificado

`robots.txt`, leido verbatim el 21 de noviembre de 2026:

```
User-agent: *
Disallow: /Analisis/
Disallow: /*.xls$
Disallow: /2010/
Disallow: /Sicia/
Disallow: /Sicia2/
Disallow: /SiciaAnt/
Disallow: /Sicia
Disallow: Sicia
# Allow: /
```

**Ninguno de los endpoints que usamos ni de los que se recomiendan arriba esta
prohibido.** Lo unico que nos tocaria es `Disallow: /*.xls$`, que cierra la
puerta a bajar los anuarios en Excel.

No hay pagina de terminos y condiciones ni aviso legal. El unico instrumento
publicado es la politica de privacidad, que dice textualmente: "El uso de la
informacion recabada, es de carácter público y será responsabilidad directa de
los usuarios". No hay clausula de atribucion obligatoria, ni prohibicion de uso
comercial, ni restriccion de redistribucion. Esto **no cambia** el veredicto
amarillo de la ficha: seguimos atribuyendo de forma visible y la consulta
escrita del gate B12 sigue haciendo falta, porque un silencio no es una
licencia.

El articulo 108 sigue mandando sobre todo lo anterior: por mas plazas y
familias que se agreguen, se ingiere la ventana declarada y se publican
indicadores propios, nunca el acervo.

---

## 5. Deuda tecnica, medida

| Sintoma | Medicion | Diagnostico |
| --- | --- | --- |
| La base pesa 10.5 MB para 10,562 filas | `consulta_url` es el **66 por ciento del texto**, 3,456 KiB, con **136 URLs distintas para 10,562 filas** | normalizarla a una tabla de consultas ahorra ~3.4 MB sin tocar la procedencia por fila que exige B4 |
| El flujo diario comitea la base entera | 10.5 MB por corrida | lo anterior lo baja a dos tercios; a partir de 41 plazas hay que salir del repositorio |
| La pagina pesa 478 KiB | **78 por ciento es SVG en linea**, 221 graficas | comprimida son 65 KiB, asi que hoy no duele, pero crece lineal con cada plaza |
| Se hace una peticion por dia y por plaza | 5 peticiones al dia | el endpoint acepta **rangos**: una sola peticion de 7 dias por plaza captura ademas las publicaciones tardias |

Una hipotesis que la medicion descarto: los 10.5 MB **no** son archivo inflado
por podar sin `VACUUM`. Compactar recupera 4 por ciento. Son datos reales, y el
problema esta en la columna que se repite, no en el espacio libre.

---

## 6. Precio de origen: no existe diario, y eso decide el producto

### La pregunta que habia que cerrar, cerrada

El Precio Medio Rural es **anual**, no mensual. El Avance Mensual de Siembras y
Cosechas, que si sale con tres semanas de rezago, **no tiene columna de
precio**: solo superficie, produccion y rendimiento. Asi que no hay forma de
sacar precio de origen corriente del canal mensual.

Y el dato mensual **existio dos veces**. "Cosechando Numeros del Campo" tenia
una variable llamada "Medio rural", precio pagado al productor en venta de
primera mano, con presentacion mensual y semanal: congelada hacia 2020. El
"Reporte mensual de escenarios de productos agroalimentarios" publicaba precio
medio rural mensual por tonelada: ultima edicion noviembre de 2024. Las dos
veces lo mataron.

Eso es a la vez la prueba de que el hueco es real y el argumento de que nadie lo
esta cubriendo.

### Dos cosas que hay que corregir en el repositorio

**El dominio `siap.gob.mx` ya no existe.** Verificado por DNS: no resuelve, ni
el raiz ni `www`. El SIAP es ahora DGSIAP y todo vive en
`nube.agricultura.gob.mx`. Cualquier URL de SIAP en notas o documentos esta
muerta.

**La ficha de la competencia dice que AgroPrecios usa datos del SIAP.** Sigue
siendo cierto como organismo, pero el precio al productor que muestran, 21.34
pesos por kilo de aguacate, es del **cierre agricola anual**, y ahora sabemos
por que: es el unico lugar donde ese dato existe. No es que no quisieran
ponerlo diario, es que no se puede.

### Cierre Agricola del DGSIAP · la unica fuente con precio de origen real

Verificado bajando el archivo:

- URL: `https://nube.agricultura.gob.mx/index.php?view=10AE434F-A2158368-A120BC5A-EDF4AFAA&ANIO=2025`
- HTTP 200, CSV, un archivo por anio, cobertura 2003 a 2025
- la columna se llama `Preciomediorural` y esta en la cabecera, confirmado
- primera fila real: `2025, Aguascalientes, ..., Otono-Invierno, Riego,
  Tonelada, Avena forrajera en verde, sembrada 1500, cosechada 1500, volumen
  35250, rendimiento 23.5, PMR 654, valor 23053500`
- la aritmetica cuadra: 23,053,500 entre 35,250 es exactamente 654. **El PMR es
  valor de produccion entre volumen**, el precio implicito de primera mano
- granularidad: municipio, ciclo y modalidad hidrica, cientos de cultivos
- rezago: el cierre 2025 se publico el 12 de agosto de 2026, o sea unos 7.5
  meses sobre el cierre del anio y hasta 19 meses sobre un precio de enero

Licencia: la misma serie esta en la Plataforma Nacional de Datos Abiertos con
licencia **CC BY 4.0**, verificado contra el API:
`package_show?id=produccion_agricola_generada_nivel_nacional` devuelve
`license_id: CC-BY-4.0`, organizacion "Servicio de Informacion Agroalimentaria y
Pesquera (SIAP)". CC BY permite uso comercial con atribucion, asi que es
**verde**. El matiz, tambien verificado: ese conjunto de la PNDA **solo expone 4
recursos**, de los anios viejos. Los anios recientes se bajan del portal de
DGSIAP, que no declara CC BY por si mismo. Es decir, la licencia abierta esta
probada para la serie, no para el archivo exacto que conviene usar.

**Como se usa: como producto de brecha, no como feed de precio.** Con 7 a 19
meses de rezago no se negocia nada. Lo que da, y es mucho, es la brecha
estructural entre origen y mayoreo por cultivo, municipio, ciclo y modalidad,
cruzada contra el SNIIM que ya ingerimos. Eso ninguno de los dos competidores lo
puede construir, porque los dos viven del lado de destino.

**Y da la palanca para lo mensual sin pedirle a nadie que publique precios:** el
PMR es valor entre volumen. Cualquier fuente que publique **valor y volumen**
con rezago corto da PMR implicito. El tablero de Sonora ya publica valor y
volumen municipal con semanas de rezago. La ruta de expansion no es perseguir
precios, es perseguir pares valor-volumen.

---

## 7. USDA AMS · la mejor fuente nueva, y la unica verde sin matices

Esto es lo que no esperaba encontrar. Estados Unidos publica **diario** el
precio del producto mexicano cruzando la frontera, y es obra de gobierno federal
estadounidense en dominio publico.

Verificado: los cuatro PDF que importan responden HTTP 200, son PDF de verdad y
no piden llave ni cuenta.

| Reporte | Slug | Tamano | Que da |
| --- | --- | --- | --- |
| National FOB Review | `fvdfob.pdf` | 584 KiB | precios FOB de cruce con secciones propias de **Mexico Crossings** por Nogales, Otay Mesa, Texas y California |
| LA Terminal Market | `hc_fv010.pdf` | 432 KiB | precio en terminal de Los Angeles **con el pais de origen declarado producto por producto** |
| Tomato Fax Report | `fvdtomf.pdf` | 1,106 KiB | **volumen diario de cruce** en unidades de 40,000 libras, por origen, distrito y transporte |
| Weekly T-MEC perecederos | `usmcaw.pdf` | 245 KiB | analisis semanal de volumen y precio de perecederos estacionales |

URL: `https://www.ams.usda.gov/mnreports/<slug>.pdf`. Sin cuenta, sin cookie.

**Licencia VERDE**, cita de la declaracion de AMS: "Information presented on the
AMS web site is considered public information and may be distributed or copied.
Use of appropriate byline/photo/image credits is requested." Es obra federal
estadounidense: dominio publico, credito solicitado y no exigido, uso comercial
permitido sin pedir nada. El articulo 108 de la LFDA no aplica, porque protege a
quien elaboro la base bajo ley mexicana y aqui el elaborador es una agencia
federal de otro pais.

Dos advertencias tecnicas: las versiones `.txt` de esos mismos slugs **estan
congeladas desde mayo de 2024** y hay que ignorarlas, usar solo el PDF. Y el API
estructurado, MARS, **si exige abrir una cuenta eAuth real**: es el canal
oficial y no viola la regla del proyecto, pero es una cuenta a nombre del
fundador y no la abre un agente. La ruta de PDF cubre el caso sin cuenta.

**Que aporta que no tengamos: la mitad exportadora del mercado**, que hoy esta
ciega. Precio en dolares del producto mexicano en el punto de cruce y en destino
estadounidense, volumen diario por distrito de origen, y la comparacion contra
Peru, Chile, Guatemala y la produccion de California y Florida. Para aguacate,
berries, tomate, pepino, pimiento y mango, ese es el dato que decide la
rentabilidad del productor mexicano.

---

## 8. Lo demas: dos aprovechables, un socio y un cementerio

| Fuente | Que aporta | Licencia | Veredicto |
| --- | --- | --- | --- |
| **FICEDA, feed `visor.php`** | otro feed del mismo organismo, con **aves, carnicos, abarrotes y flores**, que el visor de mayoreo no trae, y sin atribucion al SNIIM, o sea dato propio | amarillo, sin aviso legal | integrar, y pedir permiso de una vez por los dos feeds |
| **Union Nacional de Avicultores** | **precio al productor** de pollo en granja y huevo, semanal, PDF de descarga libre | amarillo, sin aviso legal | integrar, pero pedir carta antes de monetizar: es un gremio accesible |
| **Sonora, subastas ganaderas** | precio de subasta por categoria desde 2008, CKAN con `license_id: cc-by` | **verde** | bajo valor operativo por ser anual, alto valor de precedente: es la unica licencia abierta explicita mexicana del barrido |
| **GCMA, Semaforo Agroalimentario** | los cuatro eslabones a la vez: productor, medio mayoreo, mayoreo y autoservicio, semanal | **rojo** | NO raspar. Es una consultora que vende exactamente este dato, y el articulo 108 opera a su favor con toda su fuerza. Se aborda como licenciante o socio, nunca raspando |
| **Mercado Abastos Estrella, NL** | precios de mayoreo reales en portal propio | **rojo** | tras login. La unica via seria crear cuenta y raspar con sesion, que es rojo automatico por regla del proyecto |
| **FIRA** | no publica precios, solo costos por hectarea | **rojo** | su aviso legal es el mas restrictivo del barrido: "Cualquier reproduccion, exhibicion, ejecucion o comercializacion del contenido de este sitio que no esten autorizadas, estan estrictamente prohibidas" |
| **INEGI, INPP** | indice de precios al productor | verde | **descartar con cita**: su metodologia dice que los genericos agropecuarios se cotizan **con precios al mayoreo**. Es lo que intentamos evitar, con otro nombre |
| **Precios de garantia, DOF** | maiz 7,000, frijol 27,000, leche 10.90 por litro | verde | precio **administrado**, no de mercado. Sirve como piso declarado |
| Centrales de abasto con portal propio, CONACCA, secretarias estatales, bolsa fisica de granos | nada | n/a | cementerio. CONACCA devuelve error de base de datos, la union de Guadalajara ya no tiene dominio, y de 14 secretarias estatales ninguna publica precios |

**Inteligencia competitiva que salio de paso:** ya hay un enjambre de sitios que
revenden el SNIIM con SEO y estan al dia, entre ellos `abastosmexico.com`,
`preciosdemexico.mx` y `abastopreciosaldia.com`. Esos son los competidores
reales, no las centrales de abasto.

---

## 9. La alarma legal, y donde pega de verdad

Verificado a mano el 21 de noviembre de 2026:

- `datos.gob.mx/libreusomx` da **HTTP 404**. Los Terminos de Libre Uso MX ya no
  estan donde todo el mundo los cita.
- `gob.mx/terminos` dice textual: "Se autoriza al Usuario a visualizar y
  descargar los materiales contenidos en el sitio solamente para su uso personal
  y no para un uso comercial".
- El portal nuevo, la Plataforma Nacional de Datos Abiertos, etiqueta **cada
  conjunto con su propia licencia**, y en el del SIAP esa etiqueta es CC BY 4.0.

**Para este proyecto no cambia nada**, y conviene decirlo con claridad: la ficha
de licencia del SNIIM ya se apoyaba en los terminos no comerciales de gob.mx
como el motivo del veredicto amarillo, y ya cita el articulo 14 **fraccion X**,
hechos y datos, en vez de la fraccion VIII. La correccion ya estaba hecha aqui.

Donde si pega es fuera: cualquier nota o expediente que use "Libre Uso MX" como
fundamento de uso comercial necesita releer el campo de licencia **por
conjunto** en la PNDA. La leccion general es que **una licencia citada de
memoria caduca**, y que hay que guardar la cita con su fecha de lectura.

---

## 10. El plan, en orden

**1. Barrer las 41 plazas vivas de frutas y hortalizas.** Doce veces mas dato
por dos minutos de ingesta, declarando la cadencia de Colima y Oaxaca para que
el vigilante no las entierre. Es lo mas barato y lo mas inmediato.

**2. USDA AMS por la ruta de PDF.** Es la mejor fuente nueva, la unica verde sin
matices, diaria, y abre la mitad exportadora que hoy no vemos. Son ocho PDF al
dia y un parser.

**3. Insumos agricolas del SNIIM.** El lado del costo, que nadie publica
consolidado, y la unica via para hablar de margen. Una tarde de trabajo.

**4. Cierre Agricola del DGSIAP como producto de brecha.** El unico precio de
origen real que existe. Se presenta como brecha estructural con su rezago
declarado en la cara, nunca como precio de hoy.

**5. Normalizar `consulta_url` y salir de la base en el repositorio.** A 41
plazas, comitear la base entera cada dia deja de ser sostenible.

**6. Las dos cartas del gate B12, mas una tercera a DGSIAP** pidiendo
confirmacion de la licencia aplicable al cierre agricola, apoyandose en que su
propia PNDA ya lo publica como CC BY 4.0.

**Lo que no se hace:** raspar GCMA, crear cuenta en Abastos Estrella, y prometer
precio de origen diario. Esa ultima es la mas importante: Mexico no lo publica,
y quien diga lo contrario esta vendiendo mayoreo con otro nombre.
