# Gates: raíz · integración y veredicto

OWNS: CONTRATO.md, PLAN.md, DECISIONES.md, GATES_raiz.md, decisiones/**, tools/verificar_decisiones.py, tools/verificar_veredicto.py

Scope: las dos pistas quedan verificadas por el conductor y no por quien las produjo, las decisiones del fundador quedan registradas con fecha y dueño, y el piloto termina en un veredicto escrito que se sostiene con las cuatro métricas medidas, dos por cada lado del modelo.

- [ ] R1: las dos decisiones ya resueltas están registradas con su fecha y las abiertas están listadas con dueño, y el verificador falla si una decisión se declara resuelta sin fecha
  CHECK: python tools/verificar_decisiones.py
  EXPECT: decisiones verificadas · resueltas con fecha y abiertas con dueño
  EVIDENCE: pending

- [ ] R2: el nombre está elegido y el dominio comprado, con el correo y la cuenta de cobro apuntados a él, separado de agropatent.com
  EVIDENCE: pending

- [ ] R3: el conductor volvió a correr con --reverify todos los gates ejecutables de la pista A y de la pista B, y ninguno regresó a no cumplido
  EVIDENCE: pending

- [ ] R4: el veredicto de continuar o parar está escrito y cita las cuatro métricas medidas del piloto, dos del lado vendedor y dos del lado comprador, cada una con el número que salió del verificador y no de la memoria
  CHECK: python tools/verificar_veredicto.py
  EXPECT: veredicto verificado · cuatro metricas citadas y trazadas a evidencia
  EVIDENCE: pending

- [ ] R5: el encuadre público del producto queda como inteligencia de origen para quien compra, con el acceso gratuito del lado vendedor declarado en la misma pieza, y sin prometer precio en finca donde el dato es de mayoreo
  EVIDENCE: pending

<!--
R3 es la regla de la casa en este ledger: ningún subagente verifica su propia
hoja, y --status no es re-ejecución.

R4 existe porque el riesgo de esta pista no es construir mal, es construir algo
que nadie quiere y reportarlo como éxito. Si el lado comprador no da tres
conversaciones con precio sobre la mesa, el veredicto honesto es parar o
cambiar de cohorte, no seguir a la fase 2.
-->
