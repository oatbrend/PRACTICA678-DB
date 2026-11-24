-- PREGUNTA: Para todos los pedidos con folio menor o igual a 100004, ¿cuál es su número de guía y costo de flete, conservando con NULL los pedidos cancelados que no tienen envío?
-- ALGEBRA: P_cuatro = pi folio, numerocliente, estatus (sigma folio <= 100004 (pedido)); E_guia = pi folio, numeroguia, costoflete (envio); P_cuatro left outer join E_guia

SELECT
  p.folio,
  p.numerocliente,
  p.estatus,
  e.numeroguia,
  e.costoflete
FROM (
  SELECT folio, numerocliente, estatus
  FROM pedido
  WHERE folio <= 100004
) AS p
LEFT JOIN (
  SELECT folio, numeroguia, costoflete
  FROM envio
) AS e
  ON p.folio = e.folio
ORDER BY p.folio;
