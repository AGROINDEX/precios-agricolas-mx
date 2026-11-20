# Contrato compartido · plataforma de precios agrícolas MX

Fuente de verdad del encuadre: `../PROMPT_plataforma_precios_agricolas.md`.
Este archivo fija solo lo que las dos pistas tienen que respetar por igual.

## Qué se está construyendo

La referencia de **precio en origen**, con el dato oficial de mayoreo como
espina dorsal y contraste, no como producto. Fase 1 compra audiencia
identificada, fase 2 la relación comercial con marcas de insumos, fase 3 el
marketplace de semillas inteligente. Si una decisión de fase 1 estorba a la
fase 3, gana la fase 3.

## Invariantes que cualquier gate puede invocar

1. Licencia verificada por fuente antes de integrar, con cita del texto legal.
2. Ingesta incremental y derivados propios, nunca espejo del acervo
   (artículo 108 de la LFDA, cinco años de protección a la base no original).
3. Nada de cuentas falsas, scraping con sesión iniciada ni grupos cerrados.
4. Frescura declarada siempre: fecha, hora cuando exista y fuente a la vista.
   Fuente congelada se dice en la cara del usuario, nunca se disfraza el
   último dato bueno como si fuera de hoy.
5. No prometer precio en finca cuando el dato es de mayoreo. El alcance va en
   la misma frase que el número.
6. Español neutral y prohibido el guion largo en todo texto de cara al
   usuario. El interpunto "·" sí se permite.

## Herencia desde AgroPatentIndex

Se reutiliza el patrón, no se toca el repo existente: ingesta diaria en CI con
cadencia ligera y pesada separada, `scrapers/check_fuentes_stale.py` como
vigilante de fuentes congeladas (mide días desde el último fetch BUENO, no la
antigüedad del archivo), memoria entre corridas vía reporte de fetch
versionado, Supabase, Stripe, Cloudflare Pages y R2 tras worker con control de
acceso, y el expediente de licencias con semáforo.

Nota verificada en esta sesión: en disco hay dos carpetas parecidas y Windows
las confunde por mayúsculas. La que tiene el repositorio de git y el `.env` es
`agropatent-index/`, con remoto `AGROINDEX/agropatent-index`. Ahí vive
`scrapers/check_fuentes_stale.py`, que falla por umbral de días sin fetch bueno,
con `STALE_UMBRAL_CRITICO` por defecto en 3 y `STALE_UMBRAL_NORMAL` en 8.

Las credenciales de Cloudflare de ese proyecto NO están en disco: son secretos
del repositorio en GitHub, no se pueden leer ni copiar desde aquí.

## Cadena técnica declarada para los gates

Python 3 para ingesta y para los verificadores (`python tools/verificar_*.py`),
Node solo para `gate-check.mjs`. No se asume `grep`, `tail`, `sed` ni `tr`:
todo verificador es un script propio del repo con marcador de éxito.
Re-verificación con la misma cadena, en el mismo shell declarado.

## Raíz y propiedad

Raíz de los ledgers: `precios-agricolas/`. La decisión de repo nuevo contra
carpeta dentro del actual sigue siendo del fundador (sección 5 del prompt) y no
bloquea este ledger: esta carpeta se mueve completa el día que se decida.
