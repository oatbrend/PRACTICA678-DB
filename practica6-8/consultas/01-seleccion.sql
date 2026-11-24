-- PREGUNTA: ¿Cuáles son las claves, modelos, costos y precios de lista de los productos cuyo costo unitario de producción supera los 1,850 USD?
-- ALGEBRA: pi claveproducto, modeloproducto, costounitariousd, preciounitariousd (sigma costounitariousd > 1850 (producto))

SELECT DISTINCT
  claveproducto,
  modeloproducto,
  costounitariousd,
  preciounitariousd
FROM producto
WHERE costounitariousd > 1850
ORDER BY claveproducto;
