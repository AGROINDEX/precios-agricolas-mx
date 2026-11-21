# Que mas se puede ingerir, y que conviene arreglar antes

Medido el 20 y 21 de noviembre de 2026. **Documento parcial**: falta la parte de
precio de origen y la de fuentes fuera del SNIIM, que siguen en investigacion.

Todo lo que sigue esta verificado contra el sitio, no tomado de un informe. Lo
que no se pudo verificar esta marcado como no verificado.

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
