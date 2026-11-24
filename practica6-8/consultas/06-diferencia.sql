-- PREGUNTA: ¿Cuáles de los clientes 1001, 1002, 1008 y 1026 no realizaron ningún pedido dentro de los primeros cuatro folios del año (folio <= 100004)?
-- ALGEBRA: C_sel = pi numerocliente (sigma numerocliente = 1001 or numerocliente = 1002 or numerocliente = 1008 or numerocliente = 1026 (cliente)); P_cuatro = pi numerocliente (sigma folio <= 100004 (pedido)); C_sel - P_cuatro

SELECT numerocliente
FROM cliente
WHERE numerocliente IN (1001, 1002, 1008, 1026)
EXCEPT
SELECT numerocliente
FROM pedido
WHERE folio <= 100004
ORDER BY numerocliente;
