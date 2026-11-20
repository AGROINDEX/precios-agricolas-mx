# Gates: pista A · validación de demanda de dos lados

OWNS: boletin/**, datos/pista_a/**, competencia/**, fixtures/pista_a/**, tools/verificar_competencia.py, tools/verificar_boletin.py, tools/verificar_texto_boletin.py, tools/verificar_cohortes.py, tools/verificar_bitacora_envio.py, tools/verificar_metricas.py, tools/verificar_boletin_desde_base.py

Scope: un boletín diario de precios de un cultivo y una plaza, distribuido siete días seguidos por WhatsApp o Telegram a dos cohortes reales y separadas, que deja medido con números calculados desde bitácora si el lado vendedor aporta dato y si el lado comprador pagaría por el agregado.

Cadena declarada: Python 3 en el shell del proyecto. Cada verificador es un script propio del repo y solo imprime su marcador después de que pasan todas sus aserciones.

- [x] A1: el boletín del día se genera para un cultivo y una plaza, y cada precio sale con su fecha, su hora cuando exista, su fuente, su atribución y el alcance declarado, mayoreo u origen, en la misma frase del número
  CHECK: python tools/verificar_boletin.py --dia hoy
  EXPECT: boletin verificado · procedencia y alcance completos en todas las filas
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\user\Desktop\Claude Code\precios-agricolas; path=a07f07046df2/34 entries; output=trazas verificadas contra la base: 2 | boletin verificado · procedencia y alcance completos en todas las filas

- [x] A2: el texto del boletín no promete precio en finca cuando el dato es de mayoreo y no usa guion largo, y el mismo verificador rechaza un boletín infractor de control
  CHECK: python tools/verificar_texto_boletin.py --boletin boletin/ultimo.md --control-positivo fixtures/pista_a/boletin_infractor.md
  EXPECT: texto verificado · control positivo rechazado como se esperaba
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\user\Desktop\Claude Code\precios-agricolas; path=a07f07046df2/34 entries; output=control positivo rechazado por ['guion largo', 'movimiento del precio en finca', 'precio en finca con cifra', 'precio presentado como garantizado', 'pronostico de precio', 'recomendacion de venta'] | texto verificado · control positivo rech

- [ ] A3: cohorte del lado vendedor registrada con al menos quince productores o comerciantes reales, cada uno con canal, fecha y consentimiento explícito, sin una sola cuenta falsa ni grupo cerrado raspado
  CHECK: python tools/verificar_cohortes.py --lado vendedor --minimo 15
  EXPECT: cohorte vendedor verificada · consentimiento presente en todos los registros
  EVIDENCE: pending

- [ ] A4: cohorte del lado comprador registrada con tres a cinco compradores reales, mayorista, exportador, cadena, servicio de alimentos o agroindustria, cada uno con empresa, cargo y fecha de conversación
  CHECK: python tools/verificar_cohortes.py --lado comprador --minimo 3
  EXPECT: cohorte comprador verificada · tres o mas compradores con conversacion fechada
  EVIDENCE: pending

- [ ] A5: la bitácora cubre siete días consecutivos con un envío por día y sin huecos, y distingue por lado a quién se le envió qué
  CHECK: python tools/verificar_bitacora_envio.py --dias 7
  EXPECT: bitacora verificada · siete dias consecutivos sin huecos
  EVIDENCE: pending

- [ ] A6: la métrica del lado vendedor queda calculada desde la bitácora, no copiada: lecturas al tercer día y número de respuestas que traen el precio propio de quien contesta
  CHECK: python tools/verificar_metricas.py --lado vendedor
  EXPECT: metrica vendedor calculada desde bitacora
  EVIDENCE: pending

- [ ] A7: la métrica del lado comprador queda calculada desde la bitácora: al menos tres conversaciones donde se puso un precio sobre la mesa, con la respuesta registrada textual y clasificada en pagaría, no pagaría o condicionada
  CHECK: python tools/verificar_metricas.py --lado comprador
  EXPECT: metrica comprador calculada desde bitacora
  EVIDENCE: pending

- [x] A8: el boletín se arma desde la base normalizada de la pista B y no a mano, con el identificador de cada fila trazado hasta la ingesta
  CHECK: python tools/verificar_boletin_desde_base.py
  EXPECT: boletin trazado a la base · sin filas capturadas a mano
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\user\Desktop\Claude Code\precios-agricolas; path=a07f07046df2/34 entries; output=control interno: una cifra ajena a la base si es rechazada | boletin trazado a la base · sin filas capturadas a mano

- [ ] A11: los dos competidores mexicanos fueron probados pagando su plan y no solo mirados por fuera, y existe un desmontaje escrito que para cada uno registra la fecha de la prueba, el plan contratado y su costo, qué entrega al lado comprador, qué no entrega, de dónde saca el dato y con qué frescura, y cierra con el hueco concreto que queda para la referencia de precio en origen
  CHECK: python tools/verificar_competencia.py
  EXPECT: competencia verificada · dos productos probados con campos completos y hueco declarado
  EVIDENCE: pending

- [ ] A9: existe acuerdo escrito con al menos quien ya arma una lista de precios en origen, o constancia fechada de que se pidió y de qué contestó
  EVIDENCE: NO CUMPLIDO · no hay acuerdo ni constancia. Es gestión del fundador con quien ya arma listas, y no hay atajo: la vía de raspar grupos de Facebook está cerrada desde que Meta removió la Groups API en abril de 2024, y los grupos cerrados quedan fuera por definición.

- [ ] A10: el encuadre del piloto está revisado contra la decisión del fundador, inteligencia de origen para quien compra, con el acceso gratuito del lado vendedor como contraparte declarada, y sin la narrativa de salvar al productor del coyote
  EVIDENCE: PARCIAL, NO CUMPLIDO · revisada la pieza del lado vendedor, que es boletin/ultimo.md: declara que el mayoreo no es precio en finca, dice que entre ese número y lo que recibe quien cosecha están el flete, la merma y el margen de quien compra, ofrece el acceso gratuito a cambio del precio propio, y no usa la narrativa del coyote. Falta la pieza del lado comprador, que todavía no existe: su guion se escribe con el desmontaje de A11 y se prueba en las conversaciones de A4.

<!--
A8 depende de B2. Hasta que la pista B tenga ingesta idempotente verificada, el
boletín se arma desde el dato oficial descargado a mano y A8 queda abierto, lo
cual no exime a A1 de declarar procedencia por fila.

A3 y A4 son el cuello de botella real de esta pista y no los puede cerrar un
agente: dependen de la red del fundador. Si una de las dos cohortes no se
arma, se abandona el gate con razón escrita en vez de bajar el mínimo.

A11 va antes de A4, y es orden, no sugerencia. No se puede sostener una
conversación de venta de inteligencia de origen con un comprador sin saber qué
le dan ya los dos incumbentes por doscientos pesos al mes: AgroPrecios MX con
predicción a siete y catorce días, alertas, exportación y chat, y Abasteros con
cuarenta y ocho ciudades, doscientas dieciocho centrales, arbitraje entre
plazas y calculadora de fletes, en planes de cuatrocientos noventa y nueve y
mil novecientos noventa y nueve. Con A4 abierto y A11 sin cumplir, la
conversación del lado comprador se hace a ciegas y su resultado no sirve como
evidencia. El desmontaje de A11 es insumo de venta antes que de producto: lo
que salga de ahí es el guion de A4.

A11 exige probar pagando, no mirar por fuera, así que la contratación de los
dos planes, del orden de setecientos pesos entre ambos, es acción del fundador
y no de un agente. El gate solo verifica que el desmontaje escrito trae todos
sus campos.

A6 y A7 miden cosas distintas a propósito. El lado vendedor se mide por oferta
de dato, el lado comprador por disposición a pagar. Un número alto del lado
vendedor no prueba negocio, y así hay que reportarlo.
-->
