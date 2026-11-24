-- PREGUNTA: ¿Qué pedidos (folio) han incluido TODOS los productos cuyo proveedor de transporte es Tráileres Monterrey (HPB-02 y HPL-01)?
-- ALGEBRA: R = pi folio, claveproducto (detalle); S = pi claveproducto (sigma provtransporte = 'Tráileres Monterrey' (producto)); R / S

SELECT d.folio
FROM detalle AS d
WHERE d.claveproducto IN (
  SELECT claveproducto
  FROM producto
  WHERE provtransporte = 'Tráileres Monterrey'
)
GROUP BY d.folio
HAVING COUNT(DISTINCT d.claveproducto) = (
  SELECT COUNT(DISTINCT claveproducto)
  FROM producto
  WHERE provtransporte = 'Tráileres Monterrey'
)
ORDER BY d.folio;
