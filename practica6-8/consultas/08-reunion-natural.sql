-- PREGUNTA: ¿A qué línea comercial (tipoproducto) pertenece cada presentación cuyo costo unitario de producción supera los 2,000 USD?
-- ALGEBRA: P_caros = sigma costounitariousd > 2000 (producto); pi claveproducto, modeloproducto, tipoproducto, costounitariousd, preciounitariousd (P_caros natural join modelo_producto)

SELECT DISTINCT
  claveproducto,
  modeloproducto,
  tipoproducto,
  costounitariousd,
  preciounitariousd
FROM producto
NATURAL JOIN modelo_producto
WHERE costounitariousd > 2000
ORDER BY claveproducto;
