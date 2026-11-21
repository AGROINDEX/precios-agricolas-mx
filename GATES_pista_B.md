# Gates: pista B · espina dorsal de ingesta y frescura

OWNS: ingesta/**, esquema/**, web/**, licencias/**, datos/pista_b/**, fixtures/pista_b/**, .github/workflows/**, tools/verificar_esquema.py, tools/verificar_idempotencia.py, tools/verificar_procedencia.py, tools/verificar_ventana.py, tools/verificar_frescura.py, tools/verificar_pagina.py, tools/verificar_sin_velas.py, tools/verificar_licencias.py, tools/verificar_workflows.py, tools/verificar_sin_guion_largo.py, tools/verificar_historico.py, tools/verificar_grafica_historica.py, tools/verificar_cadencia.py, tools/verificar_plaza_morelos.py, tools/verificar_frescura_cadencia.py, diseno/**

Scope: ingesta diaria incremental del SNIIM y de la Central de Abasto hacia un esquema normalizado con procedencia completa por fila, el vigilante de fuentes congeladas apuntado a las fuentes nuevas desde el día uno, y una sola página que muestra los precios de hoy con su frescura y su atribución, sin gráficas de velas.

Cadena declarada: Python 3 en el shell del proyecto. Cada verificador es un script propio del repo y solo imprime su marcador después de que pasan todas sus aserciones.

- [x] B1: el esquema normalizado existe y rechaza el duplicado por llave de fuente, fecha, producto, presentación, calidad, origen y mercado, probado contra un par de filas idénticas
  CHECK: python tools/verificar_esquema.py
  EXPECT: esquema verificado · duplicado rechazado por llave natural
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\user\Desktop\Claude Code\precios-agricolas; path=a07f07046df2/34 entries; output=INSERT directo duplicado rechazado por la base | esquema verificado · duplicado rechazado por llave natural

- [x] B2: la ingesta del SNIIM corre sobre un día y es idempotente: la segunda corrida del mismo día inserta cero filas y no modifica ninguna
  CHECK: python tools/verificar_idempotencia.py --fuente sniim
  EXPECT: idempotencia sniim verificada · segunda corrida con cero inserciones
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\user\Desktop\Claude Code\precios-agricolas; path=a07f07046df2/34 entries; output=segunda corrida: 80 filas · sello f77922f63a55db31 · cero inserciones | idempotencia sniim verificada · segunda corrida con cero inserciones

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
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\user\Desktop\Claude Code\precios-agricolas; path=a07f07046df2/34 entries; output=de 9102 derivados con historia, 2782 difieren del precio del dia | ventana verificada · sin espejo del acervo y con derivado propio

- [x] B6: el vigilante de fuentes congeladas apunta a las fuentes nuevas, lee el reporte de fetch versionado y falla cuando una fuente pasa el umbral de días sin fetch bueno, probado contra un reporte de control con una fuente congelada
  CHECK: python tools/verificar_frescura.py --control-positivo fixtures/pista_b/fetch_report_congelado.json
  EXPECT: vigilante verificado · control positivo detectado como congelado
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\user\Desktop\Claude Code\precios-agricolas; path=a07f07046df2/34 entries; output=mide dias desde el ultimo fetch bueno, no desde el ultimo intento | vigilante verificado · control positivo detectado como congelado

- [x] B7: la página de hoy muestra para cada precio su fecha, su fuente y su atribución, y cuando una fuente está congelada lo dice en la cara del usuario en vez de presentar el último dato bueno como si fuera de hoy, probado con un estado congelado simulado
  CHECK: python tools/verificar_pagina.py --estado-congelado-simulado
  EXPECT: pagina verificada · aviso de congelamiento visible y frescura por fila
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\user\Desktop\Claude Code\precios-agricolas; path=a07f07046df2/34 entries; output=con estado congelado simulado: 2 avisos para 2 fuentes, filas marcadas como dato detenido | pagina verificada · aviso de congelamiento visible y frescura por fila

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
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\user\Desktop\Claude Code\precios-agricolas; path=a07f07046df2/34 entries; output=9497 derivados propios conservados en la base | historico verificado · ventana rellenada sin exceder la declarada

- [x] B16: la vista dibuja el historico de cada producto desde las filas crudas y no presenta mediana movil en su lugar, y el verificador recalcula la serie desde la base, la compara contra los puntos dibujados y rechaza una grafica de control construida con datos desfasados
  CHECK: python tools/verificar_grafica_historica.py --control-desfasado
  EXPECT: grafica historica verificada · recalculo coincide y control desfasado rechazado
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\user\Desktop\Claude Code\precios-agricolas; path=a07f07046df2/34 entries; output=control desfasado rechazado en las 174 series con forma | grafica historica verificada · recalculo coincide y control desfasado rechazado

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

B12 no lo cierra un agente: es correspondencia del fundador. Mientras esté
abierto, la ingesta corre solo con fuentes verdes.
-->
