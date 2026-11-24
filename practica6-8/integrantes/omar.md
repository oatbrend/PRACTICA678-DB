# Trabajo Individual — Omar Flores Olivares

**Integrante:** Omar Flores Olivares  
**Grupo:** 3BV1 — Ingeniería en Inteligencia Artificial (ESCOM - IPN)

---

## 1. Tres consultas propias en álgebra relacional y SQL

Estas tres consultas no repiten las del equipo e incluyen una consulta con **división ($\div$)** y una con **reunión externa ($\)**. Fueron verificadas tanto en RelaX (`grupo.txt`) como en PostgreSQL (`ventas_industriales`).

---

### Consulta Individual 1 — División ($\div$)

1. **Pregunta del dominio:** ¿Qué clientes (`numerocliente`) han comprado **todas** las presentaciones del modelo `'HYPRENE BO150'` (`HPB-01`, `HPB-02`, `HPB-03` y `HPB-04`)?
2. **Expresión en álgebra relacional:**
   $$\text{ComprasCliente} \leftarrow \pi_{\text{numerocliente, claveproducto}}\big(\text{pedido} \bowtie \text{detalle}\big)$$
   $$\text{ProductosBO150} \leftarrow \pi_{\text{claveproducto}}\big(\sigma_{\text{modeloproducto} = \text{'HYPRENE BO150'}}(\text{producto})\big)$$
   $$\text{Resultado} \leftarrow \text{ComprasCliente} \div \text{ProductosBO150}$$
   **En RelaX:**
   ```text
   ComprasCliente = pi numerocliente, claveproducto (pedido natural join detalle)
   ProductosBO150 = pi claveproducto (sigma modeloproducto = 'HYPRENE BO150' (producto))
   ComprasCliente / ProductosBO150
   ```
3. **Árbol y resultado en RelaX ([captura](../evidencias/relax-omar-q1.svg)):**
   ```text
                    ÷
          ┌─────────┴─────────┐
   π numerocliente,     π claveproducto
     claveproducto            │
          │             σ modeloproducto = 'HYPRENE BO150'
          ⋈                   │
       ┌──┴──┐             producto
    pedido detalle
   ```
   | numerocliente |
   | ---: |
   | 1037 |
4. **Consulta SQL equivalente y comprobación:**
   ```sql
   SELECT p.numerocliente
   FROM pedido AS p
   JOIN detalle AS d ON p.folio = d.folio
   WHERE d.claveproducto IN (
     SELECT claveproducto FROM producto WHERE modeloproducto = 'HYPRENE BO150'
   )
   GROUP BY p.numerocliente
   HAVING COUNT(DISTINCT d.claveproducto) = (
     SELECT COUNT(*) FROM producto WHERE modeloproducto = 'HYPRENE BO150'
   )
   ORDER BY p.numerocliente;
   ```
   *Comprobación:* Tanto en RelaX como en PostgreSQL devuelve únicamente al cliente **`1037`** (adquirió `HPB-03` y `HPB-04` en el folio `100136`, y `HPB-01` y `HPB-02` en el folio `100281`).

---

### Consulta Individual 2 — Reunión externa izquierda ($\)

1. **Pregunta del dominio:** Para los transportistas `'TR001'`, `'TR002'`, `'TR012'` y `'TR030'`, ¿qué envíos de los primeros cuatro pedidos (`folio <= 100004`) han ejecutado, conservando con `NULL` a los transportistas sin envíos en ese bloque?
2. **Expresión en álgebra relacional:**
   $$T_{\text{sel}} \leftarrow \pi_{\text{clavetransportista, nombreempresa}}\big(\sigma_{\text{clavetransportista} \in \{\text{'TR001'}, \text{'TR002'}, \text{'TR012'}, \text{'TR030'}\}}(\text{transportista})\big)$$
   $$E_{\text{cuatro}} \leftarrow \pi_{\text{clavetransportista, numeroguia, folio, costoflete}}\big(\sigma_{\text{folio} \le 100004}(\text{envio})\big)$$
   $$\text{Resultado} \leftarrow T_{\text{sel}} \ E_{\text{cuatro}}$$
   **En RelaX:**
   ```text
   T_sel = pi clavetransportista, nombreempresa (sigma clavetransportista = 'TR001' or clavetransportista = 'TR002' or clavetransportista = 'TR012' or clavetransportista = 'TR030' (transportista))
   E_cuatro = pi clavetransportista, numeroguia, folio, costoflete (sigma folio <= 100004 (envio))
   T_sel left outer join E_cuatro
   ```
3. **Árbol y resultado en RelaX ([captura](../evidencias/relax-omar-q2.svg)):**
   ```text
            ⟕ (left outer join por clavetransportista)
            ├── π clavetransportista, nombreempresa (σ ... (transportista))
            └── π clavetransportista, numeroguia, folio, costoflete (σ folio ≤ 100004 (envio))
   ```
   | clavetransportista | nombreempresa | numeroguia | folio | costoflete |
   | :--- | :--- | :--- | ---: | ---: |
   | `TR001` | `Logística Unidos S.A. de C.V.` | `null` | `null` | `null` |
   | `TR002` | `Express Peninsular S.A. de C.V.` | `null` | `null` | `null` |
   | `TR012` | `Transportes del Pacífico S.A. de C.V.` | `GU309405377382` | 100002 | 178.59 |
   | `TR030` | `Distribución Peninsular S.A. de C.V.` | `GU937557166733` | 100001 | 3982.88 |
4. **Consulta SQL equivalente y comprobación:**
   ```sql
   SELECT t.clavetransportista, t.nombreempresa, e.numeroguia, e.folio, e.costoflete
   FROM (
     SELECT clavetransportista, nombreempresa FROM transportista
     WHERE clavetransportista IN ('TR001', 'TR002', 'TR012', 'TR030')
   ) AS t
   LEFT JOIN (
     SELECT clavetransportista, numeroguia, folio, costoflete FROM envio
     WHERE folio <= 100004
   ) AS e ON t.clavetransportista = e.clavetransportista
   ORDER BY t.clavetransportista;
   ```
   *Comprobación:* Devuelve las mismas **4 filas** en PostgreSQL y en RelaX, conservando a `TR001` y `TR002` con `NULL`.

---

### Consulta Individual 3 — Reunión natural y Agrupación ($\bowtie$ y $\gamma$)

1. **Pregunta del dominio:** Entre los modelos `'HYVOLT II'` y `'HYPRENE BO150'`, ¿cuántas presentaciones corresponden a cada línea comercial (`tipoproducto`) y cuál es la suma y el promedio de sus precios unitarios de lista?
2. **Expresión en álgebra relacional:**
   $$P_{\text{sel}} \leftarrow \sigma_{\text{modeloproducto} = \text{'HYVOLT II'} \lor \text{modeloproducto} = \text{'HYPRENE BO150'}}(\text{producto})$$
   $$P_{\text{linea}} \leftarrow P_{\text{sel}} \bowtie \text{modelo\_producto}$$
   $$\text{Resultado} \leftarrow \gamma_{\text{tipoproducto};\; \text{count}(\text{claveproducto}) \to \text{total\_productos},\; \text{sum}(\text{preciounitariousd}) \to \text{suma\_precios},\; \text{avg}(\text{preciounitariousd}) \to \text{promedio\_precio}}(P_{\text{linea}})$$
   **En RelaX:**
   ```text
   P_sel = sigma modeloproducto = 'HYVOLT II' or modeloproducto = 'HYPRENE BO150' (producto)
   P_linea = P_sel natural join modelo_producto
   gamma tipoproducto; count(claveproducto)->total_productos, sum(preciounitariousd)->suma_precios, avg(preciounitariousd)->promedio_precio (P_linea)
   ```
3. **Árbol y resultado en RelaX ([captura](../evidencias/relax-omar-q3.svg)):**
   ```text
   γ tipoproducto; count(claveproducto)→total_productos, sum(...)→suma_precios, avg(...)→promedio_precio
     │
     ⋈ (natural join por modeloproducto)
     ├── σ modeloproducto = 'HYVOLT II' ∨ modeloproducto = 'HYPRENE BO150' (producto)
     └── modelo_producto
   ```
   | tipoproducto | total_productos | suma_precios | promedio_precio |
   | :--- | ---: | ---: | ---: |
   | `HYPRENE` | 4 | 815.87 | 203.97 |
   | `HYVOLT` | 4 | 13413.82 | 3353.45 |
4. **Consulta SQL equivalente y comprobación:**
   ```sql
   SELECT m.tipoproducto,
          COUNT(p.claveproducto) AS total_productos,
          ROUND(SUM(p.preciounitariousd), 2) AS suma_precios,
          ROUND(AVG(p.preciounitariousd), 2) AS promedio_precio
   FROM producto AS p
   NATURAL JOIN modelo_producto AS m
   WHERE p.modeloproducto IN ('HYVOLT II', 'HYPRENE BO150')
   GROUP BY m.tipoproducto
   ORDER BY m.tipoproducto;
   ```
   *Comprobación:* Devuelve las mismas **2 filas** en PostgreSQL y en RelaX.

---

## 2. Explicación con mis propias palabras de una descomposición de la Parte 1

### Descomposición elegida: Normalización de la tabla `producto` (de 2FN a 3FN / BCNF)

En nuestro esquema original de las Prácticas 4 y 5, la tabla `producto` tenía como clave primaria únicamente a `claveProducto` (por ejemplo, `'HV2-01'`, `'HV2-02'`, etc.). Como la clave primaria era una sola columna, la tabla ya estaba en **Segunda Forma Normal (2FN)** porque es imposible que un atributo dependa de "la mitad" de una clave de una sola columna.

El problema apareció porque en la misma tabla guardábamos tanto el modelo comercial (`modeloProducto`, como `'HYVOLT II'`) como la línea o familia del producto (`tipoProducto`, como `'HYVOLT'`). Según las reglas de negocio de ERGON, cada modelo pertenece siempre a una misma línea comercial (`modeloProducto -> tipoProducto`). Como cada modelo tiene 4 presentaciones distintas en el catálogo, estábamos repitiendo 4 veces seguidas que `'HYVOLT II'` es de tipo `'HYVOLT'`, que `'HYGOLD 100'` es de tipo `'OMNIGOLD'`, etc.

En términos de normalización, eso es una **dependencia transitiva** (`claveProducto -> modeloProducto -> tipoProducto`): la clave determina al modelo, y el modelo (sin ser clave de la tabla) determina al tipo de producto. Eso violaba la **Tercera Forma Normal (3FN)** y nos causaba anomalías muy claras: si queríamos dar de alta un modelo nuevo en el catálogo, no podíamos hacerlo sin inventarle primero un producto con precio y costo; y si borrábamos las 4 presentaciones de un modelo, se perdía de la base a qué línea pertenecía ese modelo.

**¿Cómo lo resolvimos?**  
Aplicamos la regla para eliminar dependencias transitivas:
1. Sacamos la regla `modeloProducto -> tipoProducto` a una tabla nueva llamada **`modelo_producto(modeloProducto [PK], tipoProducto)`**, donde cada uno de los 10 modelos se registra una sola vez junto con su línea.
2. En la tabla **`producto`** borramos la columna `tipoProducto` y dejamos `modeloProducto` como llave foránea apuntando a `modelo_producto`.

Con esto, en ambas tablas el único determinante es su propia clave primaria (quedando en **3FN y BCNF**), no se pierde ninguna dependencia funcional y la unión entre las dos tablas es **sin pérdida** porque la columna que tienen en común (`modeloProducto`) es la clave primaria de `modelo_producto`.
