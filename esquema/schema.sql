-- Esquema normalizado de la pista B.
--
-- Escrito en SQL portable a proposito: corre en SQLite para el piloto y se
-- mueve a Postgres (Supabase) sin rediseno. Lo unico especifico de SQLite es
-- el uso de TEXT para fecha y hora, que en Postgres pasan a date y time.
--
-- REGLA DEL ARTICULO 108. Esta base no es espejo del acervo de nadie. Guarda
-- una ventana corta y declarada por fuente (columna ventana_dias) y calcula
-- indicadores propios sobre ella. La profundidad historica se consulta en la
-- fuente, que es quien la elaboro.

CREATE TABLE IF NOT EXISTS fuentes (
    clave             TEXT PRIMARY KEY,
    nombre            TEXT NOT NULL,
    url_base          TEXT NOT NULL,
    atribucion        TEXT NOT NULL,
    licencia_veredicto TEXT NOT NULL CHECK (licencia_veredicto IN ('verde', 'amarillo', 'rojo')),
    licencia_ficha    TEXT NOT NULL,
    alcance           TEXT NOT NULL CHECK (alcance IN ('mayoreo', 'menudeo', 'origen')),
    critica           INTEGER NOT NULL DEFAULT 0,
    ventana_dias      INTEGER NOT NULL
);

-- Una fila por observacion de precio. La llave natural impide el duplicado y
-- es lo que hace idempotente a la ingesta: correr dos veces el mismo dia no
-- agrega nada.
CREATE TABLE IF NOT EXISTS precios (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    fuente        TEXT NOT NULL REFERENCES fuentes(clave),
    fecha_dato    TEXT NOT NULL,
    hora_dato     TEXT,
    categoria     TEXT,
    producto      TEXT NOT NULL,
    calidad       TEXT NOT NULL DEFAULT '',
    presentacion  TEXT NOT NULL DEFAULT '',
    origen        TEXT NOT NULL DEFAULT '',
    mercado       TEXT NOT NULL,
    observaciones TEXT NOT NULL DEFAULT '',
    precio_min    REAL,
    precio_max    REAL,
    precio_frec   REAL,
    moneda        TEXT NOT NULL DEFAULT 'MXN',
    -- Sobre que esta cotizado el numero. El SNIIM se consulta con precio por
    -- kilogramo calculado y la Central de Abasto publica por presentacion
    -- comercial, asi que 34.44 y 310.00 pueden ser el mismo precio del mismo
    -- aguacate. Sin esta columna, ponerlos en la misma tabla miente.
    base_precio   TEXT NOT NULL DEFAULT '' CHECK (base_precio IN ('', 'kilogramo', 'presentacion')),
    alcance       TEXT NOT NULL CHECK (alcance IN ('mayoreo', 'menudeo', 'origen')),
    consulta_url  TEXT NOT NULL,
    capturado_en  TEXT NOT NULL,
    UNIQUE (fuente, fecha_dato, producto, calidad, presentacion, origen, mercado, observaciones)
);

CREATE INDEX IF NOT EXISTS idx_precios_fecha ON precios (fecha_dato);
CREATE INDEX IF NOT EXISTS idx_precios_producto ON precios (producto, mercado, fecha_dato);

-- Indicadores propios. No son dato de la fuente: son calculo nuestro sobre la
-- ventana, y por eso se pueden publicar sin replicar el acervo ajeno.
CREATE TABLE IF NOT EXISTS derivados (
    fuente        TEXT NOT NULL REFERENCES fuentes(clave),
    producto      TEXT NOT NULL,
    mercado       TEXT NOT NULL,
    fecha_dato    TEXT NOT NULL,
    mediana_frec_7d REAL,
    variacion_pct_1d REAL,
    amplitud_rel  REAL,
    n_obs_7d      INTEGER NOT NULL,
    calculado_en  TEXT NOT NULL,
    PRIMARY KEY (fuente, producto, mercado, fecha_dato)
);
