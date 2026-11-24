-- PREGUNTA: Entre los primeros cuatro pedidos del año (folio <= 100004), ¿cuáles tuvieron un envío con costo de flete mayor a 3,000 USD y qué guía y transportista los atendió?
-- ALGEBRA: P_cuatro = rho p (sigma folio <= 100004 (pedido)); E_cuatro = rho e (sigma folio <= 100004 (envio)); pi p.folio, p.numerocliente, p.estatus, e.numeroguia, e.clavetransportista, e.costoflete (P_cuatro join p.folio = e.folio and e.costoflete > 3000 E_cuatro)

SELECT DISTINCT
  p.folio,
  p.numerocliente,
  p.estatus,
  e.numeroguia,
  e.clavetransportista,
  e.costoflete
FROM pedido AS p
JOIN envio AS e
  ON p.folio = e.folio
 AND e.costoflete > 3000
WHERE p.folio <= 100004
ORDER BY p.folio;
