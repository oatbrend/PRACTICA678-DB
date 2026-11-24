-- PREGUNTA: ¿Qué modelos comerciales del catálogo pertenecen a las líneas especializadas HYPRENE o HYVOLT?
-- ALGEBRA: pi modeloproducto, tipoproducto (sigma tipoproducto = 'HYPRENE' or tipoproducto = 'HYVOLT' (modelo_producto))

SELECT DISTINCT
  modeloproducto,
  tipoproducto
FROM modelo_producto
WHERE tipoproducto = 'HYPRENE' OR tipoproducto = 'HYVOLT'
ORDER BY modeloproducto;
