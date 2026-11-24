-- PREGUNTA: ¿Qué números de cliente (entre los clientes 1001, 1002, 1004 y 1052) son clientes nacionales y además tienen registrada una segunda sucursal con clave S02?
-- ALGEBRA: C_nac = pi numerocliente (sigma tipocliente = 'NACIONAL' and (numerocliente = 1001 or numerocliente = 1002 or numerocliente = 1004 or numerocliente = 1052) (cliente)); C_s02 = pi numerocliente (sigma clavesucursal = 'S02' and (numerocliente = 1001 or numerocliente = 1002 or numerocliente = 1004 or numerocliente = 1052) (sucursal)); C_nac intersect C_s02

SELECT numerocliente
FROM cliente
WHERE tipocliente = 'NACIONAL'
  AND numerocliente IN (1001, 1002, 1004, 1052)
INTERSECT
SELECT numerocliente
FROM sucursal
WHERE clavesucursal = 'S02'
  AND numerocliente IN (1001, 1002, 1004, 1052)
ORDER BY numerocliente;
