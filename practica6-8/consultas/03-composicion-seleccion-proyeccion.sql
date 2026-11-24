-- PREGUNTA: ¿Cuál es el número de cliente, razón social, RFC y estado de origen de los clientes nacionales con número de cliente entre 1001 y 1004?
-- ALGEBRA: pi numerocliente, razonsocial, rfc, estadoorigen (sigma tipocliente = 'NACIONAL' and numerocliente <= 1004 (cliente))

SELECT DISTINCT
  numerocliente,
  razonsocial,
  rfc,
  estadoorigen
FROM cliente
WHERE tipocliente = 'NACIONAL'
  AND numerocliente <= 1004
ORDER BY numerocliente;
