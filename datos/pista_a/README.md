# Registros del piloto de la pista A

Tres archivos, que son la unica fuente de las metricas del piloto. Los
verificadores leen de aqui y no aceptan numeros escritos aparte: si una cifra no
sale de estos archivos, no existe.

Hoy los tres estan vacios a proposito. **Ningun agente los llena.** Las personas
son reales o no son, y un registro inventado convierte el piloto en teatro.

## cohorte_vendedor.json

Productores y comerciantes que reciben el boletin gratis y son la fuente del
precio en origen. Minimo del gate A3: quince.

```json
{
  "lado": "vendedor",
  "registros": [
    {
      "id": "v01",
      "nombre": "nombre o razon social",
      "rol": "productor | comerciante | acopiador",
      "cultivo": "aguacate hass",
      "plaza": "Michoacan: Mercado de Abasto de Morelia",
      "canal": "whatsapp | telegram",
      "contacto": "+52 ...",
      "fuente_del_contacto": "como se llego a esta persona",
      "consentimiento": {
        "fecha": "2026-11-21",
        "medio": "mensaje de whatsapp | llamada | en persona",
        "texto": "lo que la persona contesto cuando se le pregunto"
      }
    }
  ]
}
```

El consentimiento no es un campo de tramite. Sin el, el envio es spam y el
registro no entra: el gate falla si falta la fecha, el medio o el texto.

## cohorte_comprador.json

Mayoristas, exportadores, cadenas, servicio de alimentos o agroindustria. Es el
lado que paga. Minimo del gate A4: tres.

```json
{
  "lado": "comprador",
  "registros": [
    {
      "id": "c01",
      "empresa": "razon social",
      "persona": "nombre",
      "cargo": "compras | abasto | categoria",
      "tipo": "mayorista | exportador | cadena | servicio de alimentos | agroindustria",
      "contacto": "correo o telefono",
      "fecha_conversacion": "2026-11-24",
      "fuente_del_contacto": "como se llego a esta empresa"
    }
  ]
}
```

## bitacora.json

Un envio por dia y las respuestas que llegaron. Siete dias seguidos para el
gate A5.

```json
{
  "envios": [
    {
      "fecha": "2026-11-21",
      "lado": "vendedor",
      "boletin": "boletin/2026-11-21_aguacate_hass.md",
      "canal": "whatsapp",
      "destinatarios": ["v01", "v02"],
      "lecturas": 0,
      "nota": "lecturas se cuenta a mano sobre los acuses del canal"
    }
  ],
  "respuestas": [
    {
      "fecha": "2026-11-23",
      "lado": "vendedor",
      "contacto": "v01",
      "tipo": "precio_propio",
      "texto": "lo que contesto, literal",
      "precio": { "producto": "Aguacate Hass", "precio": 28.5, "plaza": "huerto, Tacambaro", "base": "kilogramo" }
    },
    {
      "fecha": "2026-11-25",
      "lado": "comprador",
      "contacto": "c01",
      "tipo": "disposicion_a_pagar",
      "precio_puesto": 1500,
      "periodo": "mensual",
      "texto": "lo que contesto, literal",
      "clasificacion": "pagaria | no_pagaria | condicionada"
    }
  ]
}
```

`precio_puesto` es el numero que se le dijo al comprador, no una estimacion.
Una conversacion sin precio sobre la mesa no cuenta para el gate A7: preguntar
si algo "les interesa" no mide disposicion a pagar.
