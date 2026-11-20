# Runbook del piloto · pista A

Lo que falta para cerrar la pista A no es codigo. Es esto, y lo hace el
fundador. Siete dias de calendario.

## Antes del dia 1

**Probar a los dos competidores pagando.** AgroPrecios MX y Abasteros, el plan
mas barato de cada uno, alrededor de setecientos pesos entre los dos. Llenar los
campos de `competencia/desmontaje.md`: fecha de la prueba, plan, costo, que
entrega al comprador, que no entrega, de donde saca el dato y con que frescura.
Cerrar con la seccion del hueco. Esto va primero porque es el guion de la
conversacion con el comprador, y sin el esa conversacion se hace a ciegas.
Verificar con `python tools/verificar_competencia.py`.

**Armar la cohorte vendedora.** Quince productores o comerciantes de aguacate
Hass de la zona de Morelia. A cada uno se le pregunta si quiere recibir el
boletin diario, y se anota lo que contesto en
`datos/pista_a/cohorte_vendedor.json`, con fecha y medio. Sin ese registro el
envio es spam. Formato en `datos/pista_a/README.md`.

**Armar la cohorte compradora.** De tres a cinco compradores reales: mayorista,
exportador, cadena, servicio de alimentos o agroindustria. Van en
`datos/pista_a/cohorte_comprador.json`.

**Mandar las dos cartas de la pista B.** `correspondencia/consulta_sniim.md` al
SNIIM y `correspondencia/permiso_ficeda.md` a la Central de Abasto. Son el gate
B12 y la respuesta tarda, asi que salen el primer dia.

## Cada dia, siete dias seguidos

1. `python ingesta/sniim.py` y `python ingesta/ficeda.py`
2. `python ingesta/derivados.py`
3. `python boletin/generar.py`
4. `python tools/verificar_boletin.py --dia hoy` y
   `python tools/verificar_texto_boletin.py --boletin boletin/ultimo.md --control-positivo fixtures/pista_a/boletin_infractor.md`
5. Copiar `boletin/ultimo.md` al grupo o a la lista de difusion
6. Anotar el envio en `datos/pista_a/bitacora.json`, con cuantos lo leyeron

El dia tres es el que importa para la metrica del lado vendedor. Hay que contar
las lecturas de ese dia con calma y anotarlas.

## Lo que se anota cuando alguien contesta

Del lado vendedor, si alguien manda su propio precio: va como respuesta de tipo
`precio_propio`, con el texto literal y el precio, el producto, la plaza y la
base. Eso es oferta de dato, que es la mitad del modelo.

Del lado comprador, la conversacion es otra y se tiene aparte. Se le pone un
precio sobre la mesa, un numero concreto al mes, y se anota lo que contesto
literal, clasificado en pagaria, no pagaria o condicionada. Preguntar si "les
interesa" no cuenta y el verificador lo rechaza.

## Como se cuenta el piloto, y como no

Se cuenta como inteligencia de origen para quien compra, con el acceso gratuito
del productor como la contraparte honesta del trato. No se cuenta como salvar al
productor del coyote, porque se le cobra al lado que captura el margen.

Nunca se promete precio en finca sobre un dato de mayoreo. El boletin ya trae
ese descargo y el verificador lo exige.

## Al terminar

```powershell
node C:\Users\user\.claude\skills\unlazy\scripts\gate-check.mjs --reverify --root . GATES_pista_A.md
```

Los numeros del veredicto salen de ahi, no de la memoria. Si el lado comprador
no da tres conversaciones con precio sobre la mesa, el veredicto honesto es
parar o cambiar de cohorte, no seguir a la fase 2.
