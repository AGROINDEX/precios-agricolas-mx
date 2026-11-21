# Gates: pista B · espina dorsal de ingesta y frescura

OWNS: ingesta/**, esquema/**, web/**, licencias/**, datos/pista_b/**, fixtures/pista_b/**, .github/workflows/**, tools/verificar_esquema.py, tools/verificar_idempotencia.py, tools/verificar_procedencia.py, tools/verificar_ventana.py, tools/verificar_frescura.py, tools/verificar_pagina.py, tools/verificar_sin_velas.py, tools/verificar_licencias.py, tools/verificar_workflows.py, tools/verificar_sin_guion_largo.py, tools/verificar_historico.py, tools/verificar_grafica_historica.py, tools/verificar_cadencia.py, tools/verificar_plaza_morelos.py, tools/verificar_frescura_cadencia.py, tools/verificar_reaparicion.py, tools/verificar_cadencia_medida.py, tools/verificar_ingesta_rango.py, tools/verificar_base_reconstruible.py, tools/verificar_vista_escalada.py, diseno/**

Scope: ingesta diaria incremental del SNIIM y de la Central de Abasto hacia un esquema normalizado con procedencia completa por fila, el vigilante de fuentes congeladas apuntado a las fuentes nuevas desde el día uno, y una sola página que muestra los precios de hoy con su frescura y su atribución, sin gráficas de velas.

Cadena declarada: Python 3 en el shell del proyecto. Cada verificador es un script propio del repo y solo imprime su marcador después de que pasan todas sus aserciones.

- [x] B1: el esquema normalizado existe y rechaza el duplicado por llave de fuente, fecha, producto, presentación, calidad, origen y mercado, probado contra un par de filas idénticas
  CHECK: python tools/verificar_esquema.py
  EXPECT: esquema verificado · duplicado rechazado por llave natural
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\user\Desktop\Claude Code\precios-agricolas; path=a07f07046df2/34 entries; output=INSERT directo duplicado rechazado por la base | esquema verificado · duplicado rechazado por llave natural

- [x] B2: la ingesta del SNIIM corre sobre un día y es idempotente: la segunda corrida del mismo día inserta cero filas y no modifica ninguna
  CHECK: python tools/verificar_idempotencia.py --fuente sniim
  EXPECT: idempotencia sniim verificada · segunda corrida con cero inserciones
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\user\Desktop\Claude Code\precios-agricolas; path=a07f07046df2/34 entries; output=segunda corrida: 400 filas · sello 3790a2e47b50ddaf · cero inserciones | idempotencia sniim verificada · segunda corrida con cero inserciones

- [x] B3: la ingesta de la Central de Abasto corre sobre un día y es idempotente con el mismo criterio
  CHECK: python tools/verificar_idempotencia.py --fuente ficeda
  EXPECT: idempotencia ficeda verificada · segunda corrida con cero inserciones
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\user\Desktop\Claude Code\precios-agricolas; path=a07f07046df2/34 entries; output=segunda corrida: 80 filas · sello 3f93356172cdf1b0 · cero inserciones | idempotencia ficeda verificada · segunda corrida con cero inserciones

- [x] B4: toda fila de precio lleva procedencia completa, fuente, consulta de origen, fecha del dato y momento de captura, y el verificador falla si falta cualquiera en cualquier fila
  CHECK: python tools/verificar_procedencia.py
  EXPECT: procedencia verificada · sin filas incompletas
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\user\Desktop\Claude Code\precios-agricolas; path=a07f07046df2/34 entries; output=sin filas sin precio ni capturas anteriores a su propio dato | procedencia verificada · sin filas incompletas

- [x] B5: la base respeta el artículo 108 y no es espejo del acervo: ninguna fuente guarda más profundidad que la ventana declarada, y existe al menos un indicador derivado propio calculado sobre esa ventana
  CHECK: python tools/verificar_ventana.py
  EXPECT: ventana verificada · sin espejo del acervo y con derivado propio
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\user\Desktop\Claude Code\precios-agricolas; path=a07f07046df2/34 entries; output=de 124816 derivados con historia, 38051 difieren del precio del dia | ventana verificada · sin espejo del acervo y con derivado propio

- [x] B6: el vigilante de fuentes congeladas apunta a las fuentes nuevas, lee el reporte de fetch versionado y falla cuando una fuente pasa el umbral de días sin fetch bueno, probado contra un reporte de control con una fuente congelada
  CHECK: python tools/verificar_frescura.py --control-positivo fixtures/pista_b/fetch_report_congelado.json
  EXPECT: vigilante verificado · control positivo detectado como congelado
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\user\Desktop\Claude Code\precios-agricolas; path=a07f07046df2/34 entries; output=mide dias desde el ultimo fetch bueno, no desde el ultimo intento | vigilante verificado · control positivo detectado como congelado

- [x] B7: la página de hoy muestra para cada precio su fecha, su fuente y su atribución, y cuando una fuente está congelada lo dice en la cara del usuario en vez de presentar el último dato bueno como si fuera de hoy, probado con un estado congelado simulado
  CHECK: python tools/verificar_pagina.py --estado-congelado-simulado
  EXPECT: pagina verificada · aviso de congelamiento visible y frescura por fila
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\user\Desktop\Claude Code\precios-agricolas; path=a07f07046df2/34 entries; output=con estado congelado simulado: 44 avisos para 2 fuentes, filas marcadas como dato detenido | pagina verificada · aviso de congelamiento visible y frescura por fila

- [x] B8: la página no incluye gráficas de velas ni de rango alto y bajo presentadas como precio de transacción, y el mismo verificador rechaza una página de control que sí las trae
  CHECK: python tools/verificar_sin_velas.py --control-positivo fixtures/pista_b/pagina_con_velas.html
  EXPECT: ausencia de velas verificada · control positivo rechazado como se esperaba
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\user\Desktop\Claude Code\precios-agricolas; path=a07f07046df2/34 entries; output=control positivo rechazado por 7 senales, entre ellas candlestick | ausencia de velas verificada · control positivo rechazado como se esperaba

- [x] B9: toda fuente integrada tiene ficha de licencia con veredicto de semáforo y cita del texto legal que lo respalda, y el verificador falla si hay una fuente en la ingesta sin ficha o con veredicto rojo
  CHECK: python tools/verificar_licencias.py
  EXPECT: licencias verificadas · sin fuente integrada en rojo ni sin ficha
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\user\Desktop\Claude Code\precios-agricolas; path=a07f07046df2/34 entries; output=ninguna de las fuentes en rojo del expediente esta en el catalogo | licencias verificadas · sin fuente integrada en rojo ni sin ficha

- [x] B10: el CI corre la ingesta diaria y el vigilante en flujos separados, de modo que el vigilante pueda fallar sin tumbar el despliegue, con concurrencia declarada
  CHECK: python tools/verificar_workflows.py
  EXPECT: workflows verificados · ingesta y vigilante en flujos separados
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\user\Desktop\Claude Code\precios-agricolas; path=a07f07046df2/34 entries; output=el flujo de ingesta recalcula derivados y reconstruye la pagina | workflows verificados · ingesta y vigilante en flujos separados

- [x] B11: ningún texto de cara al usuario de la pista B usa guion largo, y el verificador rechaza un archivo de control que sí lo usa
  CHECK: python tools/verificar_sin_guion_largo.py --rutas web --control-positivo fixtures/pista_b/texto_con_guion_largo.md
  EXPECT: tipografia verificada · control positivo rechazado como se esperaba
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\user\Desktop\Claude Code\precios-agricolas; path=a07f07046df2/34 entries; output=control positivo rechazado por ['—'] | tipografia verificada · control positivo rechazado como se esperaba

- [x] B13: la frescura real de cada plaza queda medida sobre el movimiento de los valores y no sobre la fecha declarada, con el veredicto por plaza visible en la página, y el verificador recalcula las cifras desde las filas crudas y detecta una plaza estancada de control
  CHECK: python tools/verificar_frescura_real.py --control-estancado
  EXPECT: frescura real verificada · recalculo coincide y plaza estancada detectada
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\user\Desktop\Claude Code\precios-agricolas; path=a07f07046df2/34 entries; output=veredicto por plaza visible en la pagina publicada | frescura real verificada · recalculo coincide y plaza estancada detectada

- [x] B14: el vigilante avisa cuando una plaza se queda quieta y falla solo cuando el veredicto empeora respecto del día publicado anterior, no mientras el estado persiste, probado contra tres plazas de control: una que se estanca, una estancada desde siempre y una que se mueve
  CHECK: python tools/verificar_aviso_plaza_quieta.py
  EXPECT: aviso de plaza quieta verificado · falla en la transicion y no en el estado persistente
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\user\Desktop\Claude Code\precios-agricolas; path=a07f07046df2/34 entries; output=cableado en vigilante-diario.yml | aviso de plaza quieta verificado · falla en la transicion y no en el estado persistente

- [x] B15: la base guarda la ventana declarada rellenada desde la fuente y no mas, de modo que la vista historica tenga de donde dibujarse, y el verificador falla si alguna fuente excede su ventana o si la profundidad real es tan corta que la grafica no dice nada
  CHECK: python tools/verificar_historico.py
  EXPECT: historico verificado · ventana rellenada sin exceder la declarada
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\user\Desktop\Claude Code\precios-agricolas; path=a07f07046df2/34 entries; output=129499 derivados propios conservados en la base | historico verificado · ventana rellenada sin exceder la declarada

- [x] B16: la vista dibuja el historico de cada producto desde las filas crudas y no presenta mediana movil en su lugar, y el verificador recalcula la serie desde la base, la compara contra los puntos dibujados y rechaza una grafica de control construida con datos desfasados
  CHECK: python tools/verificar_grafica_historica.py --control-desfasado
  EXPECT: grafica historica verificada · recalculo coincide y control desfasado rechazado
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\user\Desktop\Claude Code\precios-agricolas; path=a07f07046df2/34 entries; output=control desfasado rechazado en las 1894 series con forma | grafica historica verificada · recalculo coincide y control desfasado rechazado

- [x] B17: la cadencia de publicacion de cada plaza esta declarada en una tabla unica del codigo, la ingesta consulta igual todos los dias a la plaza semanal para poder detectar que cambie de cadencia, y existe un vigilante por plaza que falla cuando una plaza falta a SU propio dia de publicacion y no cuando calla un dia que no le toca, probado contra tres plazas de control: una diaria callada, una semanal callada en su lunes y una semanal callada un jueves
  CHECK: python tools/verificar_cadencia.py --control-callada
  EXPECT: cadencia verificada · falta en su dia detectada y silencio esperado tolerado
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\user\Desktop\Claude Code\precios-agricolas; path=a07f07046df2/34 entries; output=control: 2 transiciones detectadas (diaria y semanal), semanal al dia tolerada mirandola el jueves 2026-11-19, 2 calladas viejas degradadas a nota | cadencia verificada · falta en su dia detectada y silencio esperado tolerado

- [x] B18: la plaza de Morelos esta en el piloto con su ventana declarada rellenada desde la fuente, y el verificador recuenta desde las filas crudas que todos sus dias publicados caen en el dia de la semana declarado y que ninguno excede la ventana
  CHECK: python tools/verificar_plaza_morelos.py
  EXPECT: plaza de Morelos verificada · dias publicados dentro de la ventana y en su cadencia
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\user\Desktop\Claude Code\precios-agricolas; path=a07f07046df2/34 entries; output=control positivo: el dia 2026-11-10 fuera de cadencia fue rechazado | plaza de Morelos verificada · dias publicados dentro de la ventana y en su cadencia

- [x] B19: la frescura de una plaza semanal se expresa en publicaciones y no solo en dias de calendario, de modo que publicar cada lunes no se presente como dato detenido, y la pagina dice la cadencia de cada plaza junto a su ultimo corte; el verificador rechaza una pagina de control que presenta la plaza semanal como diaria y comprueba que una plaza diaria callada cinco dias si se reporta como detenida
  CHECK: python tools/verificar_frescura_cadencia.py --control-positivo
  EXPECT: frescura por cadencia verificada · control de plaza semanal como diaria rechazado
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\user\Desktop\Claude Code\precios-agricolas; path=a07f07046df2/34 entries; output=control: plaza semanal al dia sin aviso de falta, plaza diaria callada cinco dias reportada | frescura por cadencia verificada · control de plaza semanal como diaria rechazado

- [x] B20: una plaza muerta queda en vigilancia de reaparicion: la ingesta la consulta todos los dias igual que a una viva, cada intento queda registrado aunque devuelva cero filas, y el vigilante interrumpe el dia en que la plaza vuelva a traer filas; probado con un control positivo que simula la reaparicion y con un control negativo que exige silencio mientras la plaza siga muerta
  CHECK: python tools/verificar_reaparicion.py --control-reaparicion
  EXPECT: vigilancia de reaparicion verificada · reaparicion detectada y silencio continuo tolerado
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\user\Desktop\Claude Code\precios-agricolas; path=a07f07046df2/34 entries; output=control por codigo de salida: rojo con el fixture de reaparicion, verde con el registro real | vigilancia de reaparicion verificada · reaparicion detectada y silencio continuo tolerado

- [x] B21: la cadencia de cada plaza del piloto esta MEDIDA y generada por `ingesta/medir_cadencia.py`, no escrita a mano, y el verificador vuelve a consultar una muestra de plazas en la fuente y falla si la cadencia declarada no coincide con la que la fuente publica, ademas de rechazar una tabla de control con una cadencia falsa
  CHECK: python tools/verificar_cadencia_medida.py --control-falso
  EXPECT: cadencia medida verificada · muestra coincide con la fuente y control falso rechazado
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\user\Desktop\Claude Code\precios-agricolas; path=a07f07046df2/34 entries; output=reparto declarado: diaria 38, semanal 3 | cadencia medida verificada · muestra coincide con la fuente y control falso rechazado

- [x] B22: la ingesta consulta por RANGO, una peticion por plaza para toda la ventana en vez de una por dia, lee la fecha de cada fila en vez de asumirla, y sigue siendo idempotente: la segunda corrida del mismo rango inserta cero filas
  CHECK: python tools/verificar_ingesta_rango.py
  EXPECT: ingesta por rango verificada · fecha leida por fila y segunda corrida sin inserciones
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\user\Desktop\Claude Code\precios-agricolas; path=a07f07046df2/34 entries; output=pedir 91 dias se rechaza: la ventana declarada es 90 | ingesta por rango verificada · fecha leida por fila y segunda corrida sin inserciones

- [x] B23: la base de precios deja de versionarse y se reconstruye desde la fuente en cada corrida, de modo que el repositorio no crezca con el dato, y el verificador comprueba que esta ignorada por git, que una reconstruccion en base vacia llena la ventana declarada de una plaza, y que lo que si se versiona es solo la memoria que no se puede reconstruir
  CHECK: python tools/verificar_base_reconstruible.py
  EXPECT: base reconstruible verificada · no versionada y ventana rellenable desde la fuente
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\user\Desktop\Claude Code\precios-agricolas; path=a07f07046df2/34 entries; output=base vacia reconstruida desde la fuente: 1102 filas en 14 dias publicados con una sola peticion | base reconstruible verificada · no versionada y ventana rellenable desde la fuente

- [x] B24: la vista escala a decenas de plazas sin romperse: hay un indice con una fila por plaza y una pagina por plaza, y ninguna pagina pasa el presupuesto de peso declarado; el verificador falla si una pagina lo excede y rechaza un indice de control al que le falta una plaza viva
  CHECK: python tools/verificar_vista_escalada.py --control-incompleto
  EXPECT: vista escalada verificada · presupuesto respetado e indice incompleto rechazado
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\user\Desktop\Claude Code\precios-agricolas; path=a07f07046df2/34 entries; output=control: indice sin Aguascalientes: Centro Comercial Agropec rechazado | vista escalada verificada · presupuesto respetado e indice incompleto rechazado

- [ ] B12: la consulta escrita al SNIIM está enviada a info.sniim@economia.gob.mx con fecha y copia del texto en el expediente, y la petición de permiso a la Central de Abasto está enviada o registrada como pendiente con fecha
  EVIDENCE: NO CUMPLIDO · textos redactados el 20 de noviembre de 2026 en correspondencia/consulta_sniim.md y correspondencia/permiso_ficeda.md, los dos sin enviar. El envío es del fundador: esta sesión no manda correo en su nombre. Para la FICEDA falta además el destinatario, que no está publicado en el visor y se pide por el canal de atención de ficeda.com.mx. Mientras el gate siga abierto, las dos fuentes quedan en amarillo y el dato se usa como referencia citada con atribución, no como acervo redistribuido.

<!--
B5 es el gate que cambia la arquitectura respecto a AgroPatent. Ahí se
replicaba el acervo completo de cada fuente. Aquí no se puede: el artículo 108
de la LFDA protege la base no original cinco años en uso exclusivo de quien la
elaboró. El dato puntual es libre por el artículo 14 fracción X y el 107, el
acervo no.

B6 hereda el diseño de AgroPatentIndex/scrapers/check_fuentes_stale.py, que
mide días desde el último fetch BUENO y no la antigüedad del archivo, con
umbral crítico de 3 días y normal de 8. Para un tablero de precios esta pieza
es el corazón del producto: un precio viejo presentado como de hoy es peor que
no tener precio.

B8 es un gate negativo, por eso trae control positivo obligatorio. Sin velas
no es un capricho estético: no hay precio de transacción con hora, volumen ni
calidad homogénea que las sostenga, y un comprador profesional lo detecta.

B15 y B16 salen de una correccion del fundador el 20 de noviembre de 2026: la
mediana de 7 dias no le sirve, lo que sirve es ver el historico. La mediana se
quita de la vista en vez de dejarla al lado, porque una columna que nadie usa
ocupa el lugar de la que si. El calculo derivado se conserva en la base: es lo
que sostiene el gate B5 del articulo 108.

B16 compara los puntos dibujados contra la serie recalculada desde las filas
crudas. Sin esa comparacion, una grafica bonita con los datos de otro producto
pasaria el gate, que es el modo exacto en que una vista miente sin que nadie lo
note.

B17, B18 y B19 salen de una correccion de la medicion del 20 de noviembre de
2026. Se habia concluido que las dos plazas de Morelos del SNIIM publican cero,
y era falso: Cuernavaca publica todos los lunes. La sonda preguntaba por dias
sueltos, y un dia suelto cae en lunes una vez cada siete. De ahi la leccion que
estos tres gates vuelven estructura: una plaza con cadencia propia necesita que
su cadencia este DECLARADA, porque si no, su silencio normal es indistinguible
de su muerte. Cuautla murio el 16 de octubre de 2025 y nadie lo noto.

B17 no deja de consultar a la plaza semanal los dias que no le tocan, aunque
sea gasto: dejar de preguntar es la unica forma de no enterarse de que cambio de
cadencia. Lo que cambia no es la consulta, es como se JUZGA el silencio.

B19 existe porque la medida de edad del valor cuenta dias de calendario. Para
una plaza semanal, un precio que cambia en cada publicacion tiene siete dias de
edad, y decirle al usuario que la mitad de los precios lleva siete dias sin
moverse describiria como estancada a una plaza que esta al dia.

B20 sale de medir bien lo que B17 solo habia supuesto. La Central de Abasto de
Cuautla no era una plaza intermitente: publicaba de lunes a viernes sin faltar,
98 dias en cinco meses, y murio de golpe el 31 de octubre de 2025. Lleva trece
meses en cero. Una plaza asi no se puede meter al piloto normal, porque no
tiene ni una fila y todo lo que mide por plaza recorre las filas de la base: en
el sistema normal es invisible.

Por eso la vigilancia de reaparicion registra el INTENTO y no la fila. Es la
misma leccion del vigilante de fuentes congeladas, que mide dias desde el
ultimo fetch bueno y no la antiguedad del archivo: lo que hay que guardar es la
prueba de que se pregunto, no solo la respuesta.

Este gate interrumpe con una BUENA noticia, que es raro y es a proposito. Rojo
en CI es lo unico que GitHub notifica, y el flujo del vigilante no despliega,
asi que ponerlo en rojo no deja el tablero sin actualizar. El mensaje lo dice
con todas sus letras: no es una falla, es una reaparicion, y lo que toca es
promover la plaza al piloto.

B21 a B24 salen de agregar las 41 plazas vivas del SNIIM, que es lo que
convierte en obligatorio lo que antes era opcional.

B21: con tres plazas, escribir la cadencia a mano era razonable. Con 41 es una
invitacion al error, y una cadencia declarada mal es PEOR que ninguna, porque el
vigilante juzga el silencio contra una cita equivocada. La tabla se genera
midiendo, y el gate vuelve a preguntarle a la fuente.

B22: una peticion por dia y por plaza son 90 por 41, o sea 3,690 peticiones para
llenar la ventana. Por rango son 41. El endpoint acepta rangos desde siempre y
no lo estabamos usando. Y leer por rango obliga a leer la fecha de cada fila en
vez de asumir la del dia pedido, que es mejor por si solo: captura las
publicaciones tardias.

B23 es la consecuencia incomoda. Con 41 plazas la base pasa de 10 MB a varias
decenas, y el flujo diario la comitea entera: el repositorio crecería eso cada
dia. La salida no es comprimir ni podar mas: es que la base DEJE de ser memoria.
Si cada corrida reconstruye la ventana con una peticion de rango por plaza, la
base es cache reconstruible y no hay nada que versionar. Lo que si se sigue
versionando es la memoria que no se puede reconstruir: el reporte de fetch, que
sabe cuando fue la ultima descarga buena, y el registro de sondas, que sabe
cuantas veces se le pregunto a una plaza muerta.

La resiliencia no se pierde con esto. Si la fuente se cae, la corrida falla, el
despliegue no ocurre y la ultima pagina buena sigue publicada. Antes se habria
publicado una pagina con dato viejo presentado como de hoy, que es peor.

B24: 41 plazas por unas 60 cotizaciones por una grafica cada una son del orden
de 2,500 SVG en linea, varios megabytes en una sola pagina. Una pagina por plaza
mas un indice mantiene cada pagina en el orden de cien kilobytes, y el indice
pasa a ser lo que de verdad hacia falta: ver de un golpe que plazas publicaron
hoy y cuales no.

B12 no lo cierra un agente: es correspondencia del fundador. Mientras esté
abierto, la ingesta corre solo con fuentes verdes.
-->
