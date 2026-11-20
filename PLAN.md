# Plan · árbol de profundidad

Modo: orquestado con dos hojas independientes y una rama de integración.

```text
raíz · referencia de precio en origen (GATES_raiz.md)
├── pista-A · validación de demanda, boletín diario 1 cultivo + 1 plaza (GATES_pista_A.md)
└── pista-B · espina dorsal técnica de ingesta y frescura (GATES_pista_B.md)
```

| Nodo | Ledger | OWNS | Depende de | Estado |
|---|---|---|---|---|
| pista-A | `GATES_pista_A.md` | `boletin/**`, `competencia/**`, `tools/verificar_competencia.py`, `tools/verificar_boletin*.py`, `tools/verificar_bitacora*.py`, `tools/verificar_metricas*.py`, `tools/verificar_sin_precio_finca.py`, `datos/pista_a/**` | nada para arrancar · A8 depende de B2 · A4 depende de A11 | PENDIENTE |
| pista-B | `GATES_pista_B.md` | `ingesta/**`, `esquema/**`, `web/**`, `licencias/**`, `fixtures/**`, `.github/workflows/**`, `tools/verificar_esquema.py`, `tools/verificar_idempotencia.py`, `tools/verificar_procedencia.py`, `tools/verificar_ventana.py`, `tools/verificar_frescura.py`, `tools/verificar_pagina.py`, `tools/verificar_sin_velas.py`, `tools/verificar_licencias.py`, `tools/verificar_workflows.py`, `tools/verificar_sin_guion_largo.py`, `datos/pista_b/**` | nada | 11 de 12 VERIFICADOS, B12 abierto |
| raíz | `GATES_raiz.md` | `GATES_raiz.md`, `CONTRATO.md`, `PLAN.md`, `decisiones/**` | pista-A y pista-B verificadas | PENDIENTE |

Las dos hojas se despachan en paralelo porque sus `OWNS:` son disjuntos. La
única costura es A7, que exige que el boletín se arme desde la base de la pista
B y no a mano: hasta que B2 esté verificado, A7 queda abierto y el boletín se
arma desde el dato oficial descargado a mano, lo cual está declarado en A1.

Ningún subagente verifica su propia hoja. El conductor vuelve a correr los
gates ejecutables de cada hoja con `--reverify` antes de marcarla VERIFICADA.

## Lo que cambió con las decisiones del 20 de noviembre

La pista A dejo de medir una sola cosa. Con el comprador como quien paga, el
piloto mide dos lados con dos cohortes y dos metricas separadas: oferta de dato
del lado vendedor (A3, A6) y disposicion a pagar del lado comprador (A4, A7).

La marca y el dominio aparte entran a la ruta critica y viven en el ledger raiz
como R2, porque condicionan el despliegue, el correo y la cuenta de cobro. La
pista B puede avanzar sin eso: corre en CI y aun no publica.

Ver DECISIONES.md para el detalle y para las tres decisiones que siguen
abiertas.

## Gate agregado el 20 de noviembre

A11, el desmontaje de los dos competidores mexicanos probando sus planes de
pago, entra a la pista A como precondicion de A4: el guion de la conversacion
con el lado comprador sale de ahi. Contratar los dos planes es accion del
fundador, del orden de setecientos pesos entre ambos.

## Estado de la pista B al 20 de noviembre de 2026

Once de los doce gates estan cumplidos con evidencia en el ledger, re-corridos
por el conductor con `--reverify`. B12 sigue abierto y es correspondencia del
fundador: los dos textos estan redactados en `correspondencia/` y ninguno se
envio desde esta sesion. Mientras siga abierto, las dos fuentes quedan en
amarillo y el dato se usa como referencia citada con atribucion.

La base vive en `datos/pista_b/precios.db`, con ventana de noventa dias por
fuente y poda en cada ingesta. Hoy trae 1,637 filas del 6 al 20 de noviembre.
