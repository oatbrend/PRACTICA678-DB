# Trabajo Individual — Brenda Roa Venegas

**Integrante:** Brenda Roa Venegas  
**Grupo:** 3BV1 — Ingeniería en Inteligencia Artificial (ESCOM - IPN)

---

## 1. Tres consultas propias en álgebra relacional y SQL

Estas tres consultas son distintas a las del equipo y a las de mi compañero, e incluyen una consulta con **división ($\div$)** y una con **reunión externa ($\)**. Fueron comprobadas en RelaX (`grupo.txt`) y en PostgreSQL (`ventas_industriales`).

---

### Consulta Individual 1 — División ($\div$)

1. **Pregunta del dominio:** ¿Qué pedidos (`folio`) han incluido **todos** los productos cuyo proveedor de transporte es `'Tres Guerras Logística'` (`HPB-03` y `HPB-04`)?
2. **Expresión en álgebra relacional:**
   $$R_{\text{det}} \leftarrow \pi_{\text{folio, claveproducto}}(\text{detalle})$$
   $$S_{\text{prov}} \leftarrow \pi_{\text{claveproducto}}\big(\sigma_{\text{provtransporte} = \text{'Tres Guerras Logística'}}(\text{producto})\big)$$
   $$\text{Resultado} \leftarrow R_{\text{det}} \div S_{\text{prov}}$$
   **En RelaX:**
   ```text
   R_det = pi folio, claveproducto (detalle)
   S_prov = pi claveproducto (sigma provtransporte = 'Tres Guerras Logística' (producto))
   R_det / S_prov
   ```
3. **Árbol y resultado en RelaX ([captura](../evidencias/relax-bren-q1.svg)):**
   ```text
                 ÷
         ┌───────┴───────┐
   π folio, claveprod  π claveproducto
         │               │
      detalle          σ provtransporte = 'Tres Guerras Logística'
                         │
                      producto
   ```
   | folio |
   | ---: |
   | 100136 |
   | 100245 |
4. **Consulta SQL equivalente y comprobación:**
   ```sql
   SELECT d.folio
   FROM detalle AS d
   WHERE d.claveproducto IN (
     SELECT claveproducto FROM producto WHERE provtransporte = 'Tres Guerras Logística'
   )
   GROUP BY d.folio
   HAVING COUNT(DISTINCT d.claveproducto) = (
     SELECT COUNT(*) FROM producto WHERE provtransporte = 'Tres Guerras Logística'
   )
   ORDER BY d.folio;
   ```
   *Comprobación:* Devuelve exactamente los mismos **2 folios** (`100136` y `100245`) tanto en RelaX como en PostgreSQL.

---

### Consulta Individual 2 — Reunión externa izquierda ($\)

1. **Pregunta del dominio:** Para los clientes `1001`, `1002`, `1008` y `1026`, ¿qué pedidos dentro de los primeros cuatro folios (`folio <= 100004`) han realizado, conservando con `NULL` a los clientes que no tienen pedidos en ese bloque?
2. **Expresión en álgebra relacional:**
   $$C_{\text{cuatro}} \leftarrow \pi_{\text{numerocliente, razonsocial}}\big(\sigma_{\text{numerocliente} \in \{1001, 1002, 1008, 1026\}}(\text{cliente})\big)$$
   $$P_{\text{cuatro}} \leftarrow \pi_{\text{numerocliente, folio, estatus}}\big(\sigma_{\text{folio} \le 100004}(\text{pedido})\big)$$
   $$\text{Resultado} \leftarrow C_{\text{cuatro}} \ P_{\text{cuatro}}$$
   **En RelaX:**
   ```text
   C_cuatro = pi numerocliente, razonsocial (sigma numerocliente = 1001 or numerocliente = 1002 or numerocliente = 1008 or numerocliente = 1026 (cliente))
   P_cuatro = pi numerocliente, folio, estatus (sigma folio <= 100004 (pedido))
   C_cuatro left outer join P_cuatro
   ```
3. **Árbol y resultado en RelaX ([captura](../evidencias/relax-bren-q2.svg)):**
   ```text
            ⟕ (left outer join por numerocliente)
            ├── π numerocliente, razonsocial (σ ... (cliente))
            └── π numerocliente, folio, estatus (σ folio ≤ 100004 (pedido))
   ```
   | numerocliente | razonsocial | folio | estatus |
   | ---: | :--- | ---: | :--- |
   | 1001 | `Distribuidora Metrópoli S.A.B. de C.V.` | `null` | `null` |
   | 1002 | `Eléctrica Nova S.A. de C.V.` | `null` | `null` |
   | 1008 | `Manufacturas Cobalto S.A.P.I. de C.V.` | 100004 | `ENTREGADO` |
   | 1026 | `Energía Nexus S.A.P.I. de C.V.` | 100001 | `ENTREGADO` |
4. **Consulta SQL equivalente y comprobación:**
   ```sql
   SELECT c.numerocliente, c.razonsocial, p.folio, p.estatus
   FROM (
     SELECT numerocliente, razonsocial FROM cliente
     WHERE numerocliente IN (1001, 1002, 1008, 1026)
   ) AS c
   LEFT JOIN (
     SELECT numerocliente, folio, estatus FROM pedido
     WHERE folio <= 100004
   ) AS p ON c.numerocliente = p.numerocliente
   ORDER BY c.numerocliente;
   ```
   *Comprobación:* Devuelve las mismas **4 filas** en PostgreSQL y en RelaX, mostrando cómo `1001` y `1002` se conservan con `NULL` gracias al `LEFT OUTER JOIN`.

---

### Consulta Individual 3 — Selección, Reunión Natural y Proyección sobre la ubicación normalizada ($\sigma, \bowtie, \pi$)

1. **Pregunta del dominio:** ¿Cuál es la clave de sucursal, nombre de la planta, ciudad, estado y país de las sucursales `'S01'`, `'S02'` y `'S03'` del cliente `1004`?
2. **Expresión en álgebra relacional:**
   $$S_{1004} \leftarrow \sigma_{\text{numerocliente} = 1004 \;\land\; \text{clavesucursal} \in \{\text{'S01'}, \text{'S02'}, \text{'S03'}\}}(\text{sucursal})$$
   $$S_{\text{geo}} \leftarrow (S_{1004} \bowtie \text{ciudad\_ubicacion}) \bowtie \text{estado\_ubicacion}$$
   $$\text{Resultado} \leftarrow \pi_{\text{clavesucursal, nombreplanta, ciudad, estado, pais}}(S_{\text{geo}})$$
   **En RelaX:**
   ```text
   S_1004 = sigma numerocliente = 1004 and (clavesucursal = 'S01' or clavesucursal = 'S02' or clavesucursal = 'S03') (sucursal)
   S_geo = (S_1004 natural join ciudad_ubicacion) natural join estado_ubicacion
   pi clavesucursal, nombreplanta, ciudad, estado, pais (S_geo)
   ```
3. **Árbol y resultado en RelaX ([captura](../evidencias/relax-bren-q3.svg)):**
   ```text
   π clavesucursal, nombreplanta, ciudad, estado, pais
     │
     ⋈ (natural join por estado)
     ├── ⋈ (natural join por ciudad)
     │   ├── σ numerocliente = 1004 ∧ clavesucursal ∈ {'S01','S02','S03'} (sucursal)
     │   └── ciudad_ubicacion
     └── estado_ubicacion
   ```
   | clavesucursal | nombreplanta | ciudad | estado | pais |
   | :--- | :--- | :--- | :--- | :--- |
   | `S01` | `Unidad Productiva Aguascalientes II` | `Aguascalientes` | `Aguascalientes` | `México` |
   | `S02` | `Unidad Productiva Lázaro Cárdenas III` | `Lázaro Cárdenas` | `Michoacán` | `México` |
   | `S03` | `Planta Veracruz III` | `Veracruz` | `Veracruz` | `México` |
4. **Consulta SQL equivalente y comprobación:**
   ```sql
   SELECT s.clavesucursal, s.nombreplanta, s.ciudad, c.estado, e.pais
   FROM sucursal AS s
   NATURAL JOIN ciudad_ubicacion AS c
   NATURAL JOIN estado_ubicacion AS e
   WHERE s.numerocliente = 1004
     AND s.clavesucursal IN ('S01', 'S02', 'S03')
   ORDER BY s.clavesucursal;
   ```
   *Comprobación:* Devuelve exactamente las mismas **3 filas** en PostgreSQL y en RelaX, comprobando además en la práctica que la reunión natural entre `sucursal`, `ciudad_ubicacion` y `estado_ubicacion` reconstruye la dirección completa sin pérdida.

---

## 2. Explicación con mis propias palabras de una descomposición de la Parte 1

### Descomposición elegida: Normalización de la tabla `sucursal` (de 1FN a 2FN y 3FN / BCNF)

En el diseño anterior, la tabla `sucursal` tenía una clave primaria compuesta por dos columnas: `(numeroCliente, claveSucursal)`, ya que una sucursal es una entidad débil y claves como `'S01'` se repiten en distintos clientes. En esa misma tabla guardábamos todos los datos de la dirección: `calle`, `numero`, `CP`, `ciudad`, `estado` y `pais`.

Al analizar las dependencias funcionales vimos dos problemas:
1. **Violaba 2FN (dependencia parcial):** En ERGON un cliente nacional solo tiene plantas en México y un cliente de exportación recibe en su único país receptor. Eso significa que con saber solo el `numeroCliente` (una mitad de la clave primaria compuesta) ya sabíamos qué `pais` tenía la sucursal (`numeroCliente -> pais`). Que una columna que no es clave dependa solo de un pedazo de la clave primaria compuesta es una dependencia parcial y nos dejaba en **1FN**.
2. **Violaba 3FN (dependencias transitivas):** La clave completa `(numeroCliente, claveSucursal)` determinaba la `ciudad` de la planta, pero a su vez cada `ciudad` determina a qué `estado` pertenece (`ciudad -> estado`) y cada `estado` determina a qué `pais` pertenece (`estado -> pais`). Como en la base hay 100 sucursales repartidas en 51 ciudades y 31 estados, estábamos repitiendo varias veces que Guadalajara o Tlaquepaque están en Jalisco y que Jalisco está en México.

**¿Cómo la normalizamos paso a paso?**
* **Paso 1:** Separamos `estado -> pais` en la tabla **`estado_ubicacion(estado [PK], pais)`** y quitamos `pais` de `sucursal`. Al quitar `pais` de `sucursal`, desapareció también la dependencia parcial `numeroCliente -> pais` y la tabla subió a **2FN**.
* **Paso 2:** Separamos `ciudad -> estado` en la tabla **`ciudad_ubicacion(ciudad [PK], estado [FK])`** y quitamos `estado` de `sucursal`, dejando `ciudad` en `sucursal` como llave foránea hacia `ciudad_ubicacion`.

Así nos quedaron tres tablas (`estado_ubicacion`, `ciudad_ubicacion` y `sucursal`) donde toda columna depende únicamente de la clave primaria completa de su tabla (**3FN y BCNF**). Como demostré en mi Consulta Individual 3, cuando hacemos `sucursal NATURAL JOIN ciudad_ubicacion NATURAL JOIN estado_ubicacion` recuperamos exactamente el estado y país de cada planta sin que aparezca ninguna fila falsa (reunión sin pérdida), porque las columnas puente (`ciudad` y `estado`) son claves primarias de las tablas nuevas.
