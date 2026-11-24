-- PREGUNTA: ¿Cuántos modelos comerciales están registrados en cada línea de producto (tipoproducto)?
-- ALGEBRA: gamma tipoproducto; count(modeloproducto)->total_modelos (modelo_producto)

SELECT
  tipoproducto,
  COUNT(modeloproducto) AS total_modelos
FROM modelo_producto
GROUP BY tipoproducto
ORDER BY tipoproducto;
