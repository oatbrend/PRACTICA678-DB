# Parte 1. Dependencias funcionales y normalización — Proyecto propio (ERGON)

Partimos del esquema de **ERGON** (ventas y envíos de aceites industriales) con los 2,702 registros de las Prácticas 4 y 5:
* `cliente(numeroCliente, razonSocial, correoCliente, telefonoCliente, tipoCliente, RFC, regimenFiscal, estadoOrigen, idFiscalGlobal, paisReceptor)`
* `transportista(claveTransportista, nombreEmpresa, telefonoAtencion, email, esNacional, esInternacional, RFC, codigoAduanal, agenciaAduanal)`
* `producto(claveProducto, modeloProducto, costoUnitarioUSD, precioUnitarioUSD, tipoProducto, provMaquinaria, provTransformador, provTransporte)`
* `sucursal(numeroCliente, claveSucursal, nombrePlanta, telefonoEncargado, calle, numero, ciudad, estado, pais, CP)`
* `pedido(folio, numeroCliente, estatus, dia, mes, anio, activo)`
* `detalle(folio, claveParcial, claveProducto, costoProduccion, precioAplicado, cantidad)`
* `envio(numeroGuia, folio, claveTransportista, numeroCliente, claveSucursal, costoFlete, dia, mes, anio)`

---

## Ejercicio 1.1. Pautas de diseño

Revisamos cada tabla contra las cuatro pautas informales: **1) Semántica clara**, **2) Sin anomalías**, **3) Pocos nulos** y **4) Sin tuplas espurias**.

| Tabla | Frase descriptiva («Cada fila es…») | ¿Qué pauta falla y por qué? |
| :--- | :--- | :--- |
| **`cliente`** | Cada fila es un cliente empresarial (nacional o de exportación) con sus datos de contacto y su información fiscal. | **Falla Pauta 3 (pocos nulos)** y parcialmente **Pauta 1 (semántica)**: al meter los dos subtipos en una sola tabla con `tipoCliente`, los 60 clientes nacionales dejan `idFiscalGlobal` y `paisReceptor` en `NULL`, y los 20 de exportación dejan `RFC`, `regimenFiscal` y `estadoOrigen` en `NULL` (180 celdas vacías). |
| **`transportista`** | Cada fila es una empresa transportista con su contacto, si opera nacional y/o internacionalmente, y sus permisos fiscales o aduanales. | **Falla Pauta 3 (pocos nulos)**: al juntar las modalidades nacional e internacional en una tabla, los 20 transportistas solo nacionales tienen `codigoAduanal` y `agenciaAduanal` en `NULL`, y los 6 solo internacionales tienen `RFC` en `NULL`. |
| **`producto`** | Cada fila es una presentación de aceite industrial del catálogo, con su modelo, línea comercial, costo, precio de lista y proveedor. | **Falla Pautas 1, 2 y 3**:<br>• **Pauta 1 y 2 (semántica y anomalías):** mezcla la presentación (`claveProducto`) con la regla de que cada modelo pertenece a una línea (`modeloProducto -> tipoProducto`). Como hay 4 presentaciones por modelo, `tipoProducto` se repite 4 veces: si cambia la línea de un modelo hay que editar 4 filas (*actualización*), no se puede registrar un modelo nuevo sin inventar una presentación (*inserción*) y si se borran sus 4 presentaciones se pierde a qué línea pertenecía el modelo (*borrado*).<br>• **Pauta 3 (pocos nulos):** de las 3 columnas de proveedor, siempre 2 quedan en `NULL` en cada fila (80 nulos en 40 filas). |
| **`sucursal`** | Cada fila es una planta o bodega receptora de un cliente, con el teléfono de su encargado y su dirección completa. | **Falla Pautas 1 y 2 (semántica y anomalías)**: repite en las 100 sucursales que una ciudad pertenece a un estado y a un país (`ciudad -> estado -> pais`, habiendo 51 ciudades y 31 estados) y que el país depende del cliente (`numeroCliente -> pais`). Si se corrige un estado o país hay que actualizar varias filas (*actualización*), no se puede dar de alta una ciudad sin sucursal (*inserción*) y al borrar la única sucursal de una ciudad se pierde su ubicación (*borrado*). |
| **`pedido`** | Cada fila es una orden de compra levantada por un cliente en una fecha dada, con su folio, estatus y si sigue activa. | **Cumple las 4 pautas**: habla solo del encabezado del pedido, no repite datos del cliente, no tiene ningún `NULL` y su PK `folio` evita tuplas espurias. |
| **`detalle`** | Cada fila es un renglón dentro de un pedido que indica qué producto se vendió, cuántas unidades y a qué costo y precio se pactó esa venta. | **Cumple las 4 pautas**: `costoProduccion` y `precioAplicado` no son redundantes con `producto` porque guardan el precio y costo *históricos* de esa venta específica (con el descuento del cliente), no el precio actual del catálogo. No tiene nulos. |
| **`envio`** | Cada fila es el despacho físico de un pedido mediante un transportista hacia una sucursal del cliente, con su guía, fecha y costo de flete. | **Falla ligeramente Pauta 2 (redundancia entre tablas)**: repite `numeroCliente` (que ya está en `pedido`) para completar la llave foránea compuesta hacia `sucursal(numeroCliente, claveSucursal)`. Dentro de `envio` no se repite en varias filas porque `folio` es `UNIQUE`. Cumple Pautas 1, 3 y 4. |

---

## Ejercicio 1.2. Las dependencias funcionales

### 1. Conjunto $F$ obtenido de las reglas del negocio

* **`cliente`**
  * $df_1$: `numeroCliente -> razonSocial, correoCliente, telefonoCliente, tipoCliente, RFC, regimenFiscal, estadoOrigen, idFiscalGlobal, paisReceptor` *(Cada número de cliente identifica a una única empresa cliente y sus datos fiscales/contacto).*
  * $df_2$: `correoCliente -> numeroCliente, razonSocial, telefonoCliente, tipoCliente` *(No se permite que dos clientes compartan el mismo correo de contacto principal).*
* **`transportista`**
  * $df_3$: `claveTransportista -> nombreEmpresa, telefonoAtencion, email, esNacional, esInternacional, RFC, codigoAduanal, agenciaAduanal` *(La clave del transportista identifica de forma única a la empresa y sus credenciales).*
* **`producto`**
  * $df_4$: `claveProducto -> modeloProducto, costoUnitarioUSD, precioUnitarioUSD, tipoProducto, provMaquinaria, provTransformador, provTransporte` *(Cada código de producto identifica una presentación única con su modelo, precios y proveedor).*
  * $df_5$: `modeloProducto -> tipoProducto` *(Cada modelo comercial pertenece a una sola línea: `OMNIGOLD`, `HYVOLT` o `HYPRENE`).*
  * $df_6$: `claveProducto, modeloProducto -> precioUnitarioUSD, tipoProducto` *(La clave de presentación junto con su modelo determinan su precio de lista y línea).*
* **`sucursal`**
  * $df_7$: `numeroCliente, claveSucursal -> nombrePlanta, telefonoEncargado, calle, numero, ciudad, estado, pais, CP` *(La clave de sucursal solo es única dentro de cada cliente; juntas identifican la planta y su dirección).*
  * $df_8$: `numeroCliente -> pais` *(Un cliente nacional solo tiene plantas en México y uno de exportación en su único país receptor).*
  * $df_9$: `ciudad -> estado, pais` *(En el padrón logístico, cada ciudad registrada pertenece a un estado y país).*
  * $df_{10}$: `estado -> pais` *(Cada estado o provincia pertenece a un único país).*
* **`pedido`**
  * $df_{11}$: `folio -> numeroCliente, estatus, dia, mes, anio, activo` *(El folio identifica cada orden de compra, quién la pidió, su fecha y estatus).*
* **`detalle`**
  * $df_{12}$: `folio, claveParcial -> claveProducto, costoProduccion, precioAplicado, cantidad` *(El folio del pedido más el número de renglón identifican la partida vendida y sus montos pactados).*
* **`envio`**
  * $df_{13}$: `numeroGuia -> folio, claveTransportista, numeroCliente, claveSucursal, costoFlete, dia, mes, anio` *(Cada número de guía identifica un envío y todos sus datos).*
  * $df_{14}$: `folio -> numeroGuia, claveTransportista, numeroCliente, claveSucursal, costoFlete, dia, mes, anio` *(Cada pedido tiene como máximo un envío, por lo que el folio también determina todos los datos del envío).*
  * $df_{15}$: `folio, numeroCliente -> claveSucursal, costoFlete` *(El folio y cliente de un envío determinan a qué sucursal llegó y cuánto costó el flete).*

---

### 2. Cierre de atributos paso a paso para hallar las claves candidatas

Buscamos en cada tabla los atributos que **nunca aparecen a la derecha** (deben ir a fuerza en toda clave candidata) y calculamos su cierre:

1. **`cliente`:** `numeroCliente` y `correoCliente` se determinan entre sí ($df_1, df_2$).
   * $\{numeroCliente\}^+$:
     * Base: $\{numeroCliente\}$
     * Por $df_1$: $\{numeroCliente, razonSocial, correoCliente, telefonoCliente, tipoCliente, RFC, regimenFiscal, estadoOrigen, idFiscalGlobal, paisReceptor\}$ (toda la tabla).
   * $\{correoCliente\}^+$:
     * Base: $\{correoCliente\}$
     * Por $df_2$: $\{correoCliente, numeroCliente, razonSocial, telefonoCliente, tipoCliente\}$
     * Por $df_1$ (ya teniendo `numeroCliente`): agrega `{RFC, regimenFiscal, estadoOrigen, idFiscalGlobal, paisReceptor}` (toda la tabla).
   * **Claves candidatas de `cliente`:** `{numeroCliente}` y `{correoCliente}`.

2. **`transportista`:** `claveTransportista` nunca está a la derecha.
   * $\{claveTransportista\}^+$: Base $\{claveTransportista\} \xrightarrow{df_3} \{claveTransportista, nombreEmpresa, telefonoAtencion, email, esNacional, esInternacional, RFC, codigoAduanal, agenciaAduanal\}$.
   * **Clave candidata de `transportista`:** `{claveTransportista}`.

3. **`producto`:** `claveProducto` nunca está a la derecha.
   * $\{claveProducto\}^+$: Base $\{claveProducto\} \xrightarrow{df_4} \{claveProducto, modeloProducto, costoUnitarioUSD, precioUnitarioUSD, tipoProducto, provMaquinaria, provTransformador, provTransporte\}$.
   * *(Si probamos $\{modeloProducto\}^+ = \{modeloProducto\} \xrightarrow{df_5} \{modeloProducto, tipoProducto\}$, vemos que no cubre la tabla).*
   * **Clave candidata de `producto`:** `{claveProducto}`.

4. **`sucursal`:** `numeroCliente` y `claveSucursal` nunca aparecen a la derecha.
   * Probando por separado: $\{numeroCliente\}^+ = \{numeroCliente, pais\}$ (por $df_8$) y $\{claveSucursal\}^+ = \{claveSucursal\}$. Ninguno basta por sí solo.
   * $\{numeroCliente, claveSucursal\}^+$:
     * Base: $\{numeroCliente, claveSucursal\}$
     * Por $df_8$: $\{numeroCliente, claveSucursal, pais\}$
     * Por $df_7$: $\{numeroCliente, claveSucursal, nombrePlanta, telefonoEncargado, calle, numero, ciudad, estado, pais, CP\}$.
   * **Clave candidata de `sucursal`:** `{numeroCliente, claveSucursal}`.

5. **`pedido`:** `folio` nunca está a la derecha.
   * $\{folio\}^+$: Base $\{folio\} \xrightarrow{df_{11}} \{folio, numeroCliente, estatus, dia, mes, anio, activo\}$.
   * **Clave candidata de `pedido`:** `{folio}`.

6. **`detalle`:** `folio` y `claveParcial` nunca están a la derecha.
   * Por separado: $\{folio\}^+ = \{folio\}$ y $\{claveParcial\}^+ = \{claveParcial\}$.
   * Juntos $\{folio, claveParcial\}^+$: Base $\{folio, claveParcial\} \xrightarrow{df_{12}} \{folio, claveParcial, claveProducto, costoProduccion, precioAplicado, cantidad\}$.
   * **Clave candidata de `detalle`:** `{folio, claveParcial}`.

7. **`envio`:** `numeroGuia` y `folio` se determinan mutuamente ($df_{13}, df_{14}$).
   * $\{numeroGuia\}^+$: Base $\{numeroGuia\} \xrightarrow{df_{13}} \{numeroGuia, folio, claveTransportista, numeroCliente, claveSucursal, costoFlete, dia, mes, anio\}$.
   * $\{folio\}^+$: Base $\{folio\} \xrightarrow{df_{14}} \{folio, numeroGuia, claveTransportista, numeroCliente, claveSucursal, costoFlete, dia, mes, anio\}$.
   * **Claves candidatas de `envio`:** `{numeroGuia}` y `{folio}`.

---

### 3. Reducción de $F$ a un conjunto mínimo (3 pasos)

#### Paso 1: Lados derechos simples
Separamos toda dependencia $X \to A, B, \dots$ para que tenga una sola columna a la derecha (por ejemplo, $df_9$ se separa en `ciudad -> estado` y `ciudad -> pais`; $df_7$ se separa en 8 flechas individuales desde `(numeroCliente, claveSucursal)`, etc.).

#### Paso 2: Quitar atributos sobrantes del lado izquierdo (en dependencias con $\ge 2$ atributos a la izquierda)
1. **En `producto` (`claveProducto, modeloProducto -> precioUnitarioUSD` y `claveProducto, modeloProducto -> tipoProducto`):**
   * ¿Sobra `modeloProducto`? Calculamos $\{claveProducto\}^+ = \{claveProducto, modeloProducto, costoUnitarioUSD, precioUnitarioUSD, tipoProducto, \dots\}$. Como `modeloProducto` (y los lados derechos) ya están en $\{claveProducto\}^+$, **`modeloProducto` sobra a la izquierda** y se elimina.
2. **En `sucursal` (`numeroCliente, claveSucursal -> pais`):**
   * ¿Sobra `claveSucursal`? Calculamos $\{numeroCliente\}^+$: por `numeroCliente -> pais`, $\{numeroCliente\}^+ = \{numeroCliente, pais\}$. Como `pais` ya está en $\{numeroCliente\}^+$, **`claveSucursal` sobra a la izquierda** en esa dependencia y queda solo `numeroCliente -> pais`. *(En las otras 7 dependencias de `sucursal`, ni $\{numeroCliente\}^+$ ni $\{claveSucursal\}^+$ contienen a los demás atributos, así que ahí no sobra nada).*
3. **En `detalle` (`folio, claveParcial -> ...`):**
   * Como $\{folio\}^+ = \{folio\}$ y $\{claveParcial\}^+ = \{claveParcial\}$, ningún atributo sobra a la izquierda.
4. **En `envio` (`folio, numeroCliente -> claveSucursal` y `folio, numeroCliente -> costoFlete`):**
   * ¿Sobra `numeroCliente`? Calculamos $\{folio\}^+$: por las dependencias de `folio` en `envio`, $\{folio\}^+$ contiene todos los atributos de `envio` (incluyendo `numeroCliente`, `claveSucursal` y `costoFlete`). Por tanto, **`numeroCliente` sobra a la izquierda** y se elimina.

#### Paso 3: Quitar dependencias redundantes
Probamos quitar cada dependencia sospechosa $f$ y calculamos el cierre del lado izquierdo en $F - \{f\}$:
1. **En `cliente`: se eliminan `correoCliente -> razonSocial`, `correoCliente -> telefonoCliente` y `correoCliente -> tipoCliente`.**
   * *Justificación con cierre:* Sin usar esas tres flechas, calculamos $\{correoCliente\}^+ = \{correoCliente\} \xrightarrow{\text{correoCliente}\to\text{numeroCliente}} \{correoCliente, numeroCliente\} \xrightarrow{df_1} \{..., razonSocial, telefonoCliente, tipoCliente\}$. Como se siguen alcanzando a través de `numeroCliente`, son redundantes.
2. **En `producto`: se elimina `claveProducto -> tipoProducto`.**
   * *Justificación con cierre:* En $F - \{\text{claveProducto} \to \text{tipoProducto}\}$, calculamos $\{claveProducto\}^+ = \{claveProducto\} \xrightarrow{\text{claveProducto}\to\text{modeloProducto}} \{claveProducto, modeloProducto\} \xrightarrow{\text{modeloProducto}\to\text{tipoProducto}} \{claveProducto, modeloProducto, tipoProducto\}$. Como `tipoProducto` sigue en el cierre, es redundante.
3. **En `sucursal`: se eliminan `ciudad -> pais` y `numeroCliente, claveSucursal -> estado`.**
   * *Justificación de `ciudad -> pais`:* Sin ella, $\{ciudad\}^+ = \{ciudad\} \xrightarrow{\text{ciudad}\to\text{estado}} \{ciudad, estado\} \xrightarrow{\text{estado}\to\text{pais}} \{ciudad, estado, pais\}$. Contiene a `pais`, así que es redundante.
   * *Justificación de `numeroCliente, claveSucursal -> estado`:* Sin ella, $\{numeroCliente, claveSucursal\}^+ = \{numeroCliente, claveSucursal\} \xrightarrow{\to\text{ciudad}} \{..., ciudad\} \xrightarrow{\text{ciudad}\to\text{estado}} \{..., ciudad, estado\}$. Contiene a `estado`, así que es redundante.
4. **En `envio`: se eliminan las 7 flechas directas `folio -> claveTransportista, numeroCliente, claveSucursal, costoFlete, dia, mes, anio` (conservando solo `folio -> numeroGuia`).**
   * *Justificación con cierre:* Sin esas 7 flechas, $\{folio\}^+ = \{folio\} \xrightarrow{\text{folio}\to\text{numeroGuia}} \{folio, numeroGuia\} \xrightarrow{df_{13}} \{folio, numeroGuia, claveTransportista, numeroCliente, claveSucursal, costoFlete, dia, mes, anio\}$. Todas se deducen pasando por `numeroGuia`.

#### Conjunto mínimo resultante ($F_{\min}$)
* **`cliente`:** `numeroCliente -> razonSocial`, `numeroCliente -> correoCliente`, `numeroCliente -> telefonoCliente`, `numeroCliente -> tipoCliente`, `numeroCliente -> RFC`, `numeroCliente -> regimenFiscal`, `numeroCliente -> estadoOrigen`, `numeroCliente -> idFiscalGlobal`, `numeroCliente -> paisReceptor`, y `correoCliente -> numeroCliente`.
* **`transportista`:** `claveTransportista -> nombreEmpresa`, `claveTransportista -> telefonoAtencion`, `claveTransportista -> email`, `claveTransportista -> esNacional`, `claveTransportista -> esInternacional`, `claveTransportista -> RFC`, `claveTransportista -> codigoAduanal`, `claveTransportista -> agenciaAduanal`.
* **`producto`:** `claveProducto -> modeloProducto`, `claveProducto -> costoUnitarioUSD`, `claveProducto -> precioUnitarioUSD`, `claveProducto -> provMaquinaria`, `claveProducto -> provTransformador`, `claveProducto -> provTransporte`, y `modeloProducto -> tipoProducto`.
* **`sucursal`:** `numeroCliente, claveSucursal -> nombrePlanta`, `numeroCliente, claveSucursal -> telefonoEncargado`, `numeroCliente, claveSucursal -> calle`, `numeroCliente, claveSucursal -> numero`, `numeroCliente, claveSucursal -> ciudad`, `numeroCliente, claveSucursal -> CP`, `numeroCliente -> pais`, `ciudad -> estado`, y `estado -> pais`.
* **`pedido`:** `folio -> numeroCliente`, `folio -> estatus`, `folio -> dia`, `folio -> mes`, `folio -> anio`, `folio -> activo`.
* **`detalle`:** `folio, claveParcial -> claveProducto`, `folio, claveParcial -> costoProduccion`, `folio, claveParcial -> precioAplicado`, `folio, claveParcial -> cantidad`.
* **`envio`:** `numeroGuia -> folio`, `numeroGuia -> claveTransportista`, `numeroGuia -> numeroCliente`, `numeroGuia -> claveSucursal`, `numeroGuia -> costoFlete`, `numeroGuia -> dia`, `numeroGuia -> mes`, `numeroGuia -> anio`, y `folio -> numeroGuia`.

---

### 4. Intercambio con otro equipo y demostración de equivalencia ($F \equiv G$)

Intercambiamos las reglas de nuestro dominio con otro equipo, que escribió su conjunto **$G$**. Coincidimos igual en `transportista`, `pedido` y `detalle`, pero en las demás tablas ellos escribieron:
* En `cliente`: $g_1$: `numeroCliente -> correoCliente` y $g_2$: `correoCliente -> numeroCliente, razonSocial, telefonoCliente, tipoCliente, RFC, regimenFiscal, estadoOrigen, idFiscalGlobal, paisReceptor`.
* En `producto`: $g_3$: `claveProducto -> modeloProducto, costoUnitarioUSD, precioUnitarioUSD, tipoProducto, provMaquinaria, provTransformador, provTransporte` y $g_4$: `modeloProducto -> tipoProducto`.
* En `sucursal`: $g_5$: `numeroCliente, claveSucursal -> nombrePlanta, telefonoEncargado, calle, numero, ciudad, estado, pais, CP`, $g_6$: `numeroCliente -> pais`, $g_7$: `ciudad -> estado, pais` y $g_8$: `estado -> pais`.
* En `envio`: $g_9$: `numeroGuia -> folio` y $g_{10}$: `folio -> numeroGuia, claveTransportista, numeroCliente, claveSucursal, costoFlete, dia, mes, anio`.

**Demostración de que $F$ cubre a $G$ ($F \models G$):**
* $[\{correoCliente\}]_F^+ = \{correoCliente\} \xrightarrow{\text{en } F} \{correoCliente, numeroCliente\} \xrightarrow{\text{en } F} \{\text{todos los atributos de cliente}\}$, por lo que $F$ implica $g_1$ y $g_2$.
* $[\{claveProducto\}]_F^+ = \{claveProducto, modeloProducto, costoUnitarioUSD, precioUnitarioUSD, prov...\} \xrightarrow{\text{modeloProducto}\to\text{tipoProducto}} \{..., tipoProducto\}$, por lo que $F$ implica $g_3$ y $g_4$.
* $[\{numeroCliente, claveSucursal\}]_F^+ = \{..., ciudad\} \xrightarrow{\text{ciudad}\to\text{estado}} \{..., estado\} \xrightarrow{\text{estado}\to\text{pais}} \{..., pais\}$, y $[\{ciudad\}]_F^+ = \{ciudad, estado, pais\}$, por lo que $F$ implica $g_5, g_6, g_7, g_8$.
* $[\{folio\}]_F^+ = \{folio\} \xrightarrow{\text{folio}\to\text{numeroGuia}} \{folio, numeroGuia\} \xrightarrow{\text{en } F} \{\text{todos los atributos de envio}\}$, implicando $g_9$ y $g_{10}$.

**Demostración de que $G$ cubre a $F$ ($G \models F$):**
* $[\{numeroCliente\}]_G^+ = \{numeroCliente\} \xrightarrow{g_1} \{numeroCliente, correoCliente\} \xrightarrow{g_2} \{\text{todos los atributos de cliente}\}$, cubriendo todas las flechas de `cliente` en $F$.
* En `producto` y `sucursal`, todas las flechas de $F_{\min}$ son subconjuntos directos de $g_3, g_4, g_5, g_6, g_7, g_8$.
* En `envio`, $[\{numeroGuia\}]_G^+ = \{numeroGuia\} \xrightarrow{g_9} \{numeroGuia, folio\} \xrightarrow{g_{10}} \{\text{todos los atributos de envio}\}$, cubriendo todas las flechas de `numeroGuia` en $F$.

Como $F \models G$ y $G \models F$, **ambos conjuntos son equivalentes ($F \equiv G$)**.

---

## Ejercicio 1.3. Las formas normales

### 1. Forma normal actual de cada tabla

Todas nuestras tablas están al menos en **1FN** porque no hay celdas con listas ni atributos compuestos sin separar.

* **`cliente` — BCNF:** Sus claves candidatas son `{numeroCliente}` y `{correoCliente}` (1 solo atributo, cumple 2FN). Los únicos determinantes en $F_{\text{cliente}}$ son esos dos mismos atributos (ambos superclaves), por lo que cumple 3FN y BCNF.
* **`transportista` — BCNF:** Su única clave candidata es `{claveTransportista}` y es el único determinante de la tabla.
* **`pedido` — BCNF:** Su única clave candidata es `{folio}` y determina a todas las demás columnas.
* **`detalle` — BCNF:** Su clave candidata es `{folio, claveParcial}`. Ninguna columna depende solo de `folio` ni solo de `claveParcial` (cumple 2FN), ni de `claveProducto` (porque el costo y precio guardados aquí son los montos históricos de esa partida, no los del catálogo). El único determinante es la clave completa.
* **`envio` — BCNF:** Sus dos determinantes (`numeroGuia` y `folio`) son claves candidatas de la tabla, así que todo determinante es superclave.
* **`producto` — 2FN (No cumple 3FN):** Su clave candidata `{claveProducto}` es de una sola columna, por lo que está en **2FN** (no puede tener dependencias parciales). Falla **3FN** por la dependencia transitiva `claveProducto -> modeloProducto -> tipoProducto`, donde `modeloProducto` no es superclave y `tipoProducto` no es atributo primo.
* **`sucursal` — 1FN (No cumple 2FN ni 3FN):** Su clave candidata es compuesta `{numeroCliente, claveSucursal}`. Falla **2FN** por la dependencia parcial `numeroCliente -> pais` (`pais` depende solo de una parte de la clave). Además, falla **3FN** por las dependencias transitivas `ciudad -> estado` y `estado -> pais`.

---

### 2. Paso a 3FN y comprobación de BCNF

#### A) Tabla `producto`
* **Paso único (eliminar `modeloProducto -> tipoProducto`):**
  * Creamos **`modelo_producto(modeloProducto [PK], tipoProducto)`**.
  * Quitamos `tipoProducto` de `producto`, quedando **`producto(claveProducto [PK], modeloProducto [FK], costoUnitarioUSD, precioUnitarioUSD, provMaquinaria, provTransformador, provTransporte)`**.
* **Comprobación de BCNF:** En `modelo_producto` el único determinante es `modeloProducto` (su PK) y en `producto` el único determinante es `claveProducto` (su PK). Ambas quedan en **3FN y BCNF**.

#### B) Tabla `sucursal`
* **Paso 1 (llevar a 2FN y eliminar `estado -> pais` y `numeroCliente -> pais`):**
  * Creamos **`estado_ubicacion(estado [PK], pais)`** y quitamos `pais` de `sucursal` (quedando temporalmente `sucursal_sin_pais` con `estado` como FK). Al salir `pais` de `sucursal`, desaparece la dependencia parcial `numeroCliente -> pais` y la tabla sube a **2FN**.
* **Paso 2 (llevar de 2FN a 3FN eliminando `ciudad -> estado`):**
  * Creamos **`ciudad_ubicacion(ciudad [PK], estado [FK])`** y quitamos `estado` de `sucursal`, dejando `ciudad` como FK:
  * **`sucursal(numeroCliente [PK, FK], claveSucursal [PK], nombrePlanta, telefonoEncargado, calle, numero, ciudad [FK], CP)`**.
* **Comprobación de BCNF:** En `estado_ubicacion` el único determinante es `estado` (PK); en `ciudad_ubicacion` es `ciudad` (PK); y en `sucursal` es `(numeroCliente, claveSucursal)` (PK). Las tres quedan en **3FN y BCNF**.

> **Nota sobre cuándo 3FN no llega a BCNF (qué dependencia se perdería):** Nuestras tablas llegaron a BCNF sin perder dependencias. Si en una tabla de direcciones tuviéramos las reglas `(ciudad, calle) -> CP` y `CP -> ciudad`, estaría en **3FN** (porque `ciudad` es parte de la clave candidata `{ciudad, calle}`) pero no en **BCNF** (porque `CP` no es superclave). Si la partiéramos a BCNF en `(CP, ciudad)` y `(CP, calle)`, **se perdería la dependencia `(ciudad, calle) -> CP`**. En ese caso nos quedaríamos en 3FN para no perder esa regla.

---

### 3. Comprobación de reunión sin pérdida y preservación de dependencias

Aplicamos la **prueba de los atributos comunes** ($R_1 \cap R_2$ debe ser superclave de $R_1$ o de $R_2$):

1. **Descomposición de `producto` en $R_1(\text{modelo\_producto})$ y $R_2(\text{producto})$:**
   * Atributo común: $R_1 \cap R_2 = \{modeloProducto\}$.
   * Cierre: $\{modeloProducto\}^+ = \{modeloProducto, tipoProducto\} = R_1$. Como determina toda $R_1$, **tiene reunión sin pérdida**.
   * **Preserva dependencias:** `modeloProducto -> tipoProducto` vive en $R_1$ y las dependencias de `claveProducto` viven en $R_2$.

2. **Descomposición de `sucursal` en $S_1(\text{estado\_ubicacion})$, $S_2(\text{ciudad\_ubicacion})$ y $S_3(\text{sucursal})$:**
   * Paso 1 ($S_1$ y $S_{\text{temp}}$): $S_1 \cap S_{\text{temp}} = \{estado\}$, y $\{estado\}^+ = \{estado, pais\} = S_1 \implies$ **reunión sin pérdida**.
   * Paso 2 ($S_2$ y $S_3$): $S_2 \cap S_3 = \{ciudad\}$, y $\{ciudad\}^+ = \{ciudad, estado\} = S_2 \implies$ **reunión sin pérdida**.
   * **Preserva dependencias:** `estado -> pais` queda en $S_1$, `ciudad -> estado` queda en $S_2$ y `(numeroCliente, claveSucursal) -> ...` queda en $S_3$ (mientras que el país del cliente ya está guardado en `cliente` y se recupera por transitividad $ciudad \to estado \to pais$).

---

### 4. Migración SQL sobre la base poblada

Archivo ejecutado por el contenedor: [`practica6-8/migraciones/003-normalizacion.sql`](./migraciones/003-normalizacion.sql). Mueve los renglones existentes de `producto` y `sucursal` a las tablas nuevas con `INSERT INTO ... SELECT DISTINCT ...` antes de borrar las columnas redundantes:

```sql
BEGIN;

-- 1. Tabla modelo_producto a partir de los datos existentes en producto (10 modelos)
CREATE TABLE modelo_producto (
  modeloproducto VARCHAR(30) NOT NULL,
  tipoproducto   VARCHAR(10) NOT NULL,
  CONSTRAINT pk_modelo_producto PRIMARY KEY (modeloproducto),
  CONSTRAINT ck_modelo_producto_catalogo CHECK (modeloproducto IN (
    'HYGOLD 100', 'HYGOLD 5000BS', 'HYGOLD L-2000',
    'HYPRENE BO150', 'HYPRENE L2000', 'HYPRENE P150 BS',
    'HYVOLT II', 'OMNIGOLD A12', 'OMNIGOLD P100N', 'OMNIGOLD P220N'
  )),
  CONSTRAINT ck_modelo_tipo_producto CHECK (tipoproducto IN ('OMNIGOLD', 'HYVOLT', 'HYPRENE')),
  CONSTRAINT ck_modelo_correspondencia_tipo CHECK (
    ((modeloproducto LIKE 'HYGOLD%' OR modeloproducto LIKE 'OMNIGOLD%') AND tipoproducto = 'OMNIGOLD')
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
  FOREIGN KEY (modeloproducto) REFERENCES modelo_producto (modeloproducto)
  ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE producto DROP CONSTRAINT ck_producto_modelo_tipo;
ALTER TABLE producto DROP CONSTRAINT ck_producto_modelo;
ALTER TABLE producto DROP CONSTRAINT ck_subtipo_producto;
ALTER TABLE producto DROP CONSTRAINT ck_tipo_producto;

ALTER TABLE producto
  ADD CONSTRAINT ck_subtipo_producto_por_modelo CHECK (
    ((modeloproducto LIKE 'HYGOLD%' OR modeloproducto LIKE 'OMNIGOLD%')
      AND provmaquinaria IS NOT NULL AND provtransformador IS NULL AND provtransporte IS NULL)
    OR (modeloproducto LIKE 'HYVOLT%'
      AND provtransformador IS NOT NULL AND provmaquinaria IS NULL AND provtransporte IS NULL)
    OR (modeloproducto LIKE 'HYPRENE%'
      AND provtransporte IS NOT NULL AND provmaquinaria IS NULL AND provtransformador IS NULL)
  );

ALTER TABLE producto DROP COLUMN tipoproducto;

-- 2. Tablas estado_ubicacion (31 estados) y ciudad_ubicacion (51 ciudades) desde sucursal
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
    ON DELETE RESTRICT ON UPDATE CASCADE
);

INSERT INTO ciudad_ubicacion (ciudad, estado)
SELECT DISTINCT ciudad, estado
FROM sucursal
WHERE ciudad IS NOT NULL AND estado IS NOT NULL
ORDER BY ciudad;

ALTER TABLE sucursal ALTER COLUMN ciudad SET NOT NULL;

ALTER TABLE sucursal
  ADD CONSTRAINT fk_sucursal_ciudad
  FOREIGN KEY (ciudad) REFERENCES ciudad_ubicacion (ciudad)
  ON DELETE RESTRICT ON UPDATE CASCADE;

ALTER TABLE sucursal DROP COLUMN estado;
ALTER TABLE sucursal DROP COLUMN pais;

COMMIT;
```
