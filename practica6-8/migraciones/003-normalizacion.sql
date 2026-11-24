-- Migración 003: Normalización de producto y sucursal a 3FN / BCNF (Prácticas 6, 7 y 8)
-- Mueve los renglones existentes de la base poblada a las tablas nuevas sin recargar a mano.

BEGIN;

-- 1. Normalización de producto: crear modelo_producto y mover los 10 modelos
CREATE TABLE modelo_producto (
  modeloproducto VARCHAR(30) NOT NULL,
  tipoproducto   VARCHAR(10) NOT NULL,
  CONSTRAINT pk_modelo_producto PRIMARY KEY (modeloproducto),
  CONSTRAINT ck_modelo_producto_catalogo CHECK (modeloproducto IN (
    'HYGOLD 100',
    'HYGOLD 5000BS',
    'HYGOLD L-2000',
    'HYPRENE BO150',
    'HYPRENE L2000',
    'HYPRENE P150 BS',
    'HYVOLT II',
    'OMNIGOLD A12',
    'OMNIGOLD P100N',
    'OMNIGOLD P220N'
  )),
  CONSTRAINT ck_modelo_tipo_producto CHECK (tipoproducto IN ('OMNIGOLD', 'HYVOLT', 'HYPRENE')),
  CONSTRAINT ck_modelo_correspondencia_tipo CHECK (
    ((modeloproducto LIKE 'HYGOLD%' OR modeloproducto LIKE 'OMNIGOLD%')
      AND tipoproducto = 'OMNIGOLD')
    OR (modeloproducto LIKE 'HYVOLT%' AND tipoproducto = 'HYVOLT')
    OR (modeloproducto LIKE 'HYPRENE%' AND tipoproducto = 'HYPRENE')
  )
);

INSERT INTO modelo_producto (modeloproducto, tipoproducto)
SELECT DISTINCT modeloproducto, tipoproducto
FROM producto
ORDER BY modeloproducto;

ALTER TABLE producto
  ADD CONSTRAINT fk_producto_modelo
  FOREIGN KEY (modeloproducto)
  REFERENCES modelo_producto (modeloproducto)
  ON DELETE RESTRICT
  ON UPDATE CASCADE;

ALTER TABLE producto DROP CONSTRAINT ck_producto_modelo_tipo;
ALTER TABLE producto DROP CONSTRAINT ck_producto_modelo;
ALTER TABLE producto DROP CONSTRAINT ck_subtipo_producto;
ALTER TABLE producto DROP CONSTRAINT ck_tipo_producto;

ALTER TABLE producto
  ADD CONSTRAINT ck_subtipo_producto_por_modelo CHECK (
    ((modeloproducto LIKE 'HYGOLD%' OR modeloproducto LIKE 'OMNIGOLD%')
      AND provmaquinaria IS NOT NULL
      AND provtransformador IS NULL
      AND provtransporte IS NULL)
    OR
    (modeloproducto LIKE 'HYVOLT%'
      AND provtransformador IS NOT NULL
      AND provmaquinaria IS NULL
      AND provtransporte IS NULL)
    OR
    (modeloproducto LIKE 'HYPRENE%'
      AND provtransporte IS NOT NULL
      AND provmaquinaria IS NULL
      AND provtransformador IS NULL)
  );

ALTER TABLE producto DROP COLUMN tipoproducto;

-- 2. Normalización de sucursal: crear estado_ubicacion (31 estados) y ciudad_ubicacion (51 ciudades)
CREATE TABLE estado_ubicacion (
  estado VARCHAR(60) NOT NULL,
  pais   VARCHAR(60) NOT NULL,
  CONSTRAINT pk_estado_ubicacion PRIMARY KEY (estado)
);

INSERT INTO estado_ubicacion (estado, pais)
SELECT DISTINCT estado, pais
FROM sucursal
WHERE estado IS NOT NULL AND pais IS NOT NULL
ORDER BY estado;

CREATE TABLE ciudad_ubicacion (
  ciudad VARCHAR(60) NOT NULL,
  estado VARCHAR(60) NOT NULL,
  CONSTRAINT pk_ciudad_ubicacion PRIMARY KEY (ciudad),
  CONSTRAINT fk_ciudad_estado FOREIGN KEY (estado)
    REFERENCES estado_ubicacion (estado)
    ON DELETE RESTRICT
    ON UPDATE CASCADE
);

INSERT INTO ciudad_ubicacion (ciudad, estado)
SELECT DISTINCT ciudad, estado
FROM sucursal
WHERE ciudad IS NOT NULL AND estado IS NOT NULL
ORDER BY ciudad;

ALTER TABLE sucursal ALTER COLUMN ciudad SET NOT NULL;

ALTER TABLE sucursal
  ADD CONSTRAINT fk_sucursal_ciudad
  FOREIGN KEY (ciudad)
  REFERENCES ciudad_ubicacion (ciudad)
  ON DELETE RESTRICT
  ON UPDATE CASCADE;

ALTER TABLE sucursal DROP COLUMN estado;
ALTER TABLE sucursal DROP COLUMN pais;

DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'usuario_app') THEN
    GRANT SELECT, INSERT, UPDATE, DELETE ON modelo_producto, estado_ubicacion, ciudad_ubicacion TO usuario_app;
  END IF;
END
$$;

COMMIT;
