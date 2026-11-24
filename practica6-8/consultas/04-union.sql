-- PREGUNTA: ¿Cuáles son las claves y modelos de los productos que pertenecen al modelo HYVOLT II o al modelo HYPRENE BO150?
-- ALGEBRA: P_hyvolt = pi claveproducto, modeloproducto (sigma modeloproducto = 'HYVOLT II' (producto)); P_hyprene = pi claveproducto, modeloproducto (sigma modeloproducto = 'HYPRENE BO150' (producto)); P_hyvolt union P_hyprene

SELECT claveproducto, modeloproducto
FROM producto
WHERE modeloproducto = 'HYVOLT II'
UNION
SELECT claveproducto, modeloproducto
FROM producto
WHERE modeloproducto = 'HYPRENE BO150'
ORDER BY claveproducto;
