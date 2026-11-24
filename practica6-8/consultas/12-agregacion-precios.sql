-- PREGUNTA: Para los modelos HYVOLT II y HYGOLD 5000BS, ¿cuántas presentaciones tiene cada uno y cuáles son su costo unitario promedio, precio mínimo y precio máximo?
-- ALGEBRA: P_dos_modelos = sigma modeloproducto = 'HYVOLT II' or modeloproducto = 'HYGOLD 5000BS' (producto); gamma modeloproducto; count(claveproducto)->presentaciones, avg(costounitariousd)->costo_promedio, min(preciounitariousd)->precio_min, max(preciounitariousd)->precio_max (P_dos_modelos)

SELECT
  modeloproducto,
  COUNT(claveproducto) AS presentaciones,
  ROUND(AVG(costounitariousd), 2) AS costo_promedio,
  MIN(preciounitariousd) AS precio_min,
  MAX(preciounitariousd) AS precio_max
FROM producto
WHERE modeloproducto IN ('HYVOLT II', 'HYGOLD 5000BS')
GROUP BY modeloproducto
ORDER BY modeloproducto;
