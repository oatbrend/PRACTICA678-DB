-- Migración 002: Fortalecer la relación entre envío, pedido y cliente (Práctica 5)
BEGIN;

ALTER TABLE pedido
  ADD CONSTRAINT uq_pedido_folio_cliente UNIQUE (folio, numerocliente);

ALTER TABLE envio
  DROP CONSTRAINT fk_envio_pedido;

ALTER TABLE envio
  ADD CONSTRAINT fk_envio_pedido_cliente
  FOREIGN KEY (folio, numerocliente)
  REFERENCES pedido (folio, numerocliente)
  ON DELETE RESTRICT
  ON UPDATE CASCADE;

COMMIT;
