"""Catalogo de plazas y cadencia declarada. ARCHIVO GENERADO, no editar a mano.

Lo genera `python ingesta/medir_cadencia.py --escribir` midiendo la fuente.
Medicion del 2026-11-20 sobre la ventana 2026-08-22 a 2026-11-20.

Los nombres son los del desplegable de la fuente, con sus acentos y sus
comillas, porque son la clave con la que se guardan las filas. Inventarles
una version limpia obligaria a mantener una traduccion a mano, que es
exactamente lo que este archivo existe para evitar.

Se declara la cadencia solo cuando la medicion la entiende. Una plaza
irregular queda sin declarar a proposito: inventarle una cita haria que el
vigilante la juzgara contra un dia equivocado.
"""

MEDIDO_EN = '2026-11-20'
VENTANA_MEDIDA = ('2026-08-22', '2026-11-20')

# Todas las plazas del desplegable, vivas y muertas.
PLAZAS = {
    '10': 'Aguascalientes: Centro Comercial Agropecuario de Aguascalientes',
    '20': 'Baja California Sur: Unión de Comerciantes de La Paz',
    '33': 'Baja California : Central de Abasto INDIA, Tijuana',
    '40': 'Campeche: Mercado "Pedro Sáinz de Baranda", Campeche',
    '50': 'Coahuila: Central de Abasto de La Laguna, Torreón',
    '61': 'Chihuahua: Central de Abasto de Chihuahua',
    '63': 'Chihuahua: Mercado de Abasto de Cd. Juárez',
    '70': 'Chiapas: Central de Abasto de Tuxtla Gutiérrez',
    '71': 'Chiapas: Tapachula',
    '80': 'Colima: Centros de distribución de Colima',
    '100': 'DF: Central de Abasto de Iztapalapa DF',
    '101': 'Durango: Centro de Distribución y Abasto de Gómez Palacio',
    '102': 'Durango: Central de Abasto "Francisco Villa"',
    '110': 'Guanajuato: Central de Abasto de León',
    '111': 'Guanajuato: Módulo de Abasto Irapuato',
    '112': 'Guanajuato: Mercado de Abasto de Celaya ("Benito Juárez")',
    '121': 'Guerrero: Central de Abastos de Acapulco',
    '122': 'Guerrero: Chilpancingo de los Bravo',
    '130': 'Hidalgo: Central de Abasto de Pachuca',
    '140': 'Jalisco: Mercado de Abasto de Guadalajara',
    '141': 'Jalisco: Mercado Felipe Ángeles de Guadalajara',
    '150': 'México: Central de Abasto de Toluca',
    '151': 'México: Central de Abasto de Ecatepec',
    '160': 'Michoacán: Mercado de Abasto de Morelia',
    '170': 'Morelos: Central de Abasto de Cuautla',
    '172': 'Morelos: Mercado "Adolfo López Mateos" de Cuernavaca',
    '180': "Nayarit: Mercado de abasto 'Adolfo López Mateos' de Tepic",
    '181': 'Nayarit: Nayarabastos de Tepic',
    '190': 'Nuevo León: Mercado de Abasto "Estrella" de San Nicolás de los Garza',
    '200': 'Oaxaca: Módulo de Abasto de Oaxaca',
    '210': 'Puebla: Central de Abasto de Puebla',
    '220': 'Querétaro: Mercado de Abasto de Querétaro',
    '230': 'Quintana Roo: Mercado de Chetumal, Quintana Roo',
    '231': 'Quintana Roo: Módulo de Abasto Cancún',
    '240': 'San Luis Potosí: Centro de Abasto de San Luis Potosí',
    '250': 'Sinaloa: Central de Abasto de Culiacán',
    '252': 'Sinaloa: Zona de Abasto de Mazatlán',
    '260': 'Sonora: Mercado de Abasto "Francisco I. Madero" de Hermosillo',
    '261': 'Sonora: Central de Abasto de Cd. Obregón',
    '270': 'Tabasco: Central de Abasto de Villahermosa',
    '280': 'Tamaulipas: Módulo de Abasto de Tampico, Madero y Altamira',
    '281': 'Tamaulipas: Módulo de Abasto de Reynosa',
    '301': 'Veracruz: Central de Abasto de Jalapa',
    '302': 'Veracruz: Central de Abasto de Minatitlán',
    '306': 'Veracruz: Mercado Malibrán',
    '310': 'Yucatán: Central de Abasto de Mérida',
    '311': 'Yucatán: Centro Mayorista Oxkutzcab',
    '312': 'Yucatán: Mercado "Casa del Pueblo"',
    '320': 'Zacatecas: Mercado de Abasto de Zacatecas',
}

# plaza -> cadencia, dias de la semana (lunes 0), umbral de silencio en dias
CADENCIAS_MEDIDAS = {
    # 10 · 62 dias en 5 dias de la semana · 3600 filas
    'Aguascalientes: Centro Comercial Agropecuario de Aguascalientes': {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
    # 33 · 62 dias en 5 dias de la semana · 4459 filas
    'Baja California : Central de Abasto INDIA, Tijuana': {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
    # 20 · 62 dias en 5 dias de la semana · 3162 filas
    'Baja California Sur: Unión de Comerciantes de La Paz': {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
    # 40 · 62 dias en 5 dias de la semana · 3410 filas
    'Campeche: Mercado "Pedro Sáinz de Baranda", Campeche': {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
    # 70 · 62 dias en 5 dias de la semana · 2718 filas
    'Chiapas: Central de Abasto de Tuxtla Gutiérrez': {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
    # 61 · 62 dias en 5 dias de la semana · 1736 filas
    'Chihuahua: Central de Abasto de Chihuahua': {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
    # 63 · 61 dias en 5 dias de la semana · 1769 filas
    'Chihuahua: Mercado de Abasto de Cd. Juárez': {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
    # 50 · 60 dias en 5 dias de la semana · 3579 filas
    'Coahuila: Central de Abasto de La Laguna, Torreón': {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
    # 80 · 26 de 26 ocasiones en martes y viernes, regularidad 100% · 1222 filas
    'Colima: Centros de distribución de Colima': {
        "cadencia": 'semanal',
        "dias": [1, 4],
        "umbral_dias": 13,
    },
    # 100 · 62 dias en 5 dias de la semana · 4626 filas
    'DF: Central de Abasto de Iztapalapa DF': {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
    # 101 · 62 dias en 5 dias de la semana · 3534 filas
    'Durango: Centro de Distribución y Abasto de Gómez Palacio': {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
    # 110 · 62 dias en 5 dias de la semana · 3410 filas
    'Guanajuato: Central de Abasto de León': {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
    # 121 · 62 dias en 5 dias de la semana · 2728 filas
    'Guerrero: Central de Abastos de Acapulco': {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
    # 130 · 62 dias en 5 dias de la semana · 2976 filas
    'Hidalgo: Central de Abasto de Pachuca': {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
    # 141 · 62 dias en 5 dias de la semana · 5147 filas
    'Jalisco: Mercado Felipe Ángeles de Guadalajara': {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
    # 140 · 62 dias en 5 dias de la semana · 5304 filas
    'Jalisco: Mercado de Abasto de Guadalajara': {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
    # 160 · 62 dias en 5 dias de la semana · 5230 filas
    'Michoacán: Mercado de Abasto de Morelia': {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
    # 172 · 11 de 13 ocasiones en lunes, regularidad 85% · 626 filas
    'Morelos: Mercado "Adolfo López Mateos" de Cuernavaca': {
        "cadencia": 'semanal',
        "dias": [0],
        "umbral_dias": 17,
    },
    # 151 · 62 dias en 5 dias de la semana · 3745 filas
    'México: Central de Abasto de Ecatepec': {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
    # 150 · 61 dias en 5 dias de la semana · 3387 filas
    'México: Central de Abasto de Toluca': {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
    # 180 · 57 dias en 5 dias de la semana · 4559 filas
    "Nayarit: Mercado de abasto 'Adolfo López Mateos' de Tepic": {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
    # 181 · 57 dias en 5 dias de la semana · 4560 filas
    'Nayarit: Nayarabastos de Tepic': {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
    # 190 · 61 dias en 5 dias de la semana · 5763 filas
    'Nuevo León: Mercado de Abasto "Estrella" de San Nicolás de los Garza': {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
    # 200 · 26 de 26 ocasiones en martes y viernes, regularidad 100% · 1447 filas
    'Oaxaca: Módulo de Abasto de Oaxaca': {
        "cadencia": 'semanal',
        "dias": [1, 4],
        "umbral_dias": 13,
    },
    # 210 · 62 dias en 5 dias de la semana · 4038 filas
    'Puebla: Central de Abasto de Puebla': {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
    # 220 · 62 dias en 5 dias de la semana · 3720 filas
    'Querétaro: Mercado de Abasto de Querétaro': {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
    # 230 · 62 dias en 5 dias de la semana · 4278 filas
    'Quintana Roo: Mercado de Chetumal, Quintana Roo': {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
    # 240 · 62 dias en 5 dias de la semana · 2967 filas
    'San Luis Potosí: Centro de Abasto de San Luis Potosí': {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
    # 250 · 62 dias en 5 dias de la semana · 2976 filas
    'Sinaloa: Central de Abasto de Culiacán': {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
    # 252 · 61 dias en 5 dias de la semana · 2256 filas
    'Sinaloa: Zona de Abasto de Mazatlán': {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
    # 261 · 62 dias en 5 dias de la semana · 3358 filas
    'Sonora: Central de Abasto de Cd. Obregón': {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
    # 260 · 61 dias en 5 dias de la semana · 3111 filas
    'Sonora: Mercado de Abasto "Francisco I. Madero" de Hermosillo': {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
    # 270 · 62 dias en 5 dias de la semana · 3348 filas
    'Tabasco: Central de Abasto de Villahermosa': {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
    # 281 · 62 dias en 5 dias de la semana · 2418 filas
    'Tamaulipas: Módulo de Abasto de Reynosa': {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
    # 280 · 62 dias en 5 dias de la semana · 2046 filas
    'Tamaulipas: Módulo de Abasto de Tampico, Madero y Altamira': {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
    # 301 · 62 dias en 5 dias de la semana · 3782 filas
    'Veracruz: Central de Abasto de Jalapa': {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
    # 302 · 62 dias en 5 dias de la semana · 3397 filas
    'Veracruz: Central de Abasto de Minatitlán': {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
    # 306 · 62 dias en 5 dias de la semana · 3932 filas
    'Veracruz: Mercado Malibrán': {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
    # 310 · 62 dias en 5 dias de la semana · 2341 filas
    'Yucatán: Central de Abasto de Mérida': {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
    # 312 · 62 dias en 5 dias de la semana · 1195 filas
    'Yucatán: Mercado "Casa del Pueblo"': {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
    # 320 · 59 dias en 5 dias de la semana · 2006 filas
    'Zacatecas: Mercado de Abasto de Zacatecas': {
        "cadencia": 'diaria',
        "dias": None,
        "umbral_dias": 3,
    },
}

# Plazas del catalogo sin cadencia declarable, con su motivo medido.
SIN_CADENCIA = {
    'Chiapas: Tapachula': ('muerta', 'sin una sola fila en la ventana'),
    'Durango: Central de Abasto "Francisco Villa"': ('muerta', 'sin una sola fila en la ventana'),
    'Guanajuato: Mercado de Abasto de Celaya ("Benito Juárez")': ('muerta', 'sin una sola fila en la ventana'),
    'Guanajuato: Módulo de Abasto Irapuato': ('muerta', 'sin una sola fila en la ventana'),
    'Guerrero: Chilpancingo de los Bravo': ('muerta', 'sin una sola fila en la ventana'),
    'Morelos: Central de Abasto de Cuautla': ('muerta', 'sin una sola fila en la ventana'),
    'Quintana Roo: Módulo de Abasto Cancún': ('muerta', 'sin una sola fila en la ventana'),
    'Yucatán: Centro Mayorista Oxkutzcab': ('muerta', 'sin una sola fila en la ventana'),
}

# Plazas que se ingieren. Son las que publicaron en la ventana medida.
PILOTO = [
    '190',  # Nuevo León: Mercado de Abasto "Estrella" de San Nicolás 
    '140',  # Jalisco: Mercado de Abasto de Guadalajara
    '160',  # Michoacán: Mercado de Abasto de Morelia
    '141',  # Jalisco: Mercado Felipe Ángeles de Guadalajara
    '100',  # DF: Central de Abasto de Iztapalapa DF
    '181',  # Nayarit: Nayarabastos de Tepic
    '180',  # Nayarit: Mercado de abasto 'Adolfo López Mateos' de Tepi
    '33',  # Baja California : Central de Abasto INDIA, Tijuana
    '230',  # Quintana Roo: Mercado de Chetumal, Quintana Roo
    '210',  # Puebla: Central de Abasto de Puebla
    '306',  # Veracruz: Mercado Malibrán
    '301',  # Veracruz: Central de Abasto de Jalapa
    '151',  # México: Central de Abasto de Ecatepec
    '220',  # Querétaro: Mercado de Abasto de Querétaro
    '10',  # Aguascalientes: Centro Comercial Agropecuario de Aguasca
    '50',  # Coahuila: Central de Abasto de La Laguna, Torreón
    '101',  # Durango: Centro de Distribución y Abasto de Gómez Palaci
    '110',  # Guanajuato: Central de Abasto de León
    '40',  # Campeche: Mercado "Pedro Sáinz de Baranda", Campeche
    '302',  # Veracruz: Central de Abasto de Minatitlán
    '150',  # México: Central de Abasto de Toluca
    '261',  # Sonora: Central de Abasto de Cd. Obregón
    '270',  # Tabasco: Central de Abasto de Villahermosa
    '20',  # Baja California Sur: Unión de Comerciantes de La Paz
    '260',  # Sonora: Mercado de Abasto "Francisco I. Madero" de Hermo
    '130',  # Hidalgo: Central de Abasto de Pachuca
    '250',  # Sinaloa: Central de Abasto de Culiacán
    '240',  # San Luis Potosí: Centro de Abasto de San Luis Potosí
    '121',  # Guerrero: Central de Abastos de Acapulco
    '70',  # Chiapas: Central de Abasto de Tuxtla Gutiérrez
    '281',  # Tamaulipas: Módulo de Abasto de Reynosa
    '310',  # Yucatán: Central de Abasto de Mérida
    '252',  # Sinaloa: Zona de Abasto de Mazatlán
    '280',  # Tamaulipas: Módulo de Abasto de Tampico, Madero y Altami
    '320',  # Zacatecas: Mercado de Abasto de Zacatecas
    '63',  # Chihuahua: Mercado de Abasto de Cd. Juárez
    '61',  # Chihuahua: Central de Abasto de Chihuahua
    '200',  # Oaxaca: Módulo de Abasto de Oaxaca
    '80',  # Colima: Centros de distribución de Colima
    '312',  # Yucatán: Mercado "Casa del Pueblo"
    '172',  # Morelos: Mercado "Adolfo López Mateos" de Cuernavaca
]

# Plazas que no publican nada y se consultan solo para notar si vuelven.
# De estas no se guardan filas: se guarda el INTENTO, en sondas.py.
VIGILANCIA = [
    '71',  # Chiapas: Tapachula
    '102',  # Durango: Central de Abasto "Francisco Villa"
    '111',  # Guanajuato: Módulo de Abasto Irapuato
    '112',  # Guanajuato: Mercado de Abasto de Celaya ("Benito Juárez"
    '122',  # Guerrero: Chilpancingo de los Bravo
    '170',  # Morelos: Central de Abasto de Cuautla
    '231',  # Quintana Roo: Módulo de Abasto Cancún
    '311',  # Yucatán: Centro Mayorista Oxkutzcab
]
