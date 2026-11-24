# Parte 2. Álgebra relacional

## Ejercicio 2.1. Sus datos en RelaX

El script [`practica6-8/relax/exportar-grupo.py`](./relax/exportar-grupo.py) se conecta a la base normalizada en PostgreSQL (o lee el archivo semilla si el contenedor aún no está levantado) y regenera automáticamente el archivo [`practica6-8/relax/grupo.txt`](./relax/grupo.txt) con una muestra de **10 a 30 renglones por tabla** conservando el 100% de la integridad referencial:

| Tabla normalizada | Renglones en `grupo.txt` | Clave primaria / Integridad referencial verificada |
| :--- | :---: | :--- |
| `modelo_producto` | 10 | PK `(modeloproducto)` |
| `producto` | 19 | PK `(claveproducto)`, FK `modeloproducto -> modelo_producto` |
| `cliente` | 14 | PK `(numerocliente)` |
| `estado_ubicacion` | 16 | PK `(estado)` |
| `ciudad_ubicacion` | 17 | PK `(ciudad)`, FK `estado -> estado_ubicacion` |
| `sucursal` | 20 | PK `(numerocliente, clavesucursal)`, FKs a `cliente` y `ciudad_ubicacion` |
| `transportista` | 15 | PK `(clavetransportista)` |
| `pedido` | 15 | PK `(folio)`, FK `numerocliente -> cliente` |
| `detalle` | 28 | PK `(folio, claveparcial)`, FKs a `pedido` y `producto` |
| `envio` | 12 | PK `(numeroguia)`, FKs a `pedido`, `transportista` y `sucursal` |

Comando para regenerar el grupo en cualquier momento:
```bash
python practica6-8/relax/exportar-grupo.py
```

---

## Ejercicio 2.2. Consultas en álgebra sobre el proyecto propio (ERGON)

Todas las consultas fueron probadas tanto en **RelaX** (cargando `grupo.txt` en el *Group Editor*) como en **PostgreSQL 17**, devolviendo exactamente las mismas filas en ambos entornos.

---

### A) Selección ($\sigma$) y Proyección ($\pi$) — 3 consultas

#### Consulta 1 (`01-seleccion.sql`)
1. **Pregunta del dominio:** ¿Cuáles son las claves, modelos, costos y precios de lista de los productos cuyo costo unitario de producción supera los 1,850 USD?
2. **Expresión en álgebra relacional:**
   $$\pi_{\text{claveproducto, modeloproducto, costounitariousd, preciounitariousd}}\big(\sigma_{\text{costounitariousd} > 1850}(\text{producto})\big)$$
   **En RelaX:**
   ```text
   pi claveproducto, modeloproducto, costounitariousd, preciounitariousd (
     sigma costounitariousd > 1850 (producto)
   )
   ```
3. **Árbol y resultado en RelaX ([captura](./evidencias/relax-q01.svg)):**
   ```text
   π claveproducto, modeloproducto, costounitariousd, preciounitariousd
     │
   σ costounitariousd > 1850
     │
   producto
   ```
   | claveproducto | modeloproducto | costounitariousd | preciounitariousd |
   | :--- | :--- | ---: | ---: |
   | `HG5-04` | `HYGOLD 5000BS` | 2078.85 | 2747.90 |
   | `HV2-01` | `HYVOLT II` | 1893.94 | 2742.70 |
   | `HV2-02` | `HYVOLT II` | 2328.74 | 3377.28 |
   | `HV2-03` | `HYVOLT II` | 2560.84 | 3424.90 |
   | `HV2-04` | `HYVOLT II` | 3065.07 | 3868.94 |
4. **Consulta SQL equivalente y comprobación en PostgreSQL:**
   ```sql
   SELECT DISTINCT claveproducto, modeloproducto, costounitariousd, preciounitariousd
   FROM producto
   WHERE costounitariousd > 1850
   ORDER BY claveproducto;
   ```
   *Comprobación:* Devuelve las mismas **5 filas** en PostgreSQL y en RelaX.

---

#### Consulta 2 (`02-proyeccion.sql`)
1. **Pregunta del dominio:** ¿Qué modelos comerciales del catálogo pertenecen a las líneas especializadas `'HYPRENE'` o `'HYVOLT'`?
2. **Expresión en álgebra relacional:**
   $$\pi_{\text{modeloproducto, tipoproducto}}\big(\sigma_{\text{tipoproducto} = \text{'HYPRENE'} \lor \text{tipoproducto} = \text{'HYVOLT'}}(\text{modelo\_producto})\big)$$
   **En RelaX:**
   ```text
   pi modeloproducto, tipoproducto (
     sigma tipoproducto = 'HYPRENE' or tipoproducto = 'HYVOLT' (modelo_producto)
   )
   ```
3. **Árbol y resultado en RelaX ([captura](./evidencias/relax-q02.svg)):**
   ```text
   π modeloproducto, tipoproducto
     │
   σ tipoproducto = 'HYPRENE' ∨ tipoproducto = 'HYVOLT'
     │
   modelo_producto
   ```
   | modeloproducto | tipoproducto |
   | :--- | :--- |
   | `HYPRENE BO150` | `HYPRENE` |
   | `HYPRENE L2000` | `HYPRENE` |
   | `HYPRENE P150 BS` | `HYPRENE` |
   | `HYVOLT II` | `HYVOLT` |
4. **Consulta SQL equivalente y comprobación en PostgreSQL:**
   ```sql
   SELECT DISTINCT modeloproducto, tipoproducto
   FROM modelo_producto
   WHERE tipoproducto = 'HYPRENE' OR tipoproducto = 'HYVOLT'
   ORDER BY modeloproducto;
   ```
   *Comprobación:* Devuelve exactamente los mismos **4 modelos** en PostgreSQL y en RelaX.

---

#### Consulta 3 (`03-composicion-seleccion-proyeccion.sql`)
1. **Pregunta del dominio:** ¿Cuál es el número de cliente, razón social, RFC y estado de origen de los clientes nacionales con número de cliente entre 1001 y 1004?
2. **Expresión en álgebra relacional:**
   $$\pi_{\text{numerocliente, razonsocial, rfc, estadoorigen}}\big(\sigma_{\text{tipocliente} = \text{'NACIONAL'} \land \text{numerocliente} \le 1004}(\text{cliente})\big)$$
   **En RelaX:**
   ```text
   pi numerocliente, razonsocial, rfc, estadoorigen (
     sigma tipocliente = 'NACIONAL' and numerocliente <= 1004 (cliente)
   )
   ```
3. **Árbol y resultado en RelaX ([captura](./evidencias/relax-q03.svg)):**
   ```text
   π numerocliente, razonsocial, rfc, estadoorigen
     │
   σ tipocliente = 'NACIONAL' ∧ numerocliente ≤ 1004
     │
   cliente
   ```
   | numerocliente | razonsocial | rfc | estadoorigen |
   | ---: | :--- | :--- | :--- |
   | 1001 | `Distribuidora Metrópoli S.A.B. de C.V.` | `SGF13092864L` | `Tamaulipas` |
   | 1002 | `Eléctrica Nova S.A. de C.V.` | `XTU100821KA7` | `Jalisco` |
   | 1003 | `Eléctrica Cobalto S.A.P.I. de C.V.` | `GQH131027S5A` | `Ciudad de México` |
   | 1004 | `Cables Andes S.A.P.I. de C.V.` | `ACS990910GZG` | `Aguascalientes` |
4. **Consulta SQL equivalente y comprobación en PostgreSQL:**
   ```sql
   SELECT DISTINCT numerocliente, razonsocial, rfc, estadoorigen
   FROM cliente
   WHERE tipocliente = 'NACIONAL' AND numerocliente <= 1004
   ORDER BY numerocliente;
   ```
   *Comprobación:* Devuelve las mismas **4 filas** en PostgreSQL y en RelaX.

---

### B) Unión ($\cup$), Intersección ($\cap$) y Diferencia ($-$) — 3 consultas

> **Compatibilidad de unión:** En las tres consultas proyectamos antes las mismas columnas con el mismo dominio en ambas relaciones para que tengan igual grado y tipos compatibles.

#### Consulta 4 — Unión (`04-union.sql`)
1. **Pregunta del dominio:** ¿Cuáles son las claves y modelos de los productos que pertenecen al modelo `'HYVOLT II'` o al modelo `'HYPRENE BO150'`?
2. **Expresión en álgebra relacional:**
   $$P_{\text{hyvolt}} \leftarrow \pi_{\text{claveproducto, modeloproducto}}\big(\sigma_{\text{modeloproducto} = \text{'HYVOLT II'}}(\text{producto})\big)$$
   $$P_{\text{hyprene}} \leftarrow \pi_{\text{claveproducto, modeloproducto}}\big(\sigma_{\text{modeloproducto} = \text{'HYPRENE BO150'}}(\text{producto})\big)$$
   $$\text{Resultado} \leftarrow P_{\text{hyvolt}} \cup P_{\text{hyprene}}$$
   **En RelaX:**
   ```text
   P_hyvolt = pi claveproducto, modeloproducto (sigma modeloproducto = 'HYVOLT II' (producto))
   P_hyprene = pi claveproducto, modeloproducto (sigma modeloproducto = 'HYPRENE BO150' (producto))
   P_hyvolt union P_hyprene
   ```
3. **Árbol y resultado en RelaX ([captura](./evidencias/relax-q04.svg)):**
   ```text
                ∪
         ┌──────┴──────┐
     π clave...    π clave...
         │             │
   σ 'HYVOLT II'  σ 'HYPRENE BO150'
         │             │
     producto      producto
   ```
   | claveproducto | modeloproducto |
   | :--- | :--- |
   | `HPB-01` | `HYPRENE BO150` |
   | `HPB-02` | `HYPRENE BO150` |
   | `HPB-03` | `HYPRENE BO150` |
   | `HPB-04` | `HYPRENE BO150` |
   | `HV2-01` | `HYVOLT II` |
   | `HV2-02` | `HYVOLT II` |
   | `HV2-03` | `HYVOLT II` |
   | `HV2-04` | `HYVOLT II` |
4. **Consulta SQL equivalente y comprobación en PostgreSQL:**
   ```sql
   SELECT claveproducto, modeloproducto FROM producto WHERE modeloproducto = 'HYVOLT II'
   UNION
   SELECT claveproducto, modeloproducto FROM producto WHERE modeloproducto = 'HYPRENE BO150'
   ORDER BY claveproducto;
   ```
   *Comprobación:* Devuelve las mismas **8 filas** en PostgreSQL y en RelaX.

---

#### Consulta 5 — Intersección (`05-interseccion.sql`)
1. **Pregunta del dominio:** ¿Qué números de cliente (entre los clientes 1001, 1002, 1004 y 1052) son clientes nacionales y además tienen registrada una segunda sucursal con clave `'S02'`?
2. **Expresión en álgebra relacional:**
   $$C_{\text{nac}} \leftarrow \pi_{\text{numerocliente}}\big(\sigma_{\text{tipocliente} = \text{'NACIONAL'} \land \text{numerocliente} \in \{1001, 1002, 1004, 1052\}}(\text{cliente})\big)$$
   $$C_{\text{s02}} \leftarrow \pi_{\text{numerocliente}}\big(\sigma_{\text{clavesucursal} = \text{'S02'} \land \text{numerocliente} \in \{1001, 1002, 1004, 1052\}}(\text{sucursal})\big)$$
   $$\text{Resultado} \leftarrow C_{\text{nac}} \cap C_{\text{s02}}$$
   **En RelaX:**
   ```text
   C_nac = pi numerocliente (sigma tipocliente = 'NACIONAL' and (numerocliente = 1001 or numerocliente = 1002 or numerocliente = 1004 or numerocliente = 1052) (cliente))
   C_s02 = pi numerocliente (sigma clavesucursal = 'S02' and (numerocliente = 1001 or numerocliente = 1002 or numerocliente = 1004 or numerocliente = 1052) (sucursal))
   C_nac intersect C_s02
   ```
3. **Árbol y resultado en RelaX ([captura](./evidencias/relax-q05.svg)):**
   ```text
                ∩
         ┌──────┴──────┐
   π numerocliente  π numerocliente
         │             │
     σ (cliente)   σ (sucursal)
   ```
   | numerocliente |
   | ---: |
   | 1004 |
   | 1052 |
4. **Consulta SQL equivalente y comprobación en PostgreSQL:**
   ```sql
   SELECT numerocliente FROM cliente
   WHERE tipocliente = 'NACIONAL' AND numerocliente IN (1001, 1002, 1004, 1052)
   INTERSECT
   SELECT numerocliente FROM sucursal
   WHERE clavesucursal = 'S02' AND numerocliente IN (1001, 1002, 1004, 1052)
   ORDER BY numerocliente;
   ```
   *Comprobación:* Ambas relaciones proyectan solo `numerocliente` (`INTEGER`), cumpliendo compatibilidad de unión, y devuelven las mismas **2 filas** (`1004` y `1052`).

---

#### Consulta 6 — Diferencia (`06-diferencia.sql`)
1. **Pregunta del dominio:** ¿Cuáles de los clientes 1001, 1002, 1008 y 1026 no realizaron ningún pedido dentro de los primeros cuatro folios del año (`folio <= 100004`)?
2. **Expresión en álgebra relacional:**
   $$C_{\text{sel}} \leftarrow \pi_{\text{numerocliente}}\big(\sigma_{\text{numerocliente} \in \{1001, 1002, 1008, 1026\}}(\text{cliente})\big)$$
   $$P_{\text{cuatro}} \leftarrow \pi_{\text{numerocliente}}\big(\sigma_{\text{folio} \le 100004}(\text{pedido})\big)$$
   $$\text{Resultado} \leftarrow C_{\text{sel}} - P_{\text{cuatro}}$$
   **En RelaX:**
   ```text
   C_sel = pi numerocliente (sigma numerocliente = 1001 or numerocliente = 1002 or numerocliente = 1008 or numerocliente = 1026 (cliente))
   P_cuatro = pi numerocliente (sigma folio <= 100004 (pedido))
   C_sel - P_cuatro
   ```
3. **Árbol y resultado en RelaX ([captura](./evidencias/relax-q06.svg)):**
   ```text
                −
         ┌──────┴──────┐
   π numerocliente  π numerocliente
         │             │
     σ (cliente)    σ (pedido)
   ```
   | numerocliente |
   | ---: |
   | 1001 |
   | 1002 |
4. **Consulta SQL equivalente y comprobación en PostgreSQL:**
   ```sql
   SELECT numerocliente FROM cliente WHERE numerocliente IN (1001, 1002, 1008, 1026)
   EXCEPT
   SELECT numerocliente FROM pedido WHERE folio <= 100004
   ORDER BY numerocliente;
   ```
   *Comprobación:* Devuelve las mismas **2 filas** (`1001` y `1002`, ya que `1008` y `1026` sí tienen los pedidos `100004` y `100001`).

---

### C) Producto cartesiano ($\times$) — 1 consulta

#### Consulta 7 (`07-producto-cartesiano.sql`)
1. **Pregunta del dominio:** ¿Qué combinaciones genera el producto cartesiano sin filtro entre los modelos `'HYVOLT II'` y `'HYPRENE BO150'` y las presentaciones `'HV2-04'` y `'HPB-04'`, demostrando por qué casi nunca se usa solo?
2. **Expresión en álgebra relacional:**
   $$M_{\text{dos}} \leftarrow \rho_{m}\Big(\pi_{\text{modeloproducto, tipoproducto}}\big(\sigma_{\text{modeloproducto} \in \{\text{'HYVOLT II'}, \text{'HYPRENE BO150'}\}}(\text{modelo\_producto})\big)\Big)$$
   $$P_{\text{dos}} \leftarrow \rho_{p}\Big(\pi_{\text{claveproducto, modeloproducto, preciounitariousd}}\big(\sigma_{\text{claveproducto} \in \{\text{'HV2-04'}, \text{'HPB-04'}\}}(\text{producto})\big)\Big)$$
   $$\text{Resultado} \leftarrow M_{\text{dos}} \times P_{\text{dos}}$$
   **En RelaX:**
   ```text
   M_dos = rho m (pi modeloproducto, tipoproducto (sigma modeloproducto = 'HYVOLT II' or modeloproducto = 'HYPRENE BO150' (modelo_producto)))
   P_dos = rho p (pi claveproducto, modeloproducto, preciounitariousd (sigma claveproducto = 'HV2-04' or claveproducto = 'HPB-04' (producto)))
   M_dos cross join P_dos
   ```
3. **Árbol y resultado en RelaX ([captura](./evidencias/relax-q07.svg)):**
   ```text
              ⨯ (cross join)
         ┌──────────┴──────────┐
       ρ m                    ρ p
        │                      │
   π modelo, tipo        π clave, modelo, precio
        │                      │
   σ (modelo_producto)    σ (producto)
   ```
   | m.modeloproducto | m.tipoproducto | p.claveproducto | p.modeloproducto | p.preciounitariousd | ¿Combinación real? |
   | :--- | :--- | :--- | :--- | ---: | :--- |
   | `HYPRENE BO150` | `HYPRENE` | `HPB-04` | `HYPRENE BO150` | 249.05 | Sí (modelos coinciden) |
   | `HYPRENE BO150` | `HYPRENE` | `HV2-04` | `HYVOLT II` | 3868.94 | **Falsa** (cruza modelos distintos) |
   | `HYVOLT II` | `HYVOLT` | `HPB-04` | `HYPRENE BO150` | 249.05 | **Falsa** (cruza modelos distintos) |
   | `HYVOLT II` | `HYVOLT` | `HV2-04` | `HYVOLT II` | 3868.94 | Sí (modelos coinciden) |
   *¿Por qué casi nunca se usa solo?* Porque empareja todas las filas contra todas ($2 \times 2 = 4$), mezclando el producto `HV2-04` con el modelo `HYPRENE BO150` al que no pertenece. Solo tiene sentido si después se filtra con $\sigma_{m.\text{modeloproducto} = p.\text{modeloproducto}}$ (lo cual es precisamente una reunión $\bowtie$).
4. **Consulta SQL equivalente y comprobación en PostgreSQL:**
   ```sql
   SELECT m.modeloproducto AS m_modeloproducto, m.tipoproducto,
          p.claveproducto, p.modeloproducto AS p_modeloproducto, p.preciounitariousd
   FROM (SELECT modeloproducto, tipoproducto FROM modelo_producto WHERE modeloproducto IN ('HYVOLT II', 'HYPRENE BO150')) AS m
   CROSS JOIN (SELECT claveproducto, modeloproducto, preciounitariousd FROM producto WHERE claveproducto IN ('HV2-04', 'HPB-04')) AS p
   ORDER BY m.modeloproducto, p.claveproducto;
   ```
   *Comprobación:* Devuelve las mismas **4 filas** en PostgreSQL y en RelaX.

---

### D) Reunión natural ($\bowtie$), Theta ($\bowtie_\theta$) y Externa (Outer Join) — 3 consultas

#### Consulta 8 — Reunión natural (`08-reunion-natural.sql`)
1. **Pregunta del dominio:** ¿A qué línea comercial (`tipoproducto`) pertenece cada presentación cuyo costo unitario de producción supera los 2,000 USD?
2. **Expresión en álgebra relacional:**
   $$P_{\text{caros}} \leftarrow \sigma_{\text{costounitariousd} > 2000}(\text{producto})$$
   $$\text{Resultado} \leftarrow \pi_{\text{claveproducto, modeloproducto, tipoproducto, costounitariousd, preciounitariousd}}\big(P_{\text{caros}} \bowtie \text{modelo\_producto}\big)$$
   **En RelaX:**
   ```text
   P_caros = sigma costounitariousd > 2000 (producto)
   pi claveproducto, modeloproducto, tipoproducto, costounitariousd, preciounitariousd (
     P_caros natural join modelo_producto
   )
   ```
3. **Árbol y resultado en RelaX ([captura](./evidencias/relax-q08.svg)):**
   ```text
   π claveproducto, modeloproducto, tipoproducto, costounitariousd, preciounitariousd
     │
     ⋈ (natural join por modeloproducto)
     ├── σ costounitariousd > 2000 (producto)
     └── modelo_producto
   ```
   | claveproducto | modeloproducto | tipoproducto | costounitariousd | preciounitariousd |
   | :--- | :--- | :--- | ---: | ---: |
   | `HG5-04` | `HYGOLD 5000BS` | `OMNIGOLD` | 2078.85 | 2747.90 |
   | `HV2-02` | `HYVOLT II` | `HYVOLT` | 2328.74 | 3377.28 |
   | `HV2-03` | `HYVOLT II` | `HYVOLT` | 2560.84 | 3424.90 |
   | `HV2-04` | `HYVOLT II` | `HYVOLT` | 3065.07 | 3868.94 |
   *Filas conservadas y perdidas:* Se conservan los 4 productos con costo $> 2000$ unidos con sus 2 modelos (`HYGOLD 5000BS` y `HYVOLT II`); los otros 8 modelos de `modelo_producto` que no tienen productos con costo $> 2000$ se pierden en la reunión natural.
4. **Consulta SQL equivalente y comprobación en PostgreSQL:**
   ```sql
   SELECT DISTINCT claveproducto, modeloproducto, tipoproducto, costounitariousd, preciounitariousd
   FROM producto NATURAL JOIN modelo_producto
   WHERE costounitariousd > 2000
   ORDER BY claveproducto;
   ```
   *Comprobación:* Devuelve las mismas **4 filas** en PostgreSQL y en RelaX.

---

#### Consulta 9 — Reunión theta (`09-reunion-theta.sql`)
1. **Pregunta del dominio:** Entre los primeros cuatro pedidos del año (`folio <= 100004`), ¿cuáles tuvieron un envío con costo de flete mayor a 3,000 USD y qué guía y transportista los atendió?
2. **Expresión en álgebra relacional:**
   $$P_4 \leftarrow \rho_{p}\big(\sigma_{\text{folio} \le 100004}(\text{pedido})\big)$$
   $$E_4 \leftarrow \rho_{e}\big(\sigma_{\text{folio} \le 100004}(\text{envio})\big)$$
   $$\text{Resultado} \leftarrow \pi_{p.\text{folio},\; p.\text{numerocliente},\; p.\text{estatus},\; e.\text{numeroguia},\; e.\text{clavetransportista},\; e.\text{costoflete}}\Big(P_4 \bowtie_{p.\text{folio} = e.\text{folio} \;\land\; e.\text{costoflete} > 3000} E_4\Big)$$
   **En RelaX:**
   ```text
   P_cuatro = rho p (sigma folio <= 100004 (pedido))
   E_cuatro = rho e (sigma folio <= 100004 (envio))
   pi p.folio, p.numerocliente, p.estatus, e.numeroguia, e.clavetransportista, e.costoflete (
     P_cuatro join p.folio = e.folio and e.costoflete > 3000 E_cuatro
   )
   ```
3. **Árbol y resultado en RelaX ([captura](./evidencias/relax-q09.svg)):**
   ```text
   π p.folio, p.numerocliente, p.estatus, e.numeroguia, e.clavetransportista, e.costoflete
     │
     ⋈ (p.folio = e.folio ∧ e.costoflete > 3000)
     ├── ρ p (σ folio ≤ 100004 (pedido))
     └── ρ e (σ folio ≤ 100004 (envio))
   ```
   | p.folio | p.numerocliente | p.estatus | e.numeroguia | e.clavetransportista | e.costoflete |
   | ---: | ---: | :--- | :--- | :--- | ---: |
   | 100001 | 1026 | `ENTREGADO` | `GU937557166733` | `TR030` | 3982.88 |
   | 100004 | 1008 | `ENTREGADO` | `GU635074827946` | `TR016` | 11919.80 |
   *Filas conservadas y perdidas:* De los 4 pedidos (`100001` a `100004`), se pierde el `100002` (porque su flete es `178.59 <= 3000`) y se pierde el `100003` (porque está `'CANCELADO'` y no tiene fila en `envio`).
4. **Consulta SQL equivalente y comprobación en PostgreSQL:**
   ```sql
   SELECT DISTINCT p.folio, p.numerocliente, p.estatus, e.numeroguia, e.clavetransportista, e.costoflete
   FROM pedido AS p
   JOIN envio AS e ON p.folio = e.folio AND e.costoflete > 3000
   WHERE p.folio <= 100004
   ORDER BY p.folio;
   ```
   *Comprobación:* Devuelve las mismas **2 filas** en PostgreSQL y en RelaX.

---

#### Consulta 10 — Reunión externa izquierda (`10-reunion-externa.sql`)
1. **Pregunta del dominio:** Para todos los pedidos con folio menor o igual a 100004, ¿cuál es su número de guía y costo de flete, conservando con `NULL` los pedidos cancelados que no tienen envío?
2. **Expresión en álgebra relacional:**
   $$P_4 \leftarrow \pi_{\text{folio, numerocliente, estatus}}\big(\sigma_{\text{folio} \le 100004}(\text{pedido})\big)$$
   $$E_{\text{guia}} \leftarrow \pi_{\text{folio, numeroguia, costoflete}}(\text{envio})$$
   $$\text{Resultado} \leftarrow P_4 \ E_{\text{guia}}$$
   **En RelaX:**
   ```text
   P_cuatro = pi folio, numerocliente, estatus (sigma folio <= 100004 (pedido))
   E_guia = pi folio, numeroguia, costoflete (envio)
   P_cuatro left outer join E_guia
   ```
3. **Árbol y resultado en RelaX ([captura](./evidencias/relax-q10.svg)):**
   ```text
         ⟕ (left outer join por folio)
         ├── π folio, numerocliente, estatus (σ folio ≤ 100004 (pedido))
         └── π folio, numeroguia, costoflete (envio)
   ```
   | folio | numerocliente | estatus | numeroguia | costoflete |
   | ---: | ---: | :--- | :--- | ---: |
   | 100001 | 1026 | `ENTREGADO` | `GU937557166733` | 3982.88 |
   | 100002 | 1052 | `ENTREGADO` | `GU309405377382` | 178.59 |
   | **100003** | **1052** | **`CANCELADO`** | **`null`** | **`null`** |
   | 100004 | 1008 | `ENTREGADO` | `GU635074827946` | 11919.80 |
   *Qué filas se conservan:* A diferencia de una reunión interna (donde el pedido `100003` desaparece por no tener envío), la **reunión externa izquierda conserva el pedido `100003`** rellenando `numeroguia` y `costoflete` con `NULL`.
4. **Consulta SQL equivalente y comprobación en PostgreSQL:**
   ```sql
   SELECT p.folio, p.numerocliente, p.estatus, e.numeroguia, e.costoflete
   FROM (SELECT folio, numerocliente, estatus FROM pedido WHERE folio <= 100004) AS p
   LEFT JOIN (SELECT folio, numeroguia, costoflete FROM envio) AS e ON p.folio = e.folio
   ORDER BY p.folio;
   ```
   *Comprobación:* Devuelve las mismas **4 filas** (incluyendo la fila con `NULL` del folio `100003`) en PostgreSQL y en RelaX.

---

### E) Agregación y agrupación ($\gamma$) — 2 consultas

#### Consulta 11 (`11-agregacion-modelos.sql`)
1. **Pregunta del dominio:** ¿Cuántos modelos comerciales están registrados en cada línea de producto (`tipoproducto`)?
2. **Expresión en álgebra relacional:**
   $$\gamma_{\text{tipoproducto};\; \text{count}(\text{modeloproducto}) \to \text{total\_modelos}}(\text{modelo\_producto})$$
   **En RelaX:**
   ```text
   gamma tipoproducto; count(modeloproducto)->total_modelos (modelo_producto)
   ```
3. **Árbol y resultado en RelaX ([captura](./evidencias/relax-q11.svg)):**
   ```text
   γ tipoproducto; count(modeloproducto) → total_modelos
     │
   modelo_producto
   ```
   | tipoproducto | total_modelos |
   | :--- | ---: |
   | `HYPRENE` | 3 |
   | `HYVOLT` | 1 |
   | `OMNIGOLD` | 6 |
4. **Consulta SQL equivalente y comprobación en PostgreSQL:**
   ```sql
   SELECT tipoproducto, COUNT(modeloproducto) AS total_modelos
   FROM modelo_producto
   GROUP BY tipoproducto
   ORDER BY tipoproducto;
   ```
   *Comprobación:* Devuelve los mismos **3 grupos** (`3 + 1 + 6 = 10` modelos) en PostgreSQL y en RelaX.

---

#### Consulta 12 (`12-agregacion-precios.sql`)
1. **Pregunta del dominio:** Para los modelos `'HYVOLT II'` y `'HYGOLD 5000BS'`, ¿cuántas presentaciones tiene cada uno y cuáles son su costo unitario promedio, precio mínimo y precio máximo?
2. **Expresión en álgebra relacional:**
   $$P_{\text{dos}} \leftarrow \sigma_{\text{modeloproducto} = \text{'HYVOLT II'} \lor \text{modeloproducto} = \text{'HYGOLD 5000BS'}}(\text{producto})$$
   $$\text{Resultado} \leftarrow \gamma_{\text{modeloproducto};\; \text{count}(\text{claveproducto}) \to \text{presentaciones},\; \text{avg}(\text{costounitariousd}) \to \text{costo\_promedio},\; \text{min}(\text{preciounitariousd}) \to \text{precio\_min},\; \text{max}(\text{preciounitariousd}) \to \text{precio\_max}}(P_{\text{dos}})$$
   **En RelaX:**
   ```text
   P_dos_modelos = sigma modeloproducto = 'HYVOLT II' or modeloproducto = 'HYGOLD 5000BS' (producto)
   gamma modeloproducto; count(claveproducto)->presentaciones, avg(costounitariousd)->costo_promedio, min(preciounitariousd)->precio_min, max(preciounitariousd)->precio_max (P_dos_modelos)
   ```
3. **Árbol y resultado en RelaX ([captura](./evidencias/relax-q12.svg)):**
   ```text
   γ modeloproducto; count(claveproducto)→presentaciones, avg(...)→costo_promedio, min(...)→precio_min, max(...)→precio_max
     │
   σ modeloproducto = 'HYVOLT II' ∨ modeloproducto = 'HYGOLD 5000BS'
     │
   producto
   ```
   | modeloproducto | presentaciones | costo_promedio | precio_min | precio_max |
   | :--- | ---: | ---: | ---: | ---: |
   | `HYGOLD 5000BS` | 4 | 1692.95 | 1844.93 | 2747.90 |
   | `HYVOLT II` | 4 | 2462.15 | 2742.70 | 3868.94 |
4. **Consulta SQL equivalente y comprobación en PostgreSQL:**
   ```sql
   SELECT modeloproducto,
          COUNT(claveproducto) AS presentaciones,
          ROUND(AVG(costounitariousd), 2) AS costo_promedio,
          MIN(preciounitariousd) AS precio_min,
          MAX(preciounitariousd) AS precio_max
   FROM producto
   WHERE modeloproducto IN ('HYVOLT II', 'HYGOLD 5000BS')
   GROUP BY modeloproducto
   ORDER BY modeloproducto;
   ```
   *Comprobación:* Devuelve las mismas **2 filas** con idénticos valores agregados en PostgreSQL y en RelaX.

---

### F) División ($\div$) — 1 consulta

#### Consulta 13 (`13-division.sql`)
1. **Pregunta del dominio:** ¿Qué pedidos (`folio`) han incluido **todos** los productos cuyo proveedor de transporte es `'Tráileres Monterrey'` (`HPB-02` y `HPL-01`)?
2. **Expresión en álgebra relacional:**
   $$R \leftarrow \pi_{\text{folio, claveproducto}}(\text{detalle})$$
   $$S \leftarrow \pi_{\text{claveproducto}}\big(\sigma_{\text{provtransporte} = \text{'Tráileres Monterrey'}}(\text{producto})\big)$$
   $$\text{Resultado} \leftarrow R \div S$$
   **En RelaX:**
   ```text
   R = pi folio, claveproducto (detalle)
   S = pi claveproducto (sigma provtransporte = 'Tráileres Monterrey' (producto))
   R / S
   ```
3. **Árbol y resultado en RelaX ([captura](./evidencias/relax-q13.svg)):**
   ```text
                 ÷
         ┌───────┴───────┐
   π folio, claveprod  π claveproducto
         │               │
      detalle          σ provtransporte = 'Tráileres Monterrey'
                         │
                      producto
   ```
   | folio |
   | ---: |
   | 100023 |
   | 100031 |
4. **Consulta SQL equivalente y comprobación en PostgreSQL:**
   ```sql
   SELECT d.folio
   FROM detalle AS d
   WHERE d.claveproducto IN (
     SELECT claveproducto FROM producto WHERE provtransporte = 'Tráileres Monterrey'
   )
   GROUP BY d.folio
   HAVING COUNT(DISTINCT d.claveproducto) = (
     SELECT COUNT(DISTINCT claveproducto) FROM producto WHERE provtransporte = 'Tráileres Monterrey'
   )
   ORDER BY d.folio;
   ```
   *Comprobación:* Tanto en RelaX como en los 1,500 renglones de `detalle` en PostgreSQL, los únicos pedidos que compraron las dos presentaciones de `'Tráileres Monterrey'` (`HPB-02` y `HPL-01`) son **`100023` y `100031`**.

---

## Ejercicio 2.3. El álgebra del proyecto asignado (`PublicMunicipalWorks_DWH`)

Tomamos tres consultas reales que ejecuta el sistema asignado en su backend y vistas analíticas (`db/arquitectura/FUNCIONES Y TRIGGERS.sql` y `backend/routes/analitica.py`), las expresamos en álgebra relacional, dibujamos su árbol y señalamos qué operador hace el trabajo pesado.

---

### Consulta Asignada 1: Tablero de obras con retraso (`v_obras_retraso`)

* **Qué hace en el sistema asignado:** Obtiene las obras activas que presentan retraso en el corte mensual más reciente, uniendo la tabla de hechos `fact_obra_mensual` con las versiones actuales de `dim_obra`, `dim_region`, `dim_constructora` y `dim_personal`.
* **Expresión en álgebra relacional por pasos:**
  $$T_{\max} \leftarrow \gamma_{;\; \max(\text{tiempo\_key}) \to \text{max\_t}}(\text{fact\_obra\_mensual})$$
  $$F_{\text{ret}} \leftarrow \sigma_{\text{tiene\_retraso} = \text{true}}(\text{fact\_obra\_mensual}) \bowtie_{\text{tiempo\_key} = \text{max\_t}} T_{\max}$$
  $$O_{\text{act}} \leftarrow \sigma_{\text{es\_actual} = \text{true}}(\text{dim\_obra})$$
  $$R_{\text{act}} \leftarrow \sigma_{\text{es\_actual} = \text{true}}(\text{dim\_region})$$
  $$C_{\text{act}} \leftarrow \sigma_{\text{es\_actual} = \text{true}}(\text{dim\_constructora})$$
  $$P_{\text{act}} \leftarrow \sigma_{\text{es\_actual} = \text{true}}(\text{dim\_personal})$$
  $$J_1 \leftarrow F_{\text{ret}} \bowtie_{F_{\text{ret}}.\text{obra\_key} = O_{\text{act}}.\text{obra\_key}} O_{\text{act}}$$
  $$J_2 \leftarrow \big((J_1 \_{J_1.\text{region\_key} = R_{\text{act}}.\text{region\_key}} R_{\text{act}}) \_{J_1.\text{constructora\_key} = C_{\text{act}}.\text{constructora\_key}} C_{\text{act}}\big) \_{J_1.\text{supervisor\_key} = P_{\text{act}}.\text{personal\_key}} P_{\text{act}}$$
  $$\text{Resultado} \leftarrow \pi_{\text{obra\_id, nombre\_obra, etapa\_nombre, comunidad, nombre\_const, nombre\_completo, presupuesto\_total, costo\_acumulado, dias\_retraso}}(J_2)$$
* **Árbol de expresión:**
  ```text
  π obra_id, nombre_obra, etapa_nombre, comunidad, nombre_const, nombre_completo, ...
    │
    ⟕ (supervisor_key = personal_key)
    ├── ⟕ (constructora_key)
    │   ├── ⟕ (region_key)
    │   │   ├── ⋈ (obra_key)
    │   │   │   ├── ⋈ (tiempo_key = max_t)
    │   │   │   │   ├── σ tiene_retraso = true (fact_obra_mensual)
    │   │   │   │   └── γ max(tiempo_key) → max_t (fact_obra_mensual)
    │   │   │   └── σ es_actual = true (dim_obra)
    │   │   └── σ es_actual = true (dim_region)
    │   └── σ es_actual = true (dim_constructora)
    └── σ es_actual = true (dim_personal)
  ```
* **¿Qué operador hace el trabajo pesado?** La **selección combinada con la reunión por el último periodo ($\sigma_{\text{tiene\_retraso}} \bowtie_{\text{tiempo\_key} = \text{max\_t}}$)** sobre `fact_obra_mensual`, porque descarta los 23 meses históricos anteriores y las obras a tiempo antes de ejecutar las reuniones externas ($\$) contra las cuatro dimensiones SCD Tipo 2.

---

### Consulta Asignada 2: Participación ciudadana por región (`v_participacion_ciudadana`)

* **Qué hace en el sistema asignado:** Cuenta cuántas propuestas ciudadanas, cuántos votantes únicos y cuántos votos totales se registraron por región y año de convocatoria.
* **Expresión en álgebra relacional por pasos:**
  $$E_{\text{voto}} \leftarrow \pi_{\text{tipo\_evento\_key}}\big(\sigma_{\text{codigo\_evento} = \text{'VOTO\_EMITIDO'}}(\text{dim\_tipo\_evento})\big)$$
  $$V \leftarrow \text{fact\_eventos\_auditoria} \bowtie E_{\text{voto}}$$
  $$U \leftarrow \text{dim\_propuesta} \_{\text{dim\_propuesta.propuesta\_key} = V.\text{propuesta\_key}} V$$
  $$\text{Resultado} \leftarrow \gamma_{\text{region, anio\_convocatoria};\; \text{count\_distinct}(\text{propuesta\_id}) \to \text{total\_propuestas},\; \text{count\_distinct}(\text{poblador\_key}) \to \text{votantes\_unicos},\; \text{count}(\text{evento\_key}) \to \text{total\_votos}}(U)$$
* **Árbol de expresión:**
  ```text
  γ region, anio_convocatoria; count(propuesta_id)→total_propuestas, count(poblador_key)→votantes_unicos, count(evento_key)→total_votos
    │
    ⟕ (propuesta_key)
    ├── dim_propuesta
    └── ⋈ (tipo_evento_key)
        ├── fact_eventos_auditoria
        └── π tipo_evento_key (σ codigo_evento = 'VOTO_EMITIDO' (dim_tipo_evento))
  ```
* **¿Qué operador hace el trabajo pesado?** El operador de **agrupación y agregación ($\gamma$)** junto con la **reunión externa izquierda ($\)**, ya que conserva propuestas que aún tienen 0 votos y agrupa miles de eventos de votación de `fact_eventos_auditoria` por región y año para calcular los conteos.

---

### Consulta Asignada 3: Ejercicio presupuestario por fuente (`v_ejercicio_presupuestario`)

* **Qué hace en el sistema asignado:** Calcula cuántas obras financia cada fuente presupuestaria (FAIS, FORTAMUN, etc.) y suma el presupuesto asignado, el monto ejercido y el saldo pendiente en el último corte mensual.
* **Expresión en álgebra relacional por pasos:**
  $$T_{\max} \leftarrow \gamma_{;\; \max(\text{tiempo\_key}) \to \text{tiempo\_key}}(\text{fact\_obra\_mensual})$$
  $$F_{\text{ult}} \leftarrow \text{fact\_obra\_mensual} \bowtie T_{\max}$$
  $$O_{\text{act}} \leftarrow \sigma_{\text{es\_actual} = \text{true}}(\text{dim\_obra})$$
  $$J \leftarrow \big(\text{dim\_fuente} \bowtie_{\text{fuente\_id} = \text{id\_fuente}} \text{financia}\big) \bowtie_{\text{id\_obra} = \text{obra\_id}} O_{\text{act}} \bowtie_{\text{obra\_key}} F_{\text{ult}}$$
  $$\text{Resultado} \leftarrow \gamma_{\text{fuente\_id, grado\_nivel, programa};\; \text{count\_distinct}(\text{obra\_key}) \to \text{obras\_financiadas},\; \text{sum}(\text{presupuesto\_total}) \to \text{presupuesto\_asignado},\; \text{sum}(\text{costo\_acumulado}) \to \text{monto\_ejercido},\; \text{sum}(\text{saldo\_presupuesto}) \to \text{saldo\_pendiente}}(J)$$
* **Árbol de expresión:**
  ```text
  γ fuente_id, grado_nivel, programa; count(obra_key)→obras, sum(presupuesto_total)→asignado, sum(costo_acumulado)→ejercido, sum(saldo_presupuesto)→saldo
    │
    ⋈ (obra_key)
    ├── ⋈ (id_obra = obra_id)
    │   ├── ⋈ (fuente_id = id_fuente)
    │   │   ├── dim_fuente
    │   │   └── financia
    │   └── σ es_actual = true (dim_obra)
    └── ⋈ (tiempo_key)
        ├── fact_obra_mensual
        └── γ max(tiempo_key) → tiempo_key (fact_obra_mensual)
  ```
* **¿Qué operador hace el trabajo pesado?** La **cadena de reuniones ($\bowtie$) seguida de la agrupación ($\gamma$)**, porque cruza las fuentes de financiamiento con las obras activas y sus snapshots mensuales para sumarizar los montos financieros por programa y nivel de gobierno.
