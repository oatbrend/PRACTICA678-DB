-- PREGUNTA: ¿Qué combinaciones genera el producto cartesiano sin filtro entre los modelos HYVOLT II y HYPRENE BO150 y las presentaciones HV2-04 y HPB-04, demostrando por qué casi nunca se usa solo?
-- ALGEBRA: M_dos = rho m (pi modeloproducto, tipoproducto (sigma modeloproducto = 'HYVOLT II' or modeloproducto = 'HYPRENE BO150' (modelo_producto))); P_dos = rho p (pi claveproducto, modeloproducto, preciounitariousd (sigma claveproducto = 'HV2-04' or claveproducto = 'HPB-04' (producto))); M_dos cross join P_dos

SELECT
  m.modeloproducto AS m_modeloproducto,
  m.tipoproducto,
  p.claveproducto,
  p.modeloproducto AS p_modeloproducto,
  p.preciounitariousd
FROM (
  SELECT modeloproducto, tipoproducto
  FROM modelo_producto
  WHERE modeloproducto IN ('HYVOLT II', 'HYPRENE BO150')
) AS m
CROSS JOIN (
  SELECT claveproducto, modeloproducto, preciounitariousd
  FROM producto
  WHERE claveproducto IN ('HV2-04', 'HPB-04')
) AS p
ORDER BY m.modeloproducto, p.claveproducto;
