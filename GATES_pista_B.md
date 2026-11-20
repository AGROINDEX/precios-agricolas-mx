# Gates: pista B · espina dorsal de ingesta y frescura

OWNS: ingesta/**, esquema/**, web/**, licencias/**, datos/pista_b/**, fixtures/pista_b/**, .github/workflows/**, tools/verificar_esquema.py, tools/verificar_idempotencia.py, tools/verificar_procedencia.py, tools/verificar_ventana.py, tools/verificar_frescura.py, tools/verificar_pagina.py, tools/verificar_sin_velas.py, tools/verificar_licencias.py, tools/verificar_workflows.py, tools/verificar_sin_guion_largo.py

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
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\user\Desktop\Claude Code\precios-agricolas; path=a07f07046df2/34 entries; output=segunda corrida: 80 filas · sello fcc5d5895c00c7d0 · cero inserciones | idempotencia ficeda verificada · segunda corrida con cero inserciones

- [x] B4: toda fila de precio lleva procedencia completa, fuente, consulta de origen, fecha del dato y momento de captura, y el verificador falla si falta cualquiera en cualquier fila
  CHECK: python tools/verificar_procedencia.py
  EXPECT: procedencia verificada · sin filas incompletas
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\user\Desktop\Claude Code\precios-agricolas; path=a07f07046df2/34 entries; output=sin filas sin precio ni capturas anteriores a su propio dato | procedencia verificada · sin filas incompletas

- [x] B5: la base respeta el artículo 108 y no es espejo del acervo: ninguna fuente guarda más profundidad que la ventana declarada, y existe al menos un indicador derivado propio calculado sobre esa ventana
  CHECK: python tools/verificar_ventana.py
  EXPECT: ventana verificada · sin espejo del acervo y con derivado propio
  EVIDENCE: exit=0; shell=C:\WINDOWS\system32\cmd.exe; cwd=C:\Users\user\Desktop\Claude Code\precios-agricolas; path=a07f07046df2/34 entries; output=de 1173 derivados con historia, 361 difieren del precio del dia | ventana verificada · sin espejo del acervo y con derivado propio

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

B12 no lo cierra un agente: es correspondencia del fundador. Mientras esté
abierto, la ingesta corre solo con fuentes verdes.
-->
