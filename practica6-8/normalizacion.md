# Parte 1. Dependencias funcionales y normalización — Proyecto propio (ERGON)

Partimos del esquema relacional de nuestro proyecto propio (**ERGON**, comercialización y logística de aceites industriales), tal como quedó después de aplicar el esquema base y las migraciones de las Prácticas 4 y 5 (`001-dominios.sql` y `002-referencias.sql`), poblado con los 2,702 registros del archivo `base_datos_pedidos2.xlsx`.

El esquema actual consta de siete tablas:
* `cliente(numeroCliente, razonSocial, correoCliente, telefonoCliente, tipoCliente, RFC, regimenFiscal, estadoOrigen, idFiscalGlobal, paisReceptor)`
* `transportista(claveTransportista, nombreEmpresa, telefonoAtencion, email, esNacional, esInternacional, RFC, codigoAduanal, agenciaAduanal)`
* `producto(claveProducto, modeloProducto, costoUnitarioUSD, precioUnitarioUSD, tipoProducto, provMaquinaria, provTransformador, provTransporte)`
* `sucursal(numeroCliente, claveSucursal, nombrePlanta, telefonoEncargado, calle, numero, ciudad, estado, pais, CP)`
* `pedido(folio, numeroCliente, estatus, dia, mes, anio, activo)`
* `detalle(folio, claveParcial, claveProducto, costoProduccion, precioAplicado, cantidad)`
* `envio(numeroGuia, folio, claveTransportista, numeroCliente, claveSucursal, costoFlete, dia, mes, anio)`

---

## Ejercicio 1.1. Pautas de diseño

A continuación escribimos para cada una de las siete tablas la frase que describe qué representa un renglón («cada fila es...») y la revisamos contra las cuatro pautas informales de diseño:
1. **Semántica clara:** que la tabla no mezcle atributos de varias entidades o conceptos distintos.
2. **Sin anomalías:** que no repita información innecesaria que provoque anomalías al insertar, borrar o actualizar.
3. **Pocos nulos:** evitar columnas que queden en `NULL` en una gran parte de las filas.
4. **Sin tuplas espurias:** que las tablas se relacionen mediante claves primarias y foráneas bien definidas para no inventar filas falsas al hacer un `JOIN`.

---

### 1. Tabla `cliente`
* **Frase descriptiva:** *«Cada fila es un cliente empresarial (B2B) registrado en ERGON, con sus datos generales de contacto y, dependiendo de si es nacional o de exportación, sus datos fiscales mexicanos o sus datos fiscales internacionales.»*
* **Revisión contra las 4 pautas:**
  * **Semántica clara (Falla parcialmente):** En la Práctica 3 transformamos la jerarquía de especialización (`clienteNacional` y `clienteExportacion`) usando una sola tabla con la columna discriminadora `tipoCliente`. Por eso en la misma fila conviven atributos exclusivos de clientes mexicanos (`RFC`, `regimenFiscal`, `estadoOrigen`) con atributos exclusivos de clientes extranjeros (`idFiscalGlobal`, `paisReceptor`).
  * **Sin anomalías (Cumple):** No repite información entre filas porque cada cliente se registra una sola vez y sus datos dependen directamente de su clave (`numeroCliente`).
  * **Pocos nulos (Falla):** Esta es la pauta que más claramente incumple. De los 80 clientes cargados, los 60 clientes nacionales tienen `idFiscalGlobal` y `paisReceptor` en `NULL` (120 celdas vacías), mientras que los 20 clientes de exportación tienen `RFC`, `regimenFiscal` y `estadoOrigen` en `NULL` (60 celdas vacías). Es decir, por diseño siempre hay 2 o 3 columnas nulas en cada fila.
  * **Sin tuplas espurias (Cumple):** Se identifica con la clave primaria `numeroCliente`, por lo que al reunirla con `pedido` o `sucursal` no genera filas falsas.

---

### 2. Tabla `transportista`
* **Frase descriptiva:** *«Cada fila es una empresa transportista contratada por ERGON para realizar envíos, con sus medios de contacto, dos banderas que indican si opera en rutas nacionales y/o internacionales, y los permisos fiscales o aduanales de cada modalidad.»*
* **Revisión contra las 4 pautas:**
  * **Semántica clara (Falla parcialmente):** Igual que en `cliente`, reúne en una sola tabla la superclase `transportista` y sus dos subtipos solapados (`transportistaNacional` y `transportistaInternacional`).
  * **Sin anomalías (Cumple):** Cada empresa transportista aparece en una sola fila identificada por `claveTransportista`; no se repiten datos de agencias en un mismo transportista ni hay anomalías de actualización.
  * **Pocos nulos (Falla):** De los 30 transportistas de la base, 20 son únicamente nacionales y tienen `codigoAduanal` y `agenciaAduanal` en `NULL` (40 celdas nulas), y 6 son únicamente internacionales y tienen `RFC` en `NULL`. Además, `telefonoAtencion` tiene 5 nulos y `email` 1 nulo por ser datos de contacto opcionales.
  * **Sin tuplas espurias (Cumple):** Su clave primaria `claveTransportista` es la que referencia `envio`, garantizando reuniones exactas.

---

### 3. Tabla `producto`
* **Frase descriptiva:** *«Cada fila es una presentación específica de aceite industrial del catálogo de ERGON, junto con el modelo comercial al que pertenece, su línea de producto, su costo y precio de lista en dólares, y el proveedor especializado según su línea.»*
* **Revisión contra las 4 pautas:**
  * **Semántica clara (Falla):** Mezcla en una misma tabla dos hechos distintos: los datos de cada presentación individual (`claveProducto`, `costoUnitarioUSD`, `precioUnitarioUSD`) y el hecho de a qué línea comercial pertenece cada modelo (`modeloProducto -> tipoProducto`). Además, junta las tres especializaciones de producto (`OMNIGOLD`, `HYVOLT`, `HYPRENE`) en la misma tabla.
  * **Sin anomalías (Falla):** En la Práctica 4 se incorporó la columna `modeloProducto` (existen 10 modelos y cada uno tiene 4 presentaciones, dando los 40 productos). Como la línea comercial (`tipoProducto`) depende del modelo (`modeloProducto`), ese dato se repite 4 veces por cada modelo, provocando las tres anomalías:
    * *Anomalía de actualización:* si queremos cambiar la clasificación de `tipoProducto` para el modelo `'HYGOLD 100'`, tenemos que modificar 4 filas distintas (`HG1-01` a `HG1-04`); si se nos pasa una, la base queda con datos contradictorios.
    * *Anomalía de inserción:* no podemos registrar en la base un nuevo modelo comercial y a qué línea pertenece si todavía no tenemos dada de alta al menos una presentación con `claveProducto`, costo y precio.
    * *Anomalía de borrado:* si eliminamos las 4 presentaciones del modelo `'HYVOLT II'`, perdemos por completo el registro de que el modelo `'HYVOLT II'` existe y pertenece a la línea `'HYVOLT'`.
  * **Pocos nulos (Falla):** Cada producto pertenece a una sola línea y solo llena una de las tres columnas de proveedor (`provMaquinaria`, `provTransformador`, `provTransporte`), dejando las otras dos en `NULL`. En las 40 filas del catálogo, esto produce $40 \times 2 = 80$ celdas en `NULL` obligatorias.
  * **Sin tuplas espurias (Cumple):** Su clave primaria `claveProducto` conecta limpiamente con `detalle`.

---

### 4. Tabla `sucursal`
* **Frase descriptiva:** *«Cada fila es una planta, bodega o almacén de recepción que pertenece a un cliente de ERGON, con los datos de su encargado y su dirección completa (calle, número, código postal, ciudad, estado y país).»*
* **Revisión contra las 4 pautas:**
  * **Semántica clara (Falla):** Además de los datos propios de la planta (`nombrePlanta`, `telefonoEncargado`, `calle`, `numero`, `CP`), guarda en la misma fila las relaciones geográficas entre `ciudad`, `estado` y `pais`, y repite el `pais` que en realidad está determinado por el cliente.
  * **Sin anomalías (Falla):** En nuestras 100 sucursales hay varias plantas ubicadas en la misma ciudad y estado (hay 100 sucursales repartidas en 51 ciudades y 31 estados/provincias). Guardar `ciudad`, `estado` y `pais` directamente en `sucursal` genera redundancia y anomalías:
    * *Anomalía de actualización:* si se corrige el nombre de un estado o país para una ciudad (por ejemplo, `'Lázaro Cárdenas'` en `'Michoacán'`, `'México'`), hay que actualizar todas las sucursales de esa ciudad para no dejar la misma ciudad asignada a dos estados distintos.
    * *Anomalía de inserción:* no podemos tener registrado en el catálogo qué ciudades y estados atiende la logística de ERGON hasta que un cliente abra una sucursal ahí.
    * *Anomalía de borrado:* si un cliente cierra la única sucursal que había en cierta ciudad (por ejemplo, en `'Bilbao'`, `'País Vasco'`, `'España'`), se borra también la relación entre esa ciudad, su comunidad/estado y su país.
  * **Pocos nulos (Cumple):** Solo tiene 15 valores `NULL` en `telefonoEncargado`, lo cual es normal porque no todas las bodegas reportan un teléfono directo del encargado. Todas las demás columnas están llenas en los 100 registros.
  * **Sin tuplas espurias (Cumple):** Su clave primaria compuesta `(numeroCliente, claveSucursal)` se usa completa como llave foránea en `envio`.

---

### 5. Tabla `pedido`
* **Frase descriptiva:** *«Cada fila es una orden de compra realizada por un cliente en una fecha específica, con su número de folio único, su estatus actual y una bandera que indica si el registro sigue activo.»*
* **Revisión contra las 4 pautas:**
  * **Semántica clara (Cumple):** Solo contiene datos del encabezado del pedido; para saber quién compró solo guarda la referencia `numeroCliente` y los artículos comprados van aparte en `detalle`.
  * **Sin anomalías (Cumple):** Cada pedido se registra una sola vez por su `folio` y ningún atributo depende de otro que no sea el folio.
  * **Pocos nulos (Cumple):** Tiene cero valores `NULL` en los 500 registros (todas sus columnas son `NOT NULL`).
  * **Sin tuplas espurias (Cumple):** Se une por `folio` (o `(folio, numeroCliente)`) con `detalle` y `envio` sin producir tuplas falsas.

---

### 6. Tabla `detalle`
* **Frase descriptiva:** *«Cada fila es un renglón o partida dentro de un pedido, que registra qué producto se compró, en qué cantidad y cuál fue el costo de producción y el precio unitario aplicado en esa venta en particular.»*
* **Revisión contra las 4 pautas:**
  * **Semántica clara (Cumple):** Representa únicamente un renglón de compra dentro de un pedido.
  * **Sin anomalías (Cumple):** Es importante aclarar que `costoProduccion` y `precioAplicado` **no son redundantes** respecto a `costoUnitarioUSD` y `precioUnitarioUSD` de la tabla `producto`. En `producto` se guarda el precio de lista actual del catálogo, mientras que en `detalle` se guarda el costo del lote y el precio histórico que se le cobró al cliente en ese pedido específico (aplicando su descuento). Si mañana sube el precio de lista en `producto`, los pedidos pasados en `detalle` no deben cambiar.
  * **Pocos nulos (Cumple):** No tiene ningún valor `NULL` en los 1,500 renglones.
  * **Sin tuplas espurias (Cumple):** Se identifica con la clave primaria compuesta `(folio, claveParcial)` y referencia a `pedido(folio)` y `producto(claveProducto)`.

---

### 7. Tabla `envio`
* **Frase descriptiva:** *«Cada fila es el envío físico de un pedido realizado por un transportista hacia una sucursal del cliente, identificado por su número de guía, con su costo de flete y la fecha en que salió.»*
* **Revisión contra las 4 pautas:**
  * **Semántica clara (Cumple):** Representa el despacho logístico que vincula el pedido, el transportista y la sucursal de entrega.
  * **Sin anomalías (Falla ligeramente por redundancia entre tablas):** Como la clave primaria de `sucursal` es compuesta `(numeroCliente, claveSucursal)`, la tabla `envio` necesita guardar `numeroCliente` además de `folio`. Pero como en `pedido` cada `folio` ya tiene asignado su `numeroCliente`, este dato queda repetido entre `pedido` y `envio` (motivo por el cual en la Práctica 5 agregamos la FK compuesta `(folio, numeroCliente)` hacia `pedido` para evitar que alguien actualice el cliente en un lado y quede distinto en el otro). Dentro de la tabla `envio` por sí sola no se repite en varias filas porque cada `folio` aparece a lo más una vez (`UNIQUE`).
  * **Pocos nulos (Cumple):** Tiene cero valores `NULL` en sus 452 filas (los pedidos que aún no se envían o fueron cancelados simplemente no tienen fila en `envio`, en vez de meter filas llenas de nulos).
  * **Sin tuplas espurias (Cumple):** Sus llaves foráneas apuntan a las claves primarias/únicas de `pedido`, `transportista` y `sucursal`.

---

### Resumen del Ejercicio 1.1

| Tabla | Pauta 1: Semántica clara | Pauta 2: Sin anomalías | Pauta 3: Pocos nulos | Pauta 4: Sin tuplas espurias | Resumen de qué falla y por qué |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **`cliente`** | Parcial | Cumple | **Falla** | Cumple | Falla **pocos nulos**: al juntar clientes nacionales y de exportación en una tabla, siempre quedan 2 o 3 columnas fiscales en `NULL` por fila (180 celdas nulas). |
| **`transportista`** | Parcial | Cumple | **Falla** | Cumple | Falla **pocos nulos**: al juntar las modalidades nacional e internacional en una sola tabla, quedan en `NULL` los permisos de la modalidad que no aplica. |
| **`producto`** | **Falla** | **Falla** | **Falla** | Cumple | Falla **semántica y anomalías** porque repite `modeloProducto -> tipoProducto` en las 4 presentaciones de cada modelo; falla **pocos nulos** porque 2 de las 3 columnas de proveedor siempre son `NULL`. |
| **`sucursal`** | **Falla** | **Falla** | Cumple | Cumple | Falla **semántica y anomalías** porque guarda en cada planta que `ciudad -> estado -> pais` y que `numeroCliente -> pais`, repitiendo datos geográficos en las 100 sucursales. |
| **`pedido`** | Cumple | Cumple | Cumple | Cumple | Cumple las cuatro pautas. |
| **`detalle`** | Cumple | Cumple | Cumple | Cumple | Cumple las cuatro pautas (el costo y precio guardados son históricos por venta). |
| **`envio`** | Cumple | Parcial | Cumple | Cumple | Repite `numeroCliente` respecto a `pedido` para poder armar la FK compuesta a `sucursal`, aunque dentro de `envio` cada `folio` es único. |

---

## Ejercicio 1.2. Las dependencias funcionales

### 1. Conjunto $F$ de dependencias funcionales obtenido de las reglas del negocio

A continuación listamos el conjunto $F$ de dependencias funcionales de nuestro esquema. Todas las dependencias provienen de las **reglas del negocio de ERGON** (documentadas en los requisitos ampliados y en las restricciones del dominio) y no de coincidencias casuales en los renglones de ejemplo:

#### Tabla `cliente`
* **$df_{1}$:** `numeroCliente -> razonSocial, correoCliente, telefonoCliente, tipoCliente, RFC, regimenFiscal, estadoOrigen, idFiscalGlobal, paisReceptor`
  * *Regla del negocio:* A cada cliente de ERGON se le asigna un número de cliente único que identifica su razón social, sus datos de contacto, si es nacional o de exportación y sus datos fiscales.
* **$df_{2}$:** `correoCliente -> numeroCliente, razonSocial, telefonoCliente, tipoCliente`
  * *Regla del negocio:* El correo electrónico de contacto principal es único por cliente (`uq_cliente_correo`); dos clientes distintos no pueden registrarse con el mismo correo institucional.

#### Tabla `transportista`
* **$df_{3}$:** `claveTransportista -> nombreEmpresa, telefonoAtencion, email, esNacional, esInternacional, RFC, codigoAduanal, agenciaAduanal`
  * *Regla del negocio:* Cada empresa transportista tiene una clave única en el padrón de ERGON que determina su razón comercial, contacto, modalidades autorizadas y registros fiscales/aduanales.

#### Tabla `producto`
* **$df_{4}$:** `claveProducto -> modeloProducto, costoUnitarioUSD, precioUnitarioUSD, tipoProducto, provMaquinaria, provTransformador, provTransporte`
  * *Regla del negocio:* Cada código de producto identifica una presentación única del catálogo con su modelo comercial, su costo unitario, su precio de lista, su línea comercial y el proveedor de su línea.
* **$df_{5}$:** `modeloProducto -> tipoProducto`
  * *Regla del negocio:* Cada modelo de aceite industrial pertenece a una y solo una de las tres líneas comerciales de ERGON (`OMNIGOLD`, `HYVOLT` o `HYPRENE`), regla que incluso está impuesta en la base mediante la restricción `ck_producto_modelo_tipo`.
* **$df_{6}$:** `claveProducto, modeloProducto -> precioUnitarioUSD, tipoProducto`
  * *Regla del negocio:* Al especificar la clave de presentación junto con su modelo comercial, quedan determinados su precio unitario de catálogo y la línea de producto a la que pertenece.

#### Tabla `sucursal`
* **$df_{7}$:** `numeroCliente, claveSucursal -> nombrePlanta, telefonoEncargado, calle, numero, ciudad, estado, pais, CP`
  * *Regla del negocio:* `sucursal` es una entidad débil: la clave de sucursal (`S01`, `S02`, etc.) se repite entre clientes distintos, pero combinada con el `numeroCliente` identifica a una única planta con su encargado y su domicilio completo.
* **$df_{8}$:** `numeroCliente -> pais`
  * *Regla del negocio:* Un cliente nacional solo tiene plantas receptoras en México y un cliente de exportación recibe toda su mercancía en su único país receptor registrado; por lo tanto, el cliente determina el país donde se ubican sus sucursales.
* **$df_{9}$:** `ciudad -> estado, pais`
  * *Regla del negocio:* En el catálogo logístico de zonas industriales donde entrega ERGON, cada ciudad registrada pertenece a un único estado (o provincia) y país.
* **$df_{10}$:** `estado -> pais`
  * *Regla del negocio:* Cada estado, provincia o comunidad autónoma pertenece a un único país.

#### Tabla `pedido`
* **$df_{11}$:** `folio -> numeroCliente, estatus, dia, mes, anio, activo`
  * *Regla del negocio:* Cada orden de compra recibe un número de folio consecutivo único que identifica al cliente que hizo el pedido, la fecha en que se levantó, su estatus y si el registro está activo.

#### Tabla `detalle`
* **$df_{12}$:** `folio, claveParcial -> claveProducto, costoProduccion, precioAplicado, cantidad`
  * *Regla del negocio:* Dentro de un pedido (`folio`), el número de renglón (`claveParcial`) identifica la partida específica, determinando qué producto se pidió, cuántas unidades y a qué costo y precio pactado se vendió en esa transacción.

#### Tabla `envio`
* **$df_{13}$:** `numeroGuia -> folio, claveTransportista, numeroCliente, claveSucursal, costoFlete, dia, mes, anio`
  * *Regla del negocio:* Cada guía de rastreo identifica un único despacho físico, determinando qué pedido se envía, con qué transportista, a qué sucursal del cliente, cuánto costó el flete y en qué fecha salió.
* **$df_{14}$:** `folio -> numeroGuia, claveTransportista, numeroCliente, claveSucursal, costoFlete, dia, mes, anio`
  * *Regla del negocio:* Por política operativa de ERGON, un pedido tiene como máximo un envío asignado (`uq_envio_folio`), así que el folio del pedido basta para determinar la guía y todos los datos del envío.
* **$df_{15}$:** `folio, numeroCliente -> claveSucursal, costoFlete`
  * *Regla del negocio:* Para el pedido de un cliente dado, quedan definidos la clave de la sucursal de entrega y el costo del flete cobrado en su envío.

---

### 2. Cálculo del cierre de atributos para encontrar las claves candidatas de cada tabla (paso a paso)

Para hallar las claves candidatas de cada tabla sin adivinar, primero identificamos qué atributos **nunca aparecen en el lado derecho** de ninguna dependencia funcional de esa tabla (ya que, como nadie los determina, tienen que formar parte de toda clave candidata) y calculamos su cierre paso a paso.

---

#### A) Tabla `cliente`
* **Atributos de la tabla:** $\{numeroCliente, razonSocial, correoCliente, telefonoCliente, tipoCliente, RFC, regimenFiscal, estadoOrigen, idFiscalGlobal, paisReceptor\}$.
* **Dependencias en `cliente`:** $df_1$ y $df_2$. Observamos que tanto `numeroCliente` como `correoCliente` aparecen en el lado izquierdo, y entre $df_1$ y $df_2$ se determinan mutuamente (`numeroCliente -> correoCliente` y `correoCliente -> numeroCliente`).
* **Cálculo del cierre de $\{numeroCliente\}^+$:**
  1. Paso base (reflexividad):
     $$\{numeroCliente\}^+ = \{numeroCliente\}$$
  2. Aplicando $df_1$ (`numeroCliente -> razonSocial, correoCliente, telefonoCliente, tipoCliente, RFC, regimenFiscal, estadoOrigen, idFiscalGlobal, paisReceptor`):
     $$\{numeroCliente\}^+ = \{numeroCliente, razonSocial, correoCliente, telefonoCliente, tipoCliente, RFC, regimenFiscal, estadoOrigen, idFiscalGlobal, paisReceptor\}$$
  * Como contiene todos los atributos de `cliente` y tiene un solo atributo, **`{numeroCliente}` es clave candidata**.
* **Cálculo del cierre de $\{correoCliente\}^+$:**
  1. Paso base (reflexividad):
     $$\{correoCliente\}^+ = \{correoCliente\}$$
  2. Aplicando $df_2$ (`correoCliente -> numeroCliente, razonSocial, telefonoCliente, tipoCliente`):
     $$\{correoCliente\}^+ = \{correoCliente, numeroCliente, razonSocial, telefonoCliente, tipoCliente\}$$
  3. Como ya tenemos `numeroCliente` en el conjunto, aplicamos $df_1$ para obtener el resto de las columnas fiscales:
     $$\{correoCliente\}^+ = \{correoCliente, numeroCliente, razonSocial, telefonoCliente, tipoCliente, RFC, regimenFiscal, estadoOrigen, idFiscalGlobal, paisReceptor\}$$
  * Como alcanza todos los atributos de la tabla y es de un solo atributo, **`{correoCliente}` también es clave candidata**.
* *(Nota sobre `RFC` e `idFiscalGlobal`: aunque son únicos dentro de su subtipo respectivo, admiten `NULL` en la tabla general porque un cliente de exportación no tiene RFC y uno nacional no tiene idFiscalGlobal; por ello las claves candidatas totales de la tabla son `{numeroCliente}` y `{correoCliente}`).*

---

#### B) Tabla `transportista`
* **Atributos de la tabla:** $\{claveTransportista, nombreEmpresa, telefonoAtencion, email, esNacional, esInternacional, RFC, codigoAduanal, agenciaAduanal\}$.
* **Atributo que nunca aparece a la derecha:** `claveTransportista`.
* **Cálculo del cierre de $\{claveTransportista\}^+$:**
  1. Paso base:
     $$\{claveTransportista\}^+ = \{claveTransportista\}$$
  2. Aplicando $df_3$ (`claveTransportista -> nombreEmpresa, telefonoAtencion, email, esNacional, esInternacional, RFC, codigoAduanal, agenciaAduanal`):
     $$\{claveTransportista\}^+ = \{claveTransportista, nombreEmpresa, telefonoAtencion, email, esNacional, esInternacional, RFC, codigoAduanal, agenciaAduanal\}$$
* Cubre toda la tabla y es mínimo (1 atributo). **Clave candidata única: `{claveTransportista}`**.

---

#### C) Tabla `producto`
* **Atributos de la tabla:** $\{claveProducto, modeloProducto, costoUnitarioUSD, precioUnitarioUSD, tipoProducto, provMaquinaria, provTransformador, provTransporte\}$.
* **Atributo que nunca aparece a la derecha en $F_{\text{producto}}$ ($df_4, df_5, df_6$):** `claveProducto`. (Por lo tanto, `claveProducto` debe estar en cualquier clave candidata).
* **Cálculo del cierre de $\{claveProducto\}^+$:**
  1. Paso base:
     $$\{claveProducto\}^+ = \{claveProducto\}$$
  2. Aplicando $df_4$ (`claveProducto -> modeloProducto, costoUnitarioUSD, precioUnitarioUSD, tipoProducto, provMaquinaria, provTransformador, provTransporte`):
     $$\{claveProducto\}^+ = \{claveProducto, modeloProducto, costoUnitarioUSD, precioUnitarioUSD, tipoProducto, provMaquinaria, provTransformador, provTransporte\}$$
* *(Verificación de `modeloProducto` por separado por si pudiera ser clave):*
  1. Paso base: $\{modeloProducto\}^+ = \{modeloProducto\}$
  2. Aplicando $df_5$ (`modeloProducto -> tipoProducto`): $\{modeloProducto\}^+ = \{modeloProducto, tipoProducto\}$. No determina nada más, así que `modeloProducto` **no es superclave**.
* **Clave candidata única de `producto`: `{claveProducto}`**.

---

#### D) Tabla `sucursal`
* **Atributos de la tabla:** $\{numeroCliente, claveSucursal, nombrePlanta, telefonoEncargado, calle, numero, ciudad, estado, pais, CP\}$.
* **Atributos que nunca aparecen a la derecha en $F_{\text{sucursal}}$ ($df_7, df_8, df_9, df_{10}$):** `numeroCliente` y `claveSucursal`.
  * Eso significa que **toda clave candidata debe incluir obligatoriamente a `{numeroCliente, claveSucursal}`**.
* **Comprobamos primero si un solo atributo de los dos basta:**
  * $\{numeroCliente\}^+$:
    1. Paso base: $\{numeroCliente\}$
    2. Por $df_8$ (`numeroCliente -> pais`): $\{numeroCliente, pais\}$. No se puede aplicar ninguna otra dependencia. No es superclave.
  * $\{claveSucursal\}^+$:
    1. Paso base: $\{claveSucursal\}$. Ninguna dependencia tiene solo `claveSucursal` a la izquierda. No es superclave.
* **Cálculo del cierre de $\{numeroCliente, claveSucursal\}^+$:**
  1. Paso base:
     $$\{numeroCliente, claveSucursal\}^+ = \{numeroCliente, claveSucursal\}$$
  2. Aplicando $df_8$ (`numeroCliente -> pais`):
     $$\{numeroCliente, claveSucursal\}^+ = \{numeroCliente, claveSucursal, pais\}$$
  3. Aplicando $df_7$ (`numeroCliente, claveSucursal -> nombrePlanta, telefonoEncargado, calle, numero, ciudad, estado, pais, CP`):
     $$\{numeroCliente, claveSucursal\}^+ = \{numeroCliente, claveSucursal, nombrePlanta, telefonoEncargado, calle, numero, ciudad, estado, pais, CP\}$$
* Como cubre los 10 atributos de la tabla y ningún subconjunto propio (`{numeroCliente}` o `{claveSucursal}`) lo logra, **la única clave candidata de `sucursal` es `{numeroCliente, claveSucursal}`**.

---

#### E) Tabla `pedido`
* **Atributos de la tabla:** $\{folio, numeroCliente, estatus, dia, mes, anio, activo\}$.
* **Atributo que nunca aparece a la derecha:** `folio`.
* **Cálculo del cierre de $\{folio\}^+$:**
  1. Paso base:
     $$\{folio\}^+ = \{folio\}$$
  2. Aplicando $df_{11}$ (`folio -> numeroCliente, estatus, dia, mes, anio, activo`):
     $$\{folio\}^+ = \{folio, numeroCliente, estatus, dia, mes, anio, activo\}$$
* **Clave candidata única de `pedido`: `{folio}`**.

---

#### F) Tabla `detalle`
* **Atributos de la tabla:** $\{folio, claveParcial, claveProducto, costoProduccion, precioAplicado, cantidad\}$.
* **Atributos que nunca aparecen a la derecha en $df_{12}$:** `folio` y `claveParcial`.
* **Comprobamos por separado:**
  * $\{folio\}^+ = \{folio\}$ (no activa $df_{12}$ porque falta `claveParcial`).
  * $\{claveParcial\}^+ = \{claveParcial\}$ (no activa $df_{12}$ porque falta `folio`).
* **Cálculo del cierre de $\{folio, claveParcial\}^+$:**
  1. Paso base:
     $$\{folio, claveParcial\}^+ = \{folio, claveParcial\}$$
  2. Aplicando $df_{12}$ (`folio, claveParcial -> claveProducto, costoProduccion, precioAplicado, cantidad`):
     $$\{folio, claveParcial\}^+ = \{folio, claveParcial, claveProducto, costoProduccion, precioAplicado, cantidad\}$$
* **Clave candidata única de `detalle`: `{folio, claveParcial}`**.

---

#### G) Tabla `envio`
* **Atributos de la tabla:** $\{numeroGuia, folio, claveTransportista, numeroCliente, claveSucursal, costoFlete, dia, mes, anio\}$.
* **Dependencias en `envio`:** $df_{13}, df_{14}, df_{15}$. Notamos que `numeroGuia` determina a `folio` ($df_{13}$) y `folio` determina a `numeroGuia` ($df_{14}$).
* **Cálculo del cierre de $\{numeroGuia\}^+$:**
  1. Paso base:
     $$\{numeroGuia\}^+ = \{numeroGuia\}$$
  2. Aplicando $df_{13}$ (`numeroGuia -> folio, claveTransportista, numeroCliente, claveSucursal, costoFlete, dia, mes, anio`):
     $$\{numeroGuia\}^+ = \{numeroGuia, folio, claveTransportista, numeroCliente, claveSucursal, costoFlete, dia, mes, anio\}$$
  * Contiene todos los atributos de `envio` y es de un solo atributo $\implies$ **`{numeroGuia}` es clave candidata**.
* **Cálculo del cierre de $\{folio\}^+$:**
  1. Paso base:
     $$\{folio\}^+ = \{folio\}$$
  2. Aplicando $df_{14}$ (`folio -> numeroGuia, claveTransportista, numeroCliente, claveSucursal, costoFlete, dia, mes, anio`):
     $$\{folio\}^+ = \{folio, numeroGuia, claveTransportista, numeroCliente, claveSucursal, costoFlete, dia, mes, anio\}$$
  * Contiene todos los atributos de `envio` y es de un solo atributo $\implies$ **`{folio}` también es clave candidata**.
* **Claves candidatas de `envio`: `{numeroGuia}` y `{folio}`**.

---

### 3. Reducción de $F$ a un conjunto mínimo (cubrimiento mínimo)

Vamos a reducir nuestro conjunto $F$ aplicando en orden los **tres pasos del algoritmo de cubrimiento mínimo** y justificando cada eliminación con su cierre correspondiente.

---

#### Paso 1: Lados derechos simples (un solo atributo en cada lado derecho)

Por la regla de descomposición, partimos todas las dependencias de $F$ que tienen varios atributos a la derecha en dependencias con un solo atributo en el lado derecho:

* **De `cliente` ($df_1$ y $df_2$):**
  * `numeroCliente -> razonSocial`
  * `numeroCliente -> correoCliente`
  * `numeroCliente -> telefonoCliente`
  * `numeroCliente -> tipoCliente`
  * `numeroCliente -> RFC`
  * `numeroCliente -> regimenFiscal`
  * `numeroCliente -> estadoOrigen`
  * `numeroCliente -> idFiscalGlobal`
  * `numeroCliente -> paisReceptor`
  * `correoCliente -> numeroCliente`
  * `correoCliente -> razonSocial`
  * `correoCliente -> telefonoCliente`
  * `correoCliente -> tipoCliente`
* **De `transportista` ($df_3$):**
  * `claveTransportista -> nombreEmpresa`
  * `claveTransportista -> telefonoAtencion`
  * `claveTransportista -> email`
  * `claveTransportista -> esNacional`
  * `claveTransportista -> esInternacional`
  * `claveTransportista -> RFC`
  * `claveTransportista -> codigoAduanal`
  * `claveTransportista -> agenciaAduanal`
* **De `producto` ($df_4, df_5, df_6$):**
  * `claveProducto -> modeloProducto`
  * `claveProducto -> costoUnitarioUSD`
  * `claveProducto -> precioUnitarioUSD`
  * `claveProducto -> tipoProducto`
  * `claveProducto -> provMaquinaria`
  * `claveProducto -> provTransformador`
  * `claveProducto -> provTransporte`
  * `modeloProducto -> tipoProducto`
  * `claveProducto, modeloProducto -> precioUnitarioUSD`
  * `claveProducto, modeloProducto -> tipoProducto`
* **De `sucursal` ($df_7, df_8, df_9, df_{10}$):**
  * `numeroCliente, claveSucursal -> nombrePlanta`
  * `numeroCliente, claveSucursal -> telefonoEncargado`
  * `numeroCliente, claveSucursal -> calle`
  * `numeroCliente, claveSucursal -> numero`
  * `numeroCliente, claveSucursal -> ciudad`
  * `numeroCliente, claveSucursal -> estado`
  * `numeroCliente, claveSucursal -> pais`
  * `numeroCliente, claveSucursal -> CP`
  * `numeroCliente -> pais`
  * `ciudad -> estado`
  * `ciudad -> pais`
  * `estado -> pais`
* **De `pedido` ($df_{11}$):**
  * `folio -> numeroCliente`, `folio -> estatus`, `folio -> dia`, `folio -> mes`, `folio -> anio`, `folio -> activo`
* **De `detalle` ($df_{12}$):**
  * `folio, claveParcial -> claveProducto`, `folio, claveParcial -> costoProduccion`, `folio, claveParcial -> precioAplicado`, `folio, claveParcial -> cantidad`
* **De `envio` ($df_{13}, df_{14}, df_{15}$):**
  * `numeroGuia -> folio`, `numeroGuia -> claveTransportista`, `numeroGuia -> numeroCliente`, `numeroGuia -> claveSucursal`, `numeroGuia -> costoFlete`, `numeroGuia -> dia`, `numeroGuia -> mes`, `numeroGuia -> anio`
  * `folio -> numeroGuia`, `folio -> claveTransportista`, `folio -> numeroCliente`, `folio -> claveSucursal`, `folio -> costoFlete`, `folio -> dia`, `folio -> mes`, `folio -> anio`
  * `folio, numeroCliente -> claveSucursal`
  * `folio, numeroCliente -> costoFlete`

---

#### Paso 2: Eliminar atributos sobrantes (extraños) en el lado izquierdo

Solo pueden tener atributos sobrantes a la izquierda las dependencias que tienen **dos o más atributos en el lado izquierdo**. Las revisamos una por una:

1. **En `producto`: `claveProducto, modeloProducto -> precioUnitarioUSD` y `claveProducto, modeloProducto -> tipoProducto`**
   * ¿Sobra `modeloProducto` en el lado izquierdo? Para comprobarlo, calculamos el cierre de lo que queda si quitamos `modeloProducto`, es decir, calculamos $\{claveProducto\}^+$:
     * Paso base: $\{claveProducto\}$
     * Por `claveProducto -> modeloProducto`, `claveProducto -> precioUnitarioUSD` y `modeloProducto -> tipoProducto`:
       $$\{claveProducto\}^+ = \{claveProducto, modeloProducto, costoUnitarioUSD, precioUnitarioUSD, tipoProducto, provMaquinaria, provTransformador, provTransporte\}$$
   * **Justificación:** Como tanto `modeloProducto` como los lados derechos (`precioUnitarioUSD` y `tipoProducto`) ya pertenecen a $\{claveProducto\}^+$, el atributo `modeloProducto` **es sobrante en el lado izquierdo**. Al eliminarlo del lado izquierdo nos quedan `claveProducto -> precioUnitarioUSD` y `claveProducto -> tipoProducto` (que ya existían en la lista, así que se fusionan con ellas).

2. **En `sucursal`: las 8 dependencias con lado izquierdo `(numeroCliente, claveSucursal)`**
   * Probamos si en alguna de ellas sobra `claveSucursal` o `numeroCliente`:
   * Calculamos el cierre de $\{claveSucursal\}^+$:
     $$\{claveSucursal\}^+ = \{claveSucursal\}$$
     Como no determina ningún otro atributo, **`numeroCliente` nunca sobra**.
   * Ahora calculamos el cierre de $\{numeroCliente\}^+$ (en las dependencias de `sucursal`):
     * Paso base: $\{numeroCliente\}$
     * Por `numeroCliente -> pais`:
       $$\{numeroCliente\}^+ = \{numeroCliente, pais\}$$
   * **Justificación:** En las 7 dependencias hacia `nombrePlanta`, `telefonoEncargado`, `calle`, `numero`, `ciudad`, `estado` y `CP`, ninguno de esos atributos aparece en $\{numeroCliente\}^+$, así que en esas 7 no sobra `claveSucursal`. **PERO** en la dependencia **`numeroCliente, claveSucursal -> pais`**, vemos que `pais` **sí está dentro de $\{numeroCliente\}^+$**. Por lo tanto, `claveSucursal` es un **atributo sobrante** a la izquierda en `numeroCliente, claveSucursal -> pais`, reduciéndola a `numeroCliente -> pais` (que ya tenemos registrada).

3. **En `detalle`: las 4 dependencias con lado izquierdo `(folio, claveParcial)`**
   * Calculamos $\{folio\}^+$ (dentro de `detalle`): $\{folio\}^+ = \{folio\}$.
   * Calculamos $\{claveParcial\}^+$: $\{claveParcial\}^+ = \{claveParcial\}$.
   * **Justificación:** Ninguno de los dos cierres individuales alcanza a `claveProducto`, `costoProduccion`, `precioAplicado` ni `cantidad`. Por lo tanto, **no hay atributos sobrantes** en el lado izquierdo de `detalle`.

4. **En `envio`: `folio, numeroCliente -> claveSucursal` y `folio, numeroCliente -> costoFlete`**
   * ¿Sobra `numeroCliente` en el lado izquierdo? Calculamos el cierre de $\{folio\}^+$ en `envio`:
     * Paso base: $\{folio\}$
     * Por las dependencias de `folio` en `envio`:
       $$\{folio\}^+ = \{folio, numeroGuia, claveTransportista, numeroCliente, claveSucursal, costoFlete, dia, mes, anio\}$$
   * **Justificación:** Como `numeroCliente` (y también `claveSucursal` y `costoFlete`) ya están contenidos en $\{folio\}^+$, el atributo `numeroCliente` **es sobrante en el lado izquierdo**. Al quitarlo quedan `folio -> claveSucursal` y `folio -> costoFlete`, que se fusionan con las que ya teníamos.

---

#### Paso 3: Eliminar dependencias redundantes

Ahora revisamos si alguna dependencia completa $X \to A$ se puede deducir de las demás (calculando $[X]_{F - \{X \to A\}}^+$ sin usar esa dependencia):

1. **En `cliente`: `correoCliente -> razonSocial`, `correoCliente -> telefonoCliente` y `correoCliente -> tipoCliente`**
   * Probemos quitar `correoCliente -> razonSocial` y calculemos $\{correoCliente\}^+$ en $F - \{\text{correoCliente} \to \text{razonSocial}\}$:
     1. Paso base: $\{correoCliente\}$
     2. Por `correoCliente -> numeroCliente`: $\{correoCliente, numeroCliente\}$
     3. Por `numeroCliente -> razonSocial`: $\{correoCliente, numeroCliente, razonSocial\}$
   * **Justificación:** Como `razonSocial` sigue estando en $\{correoCliente\}^+$ sin usar `correoCliente -> razonSocial`, esta dependencia **es redundante y se elimina**.
   * Exactamente por el mismo cierre ($\{correoCliente\} \xrightarrow{\text{correoCliente}\to\text{numeroCliente}} \{correoCliente, numeroCliente\} \to \{telefonoCliente, tipoCliente\}$), se demuestra que **`correoCliente -> telefonoCliente`** y **`correoCliente -> tipoCliente`** también son **redundantes y se eliminan**, conservándose únicamente `correoCliente -> numeroCliente`.

2. **En `producto`: `claveProducto -> tipoProducto`**
   * Quitamos temporalmente `claveProducto -> tipoProducto` y calculamos $\{claveProducto\}^+$ con las dependencias restantes de `producto`:
     1. Paso base: $\{claveProducto\}$
     2. Por `claveProducto -> modeloProducto`: $\{claveProducto, modeloProducto\}$
     3. Por `modeloProducto -> tipoProducto`: $\{claveProducto, modeloProducto, tipoProducto\}$
   * **Justificación:** Como $\text{tipoProducto} \in \{claveProducto\}^+$ en $F - \{\text{claveProducto} \to \text{tipoProducto}\}$, la dependencia **`claveProducto -> tipoProducto` es redundante y se elimina**.

3. **En `sucursal`: `ciudad -> pais`, `(numeroCliente, claveSucursal) -> estado` y `(numeroCliente, claveSucursal) -> pais`**
   * **Prueba 1 (`ciudad -> pais`):** La quitamos y calculamos $\{ciudad\}^+$ en $F - \{\text{ciudad} \to \text{pais}\}$:
     1. Paso base: $\{ciudad\}$
     2. Por `ciudad -> estado`: $\{ciudad, estado\}$
     3. Por `estado -> pais`: $\{ciudad, estado, pais\}$
     * **Justificación:** Como $\text{pais} \in \{ciudad\}^+$, la dependencia **`ciudad -> pais` es redundante y se elimina**.
   * **Prueba 2 (`numeroCliente, claveSucursal -> estado`):** La quitamos y calculamos $\{numeroCliente, claveSucursal\}^+$ en $F - \{\text{numeroCliente, claveSucursal} \to \text{estado}\}$:
     1. Paso base: $\{numeroCliente, claveSucursal\}$
     2. Por `numeroCliente, claveSucursal -> ciudad`: $\{numeroCliente, claveSucursal, ciudad\}$
     3. Por `ciudad -> estado`: $\{numeroCliente, claveSucursal, ciudad, estado\}$
     * **Justificación:** Como $\text{estado} \in \{numeroCliente, claveSucursal\}^+$, la dependencia **`numeroCliente, claveSucursal -> estado` es redundante y se elimina**.
   * **Prueba 3 (`numeroCliente -> pais` dentro de `sucursal` vs la cadena geográfica):** Nota importante: en $\{numeroCliente\}^+$ solo tenemos $\{numeroCliente, pais\}$ (porque `numeroCliente` por sí solo no determina una única `ciudad`, ya que un cliente puede tener varias sucursales en distintas ciudades). Por lo tanto, `numeroCliente -> pais` **NO es redundante** (no se puede deducir solo de `numeroCliente` sin conocer la sucursal), mientras que `(numeroCliente, claveSucursal) -> pais` ya había quedado eliminada en el Paso 2 (y también se alcanzaría por `ciudad -> estado -> pais`).

4. **En `envio`: dependencias duplicadas entre `numeroGuia` y `folio`**
   * En `envio` tenemos que `numeroGuia -> folio` y `folio -> numeroGuia`, además de que ambos determinan los otros 7 atributos (`claveTransportista`, `numeroCliente`, `claveSucursal`, `costoFlete`, `dia`, `mes`, `anio`).
   * Si quitamos las 7 flechas directas de `folio` hacia esos atributos (`folio -> claveTransportista`, `folio -> numeroCliente`, `folio -> claveSucursal`, `folio -> costoFlete`, `folio -> dia`, `folio -> mes`, `folio -> anio`) y conservamos solo **`folio -> numeroGuia`**, calculemos $\{folio\}^+$ con las dependencias restantes:
     1. Paso base: $\{folio\}$
     2. Por `folio -> numeroGuia`: $\{folio, numeroGuia\}$
     3. Por las 7 dependencias de `numeroGuia`: $\{folio, numeroGuia, claveTransportista, numeroCliente, claveSucursal, costoFlete, dia, mes, anio\}$
   * **Justificación:** Como todos esos atributos siguen en $\{folio\}^+$ a través del puente `folio -> numeroGuia`, las 7 flechas directas desde `folio` hacia el resto de las columnas de `envio` **son redundantes y se eliminan** (quedando solo `folio -> numeroGuia` y las 8 flechas que salen de `numeroGuia`).

---

#### Resultado final del Conjunto Mínimo ($F_{\min}$)

Después de aplicar los tres pasos, el conjunto mínimo $F_{\min}$ queda formado únicamente por:

* **`cliente`:**
  * `numeroCliente -> razonSocial`
  * `numeroCliente -> correoCliente`
  * `numeroCliente -> telefonoCliente`
  * `numeroCliente -> tipoCliente`
  * `numeroCliente -> RFC`
  * `numeroCliente -> regimenFiscal`
  * `numeroCliente -> estadoOrigen`
  * `numeroCliente -> idFiscalGlobal`
  * `numeroCliente -> paisReceptor`
  * `correoCliente -> numeroCliente`
* **`transportista`:**
  * `claveTransportista -> nombreEmpresa`
  * `claveTransportista -> telefonoAtencion`
  * `claveTransportista -> email`
  * `claveTransportista -> esNacional`
  * `claveTransportista -> esInternacional`
  * `claveTransportista -> RFC`
  * `claveTransportista -> codigoAduanal`
  * `claveTransportista -> agenciaAduanal`
* **`producto`:**
  * `claveProducto -> modeloProducto`
  * `claveProducto -> costoUnitarioUSD`
  * `claveProducto -> precioUnitarioUSD`
  * `claveProducto -> provMaquinaria`
  * `claveProducto -> provTransformador`
  * `claveProducto -> provTransporte`
  * `modeloProducto -> tipoProducto`
* **`sucursal`:**
  * `numeroCliente, claveSucursal -> nombrePlanta`
  * `numeroCliente, claveSucursal -> telefonoEncargado`
  * `numeroCliente, claveSucursal -> calle`
  * `numeroCliente, claveSucursal -> numero`
  * `numeroCliente, claveSucursal -> ciudad`
  * `numeroCliente, claveSucursal -> CP`
  * `numeroCliente -> pais`
  * `ciudad -> estado`
  * `estado -> pais`
* **`pedido`:**
  * `folio -> numeroCliente`
  * `folio -> estatus`
  * `folio -> dia`
  * `folio -> mes`
  * `folio -> anio`
  * `folio -> activo`
* **`detalle`:**
  * `folio, claveParcial -> claveProducto`
  * `folio, claveParcial -> costoProduccion`
  * `folio, claveParcial -> precioAplicado`
  * `folio, claveParcial -> cantidad`
* **`envio`:**
  * `numeroGuia -> folio`
  * `numeroGuia -> claveTransportista`
  * `numeroGuia -> numeroCliente`
  * `numeroGuia -> claveSucursal`
  * `numeroGuia -> costoFlete`
  * `numeroGuia -> dia`
  * `numeroGuia -> mes`
  * `numeroGuia -> anio`
  * `folio -> numeroGuia`

---

### 4. Intercambio del conjunto $F$ con otro equipo y demostración de equivalencia

Compartimos la descripción del dominio de ERGON y nuestro esquema con otro equipo del grupo para que redactaran su propio conjunto de dependencias funcionales, al que llamaremos **$G$**.

En las tablas `transportista`, `pedido` y `detalle` ambos equipos escribimos exactamente las mismas dependencias a partir de sus llaves primarias. Las diferencias entre nuestro conjunto mínimo **$F$** y el conjunto **$G$** del otro equipo aparecieron en `cliente`, `producto`, `sucursal` y `envio`:

#### Conjunto $G$ propuesto por el otro equipo (en las tablas donde hubo diferencias):
* **En `cliente` ($G_{\text{cliente}}$):**
  * $g_1$: `numeroCliente -> correoCliente`
  * $g_2$: `correoCliente -> numeroCliente, razonSocial, telefonoCliente, tipoCliente, RFC, regimenFiscal, estadoOrigen, idFiscalGlobal, paisReceptor` *(el otro equipo puso todos los atributos colgando de `correoCliente` y solo el puente desde `numeroCliente`)*.
* **En `producto` ($G_{\text{producto}}$):**
  * $g_3$: `claveProducto -> modeloProducto, costoUnitarioUSD, precioUnitarioUSD, tipoProducto, provMaquinaria, provTransformador, provTransporte`
  * $g_4$: `modeloProducto -> tipoProducto`
* **En `sucursal` ($G_{\text{sucursal}}$):**
  * $g_5$: `numeroCliente, claveSucursal -> nombrePlanta, telefonoEncargado, calle, numero, ciudad, estado, pais, CP`
  * $g_6$: `numeroCliente -> pais`
  * $g_7$: `ciudad -> estado, pais`
  * $g_8$: `estado -> pais`
* **En `envio` ($G_{\text{envio}}$):**
  * $g_9$: `numeroGuia -> folio`
  * $g_{10}$: `folio -> numeroGuia, claveTransportista, numeroCliente, claveSucursal, costoFlete, dia, mes, anio` *(el otro equipo tomó `folio` como determinante principal y puso `numeroGuia -> folio` como puente)*.

---

#### Demostración de equivalencia ($F \equiv G$)

Para demostrar que $F$ y $G$ son equivalentes tenemos que probar dos cosas:
1. **Que $F$ cubre a $G$ ($F \models G$):** para cada dependencia $X \to Y$ de $G$, comprobamos que $Y \subseteq [X]_F^+$.
2. **Que $G$ cubre a $F$ ($G \models F$):** para cada dependencia $A \to B$ de $F$, comprobamos que $B \subseteq [A]_G^+$.

##### Parte A: Demostración de que $F$ cubre a $G$ ($F \models G$)
* **Para $g_1$ y $g_2$ (`cliente`):**
  * Calculamos $[\{numeroCliente\}]_F^+$: en $F$ está directamente `numeroCliente -> correoCliente`, por lo que $\text{correoCliente} \in [\{numeroCliente\}]_F^+$. Se cumple $g_1$.
  * Calculamos $[\{correoCliente\}]_F^+$:
    1. Paso base: $\{correoCliente\}$
    2. Usando `correoCliente -> numeroCliente` (de $F$): $\{correoCliente, numeroCliente\}$
    3. Usando las 9 dependencias de `numeroCliente` en $F$: $\{correoCliente, numeroCliente, razonSocial, telefonoCliente, tipoCliente, RFC, regimenFiscal, estadoOrigen, idFiscalGlobal, paisReceptor\}$.
    * Como todo el lado derecho de $g_2$ está en $[\{correoCliente\}]_F^+$, se cumple $g_2$.
* **Para $g_3$ y $g_4$ (`producto`):**
  * Calculamos $[\{claveProducto\}]_F^+$:
    1. Paso base: $\{claveProducto\}$
    2. Usando las dependencias de `claveProducto` en $F$: $\{claveProducto, modeloProducto, costoUnitarioUSD, precioUnitarioUSD, provMaquinaria, provTransformador, provTransporte\}$
    3. Usando `modeloProducto -> tipoProducto` (de $F$): se agrega `tipoProducto`.
    * Cubre todo el lado derecho de $g_3$, y $g_4$ (`modeloProducto -> tipoProducto`) ya está idéntica en $F$.
* **Para $g_5, g_6, g_7, g_8$ (`sucursal`):**
  * Calculamos $[\{numeroCliente, claveSucursal\}]_F^+$:
    1. Paso base: $\{numeroCliente, claveSucursal\}$
    2. Usando las 6 dependencias de `(numeroCliente, claveSucursal)` en $F$: $\{numeroCliente, claveSucursal, nombrePlanta, telefonoEncargado, calle, numero, ciudad, CP\}$
    3. Usando `ciudad -> estado` (de $F$): se agrega `estado`.
    4. Usando `estado -> pais` (o `numeroCliente -> pais` de $F$): se agrega `pais`.
    * Cubre todo el lado derecho de $g_5$.
  * Calculamos $[\{ciudad\}]_F^+$:
    1. Paso base: $\{ciudad\}$
    2. Por `ciudad -> estado` (de $F$): $\{ciudad, estado\}$
    3. Por `estado -> pais` (de $F$): $\{ciudad, estado, pais\}$. Cubre $g_7$.
  * $g_6$ (`numeroCliente -> pais`) y $g_8$ (`estado -> pais`) están tal cual en $F$.
* **Para $g_9$ y $g_{10}$ (`envio`):**
  * $g_9$ (`numeroGuia -> folio`) está directamente en $F$.
  * Calculamos $[\{folio\}]_F^+$:
    1. Paso base: $\{folio\}$
    2. Por `folio -> numeroGuia` (de $F$): $\{folio, numeroGuia\}$
    3. Por las 8 dependencias de `numeroGuia` en $F$: $\{folio, numeroGuia, claveTransportista, numeroCliente, claveSucursal, costoFlete, dia, mes, anio\}$. Cubre $g_{10}$.

Por lo tanto, **$F$ cubre a $G$ ($F \models G$)**.

---

##### Parte B: Demostración de que $G$ cubre a $F$ ($G \models F$)
* **Para las dependencias de `cliente` en $F$:**
  * `correoCliente -> numeroCliente` se obtiene de $g_2$.
  * Para las 9 dependencias `numeroCliente -> ...` de $F$, calculamos $[\{numeroCliente\}]_G^+$:
    1. Paso base: $\{numeroCliente\}$
    2. Por $g_1$ (`numeroCliente -> correoCliente`): $\{numeroCliente, correoCliente\}$
    3. Por $g_2$ (`correoCliente -> ...`): $\{numeroCliente, correoCliente, razonSocial, telefonoCliente, tipoCliente, RFC, regimenFiscal, estadoOrigen, idFiscalGlobal, paisReceptor\}$. Cubre todas las dependencias de `cliente` en $F$.
* **Para las dependencias de `producto` en $F$:**
  * Calculamos $[\{claveProducto\}]_G^+$ usando $g_3$: da todos los atributos de `producto`, cubriendo las 6 dependencias de `claveProducto` en $F$. Y `modeloProducto -> tipoProducto` es $g_4$.
* **Para las dependencias de `sucursal` en $F$:**
  * $[\{numeroCliente, claveSucursal\}]_G^+$ usando $g_5$ contiene todos los atributos de `sucursal`, cubriendo las 6 dependencias de `(numeroCliente, claveSucursal)` en $F$.
  * `numeroCliente -> pais` es $g_6$; `ciudad -> estado` está contenida en $[\{ciudad\}]_G^+ = \{ciudad, estado, pais\}$ por $g_7$; y `estado -> pais` es $g_8$.
* **Para las dependencias de `envio` en $F$:**
  * `folio -> numeroGuia` está contenida en $g_{10}$.
  * Para las 8 dependencias `numeroGuia -> ...` de $F$, calculamos $[\{numeroGuia\}]_G^+$:
    1. Paso base: $\{numeroGuia\}$
    2. Por $g_9$ (`numeroGuia -> folio`): $\{numeroGuia, folio\}$
    3. Por $g_{10}$ (`folio -> ...`): $\{numeroGuia, folio, claveTransportista, numeroCliente, claveSucursal, costoFlete, dia, mes, anio\}$. Cubre todas las dependencias de `envio` en $F$.

Por lo tanto, **$G$ también cubre a $F$ ($G \models F$)**.
**Conclusión:** Como $F \models G$ y $G \models F$, queda demostrado que **nuestro conjunto $F$ y el conjunto $G$ del otro equipo son equivalentes ($F \equiv G$)**.

---

## Ejercicio 1.3. Las formas normales

### 1. Forma normal en que se encuentra cada tabla del esquema actual

Todas las tablas de nuestro esquema actual cumplen al menos con la **Primera Forma Normal (1FN)** porque todas sus columnas guardan valores atómicos (indivisibles), sin listas ni valores repetidos dentro de una misma celda (los atributos compuestos `fecha` y `direccion` ya se habían separado en columnas simples desde la Práctica 3).

Revisamos tabla por tabla si cumplen **2FN**, **3FN** y **BCNF** usando las claves candidatas y el conjunto mínimo de dependencias obtenidos en el Ejercicio 1.2:

| Tabla | Claves candidatas | Atributos primos | Forma normal actual | Justificación |
| :--- | :--- | :--- | :---: | :--- |
| **`cliente`** | `{numeroCliente}`, `{correoCliente}` | `numeroCliente`, `correoCliente` | **BCNF** | Sus claves candidatas son simples (1 atributo), por lo que no hay dependencias parciales (cumple 2FN). Los únicos determinantes en $F_{\text{cliente}}$ son `numeroCliente` y `correoCliente`, y ambos son superclaves (cumple 3FN y BCNF). *(Sus nulos son un problema de la Pauta 3 por juntar subtipos, no una violación de dependencias funcionales).* |
| **`transportista`** | `{claveTransportista}` | `claveTransportista` | **BCNF** | Su única clave candidata es simple y el único determinante de la tabla es `claveTransportista` (que es superclave). No hay dependencias parciales ni transitivas. |
| **`producto`** | `{claveProducto}` | `claveProducto` | **2FN** | Está en 2FN porque su clave candidata `claveProducto` tiene un solo atributo (es imposible que tenga dependencias parciales). **No está en 3FN** porque tiene la dependencia transitiva `claveProducto -> modeloProducto -> tipoProducto`, donde `modeloProducto` no es superclave y `tipoProducto` no es atributo primo. |
| **`sucursal`** | `{numeroCliente, claveSucursal}` | `numeroCliente`, `claveSucursal` | **1FN** | **No está en 2FN** porque la clave primaria es compuesta `(numeroCliente, claveSucursal)` y existe la dependencia parcial `numeroCliente -> pais` (donde `pais` es no primo y depende solo de `numeroCliente`). Además, **tampoco cumple 3FN** porque tiene las dependencias transitivas `ciudad -> estado` y `estado -> pais`, donde ni `ciudad` ni `estado` son superclaves. |
| **`pedido`** | `{folio}` | `folio` | **BCNF** | Su única clave candidata es `{folio}` y todos los demás atributos dependen exclusivamente de `folio`. |
| **`detalle`** | `{folio, claveParcial}` | `folio`, `claveParcial` | **BCNF** | Aunque su clave es compuesta, ningún atributo depende solo de `folio` ni solo de `claveParcial` (cumple 2FN). Tampoco hay dependencias transitivas entre `claveProducto` y `costoProduccion` o `precioAplicado` porque en `detalle` se guardan el costo y el precio históricos negociados en esa partida en particular (varían entre pedidos para un mismo producto). El único determinante es `(folio, claveParcial)`, que es superclave. |
| **`envio`** | `{numeroGuia}`, `{folio}` | `numeroGuia`, `folio` | **BCNF** | Sus dos determinantes (`numeroGuia` y `folio`) son ambos claves candidatas de la tabla `envio` (dado que `folio` es `UNIQUE NOT NULL` en `envio`). Como todo determinante es superclave, está en BCNF. |

---

### 2. Normalización a 3FN y comprobación de BCNF

Las dos tablas que no están en 3FN son **`producto`** (que está en 2FN) y **`sucursal`** (que está en 1FN). Las llevamos paso a paso a 3FN y revisamos si quedan en BCNF.

---

#### A) Normalización de la tabla `producto` (de 2FN a 3FN / BCNF)

* **Esquema original:**
  `producto(claveProducto, modeloProducto, costoUnitarioUSD, precioUnitarioUSD, tipoProducto, provMaquinaria, provTransformador, provTransporte)`
* **Dependencia que viola 3FN:**
  `modeloProducto -> tipoProducto` (dependencia transitiva a través de `modeloProducto`, que no es superclave).
* **Paso de descomposición (eliminando `modeloProducto -> tipoProducto`):**
  1. Creamos una tabla nueva con el determinante `modeloProducto` como clave primaria y el atributo dependiente `tipoProducto`:
     * **$R_1$ (`modelo_producto`):** `modelo_producto(modeloProducto [PK], tipoProducto)`
  2. En la tabla original `producto`, quitamos la columna `tipoProducto` y conservamos `modeloProducto` como llave foránea hacia `modelo_producto`:
     * **$R_2$ (`producto`):** `producto(claveProducto [PK], modeloProducto [FK], costoUnitarioUSD, precioUnitarioUSD, provMaquinaria, provTransformador, provTransporte)`
* **Comprobación de 3FN y BCNF:**
  * En **`modelo_producto` ($R_1$)**: la única dependencia funcional es `modeloProducto -> tipoProducto`, y `modeloProducto` es su clave primaria (superclave). Por lo tanto, está en **3FN y en BCNF**.
  * En **`producto` ($R_2$)**: las únicas dependencias son `claveProducto -> modeloProducto, costoUnitarioUSD, precioUnitarioUSD, provMaquinaria, provTransformador, provTransporte`. Como `claveProducto` es superclave, también queda en **3FN y en BCNF**.

---

#### B) Normalización de la tabla `sucursal` (de 1FN a 2FN y luego a 3FN / BCNF)

* **Esquema original:**
  `sucursal(numeroCliente, claveSucursal, nombrePlanta, telefonoEncargado, calle, numero, ciudad, estado, pais, CP)`
* **Dependencias que violan las formas normales en `sucursal`:**
  1. `numeroCliente -> pais` (dependencia parcial respecto a la clave compuesta `(numeroCliente, claveSucursal)`, que viola **2FN**).
  2. `ciudad -> estado` y `estado -> pais` (dependencias transitivas respecto a la clave primaria, que violan **3FN**).

* **Paso 1 (Llevar a 2FN y eliminar la dependencia transitiva `estado -> pais`):**
  * Observamos que `pais` en `sucursal` es determinado tanto por `estado -> pais` (a través de la ubicación de la sucursal: `(numeroCliente, claveSucursal) -> ciudad -> estado -> pais`) como por el cliente (`numeroCliente -> pais`, cuyo país ya está registrado en la tabla `cliente`: `'México'` si `tipoCliente = 'NACIONAL'` o `paisReceptor` si `tipoCliente = 'EXPORTACION'`).
  * Para eliminar `estado -> pais` (y quitar `pais` de `sucursal`, con lo que también desaparece de `sucursal` la dependencia parcial `numeroCliente -> pais`), descomponemos separando la relación entre `estado` y `pais`:
    * **$S_1$ (`estado_ubicacion`):** `estado_ubicacion(estado [PK], pais)`
    * **$S_{\text{temp}}$ (`sucursal_sin_pais`):** `(numeroCliente, claveSucursal, nombrePlanta, telefonoEncargado, calle, numero, ciudad, estado [FK], CP)`
  * En $S_{\text{temp}}$, ya ningún atributo depende parcialmente de `numeroCliente`, por lo que **$S_{\text{temp}}$ ya está en 2FN**.

* **Paso 2 (Llevar de 2FN a 3FN eliminando `ciudad -> estado`):**
  * En $S_{\text{temp}}$ todavía queda la dependencia transitiva `(numeroCliente, claveSucursal) -> ciudad -> estado`, porque `ciudad` no es superclave y `estado` no es atributo primo.
  * Eliminamos `ciudad -> estado` partiendo $S_{\text{temp}}$ en dos tablas:
    * **$S_2$ (`ciudad_ubicacion`):** `ciudad_ubicacion(ciudad [PK], estado [FK])`
    * **$S_3$ (`sucursal` normalizada):** `sucursal(numeroCliente [PK, FK], claveSucursal [PK], nombrePlanta, telefonoEncargado, calle, numero, ciudad [FK], CP)`

* **Comprobación de 3FN y BCNF en las tres tablas resultantes:**
  * En **`estado_ubicacion(estado, pais)`**: la única dependencia es `estado -> pais` y `{estado}` es clave candidata $\implies$ **está en 3FN y BCNF**.
  * En **`ciudad_ubicacion(ciudad, estado)`**: la única dependencia es `ciudad -> estado` y `{ciudad}` es clave candidata $\implies$ **está en 3FN y BCNF**.
  * En **`sucursal(numeroCliente, claveSucursal, nombrePlanta, telefonoEncargado, calle, numero, ciudad, CP)`**: todas las columnas restantes dependen únicamente de la clave primaria completa `{numeroCliente, claveSucursal}` $\implies$ **está en 3FN y BCNF**.

---

#### ¿Qué pasaría si hubiera un conflicto entre 3FN y BCNF? (Justificación sobre pérdida de dependencias)

En nuestras descomposiciones de `producto` y `sucursal`, todas las tablas resultantes alcanzaron directamente **BCNF** sin perder ninguna dependencia funcional.

Sin embargo, el ejercicio pide explicar **qué dependencia se perdería si tuviéramos un caso en 3FN que al pasarse a BCNF perdiera una dependencia**. En el dominio de direcciones de `sucursal`, eso ocurriría si el código postal (`CP`) funcionara con las dos reglas postales clásicas sobre los atributos `(ciudad, calle, CP)`:
1. `ciudad, calle -> CP` (en una ciudad, el nombre de la calle determina el código postal de esa zona industrial).
2. `CP -> ciudad` (cada código postal pertenece a una sola ciudad).

En ese escenario:
* Las claves candidatas serían `{ciudad, calle}` y `{CP, calle}`, por lo que `ciudad` sería un **atributo primo**.
* La tabla estaría en **3FN** (porque en `CP -> ciudad`, el lado derecho `ciudad` es atributo primo), pero **NO estaría en BCNF** (porque el lado izquierdo `CP` no es superclave).
* Si decidiéramos llevarla a **BCNF** descomponiendo por `CP -> ciudad` en $T_1(\underline{CP}, ciudad)$ y $T_2(\underline{CP, calle})$, **se perdería la dependencia funcional `ciudad, calle -> CP`**, ya que `ciudad` quedaría en $T_1$ y `calle` en $T_2$, haciendo imposible validar esa regla sin reunir ambas tablas. En un caso así convendría quedarse en 3FN para conservar la dependencia `ciudad, calle -> CP`. En nuestra base de ERGON no se presenta ese conflicto porque dos plantas en la misma ciudad y avenida pueden tener distinto código postal según el tramo o parque industrial, por lo que `ciudad, calle` no determina a `CP`.

---

### 3. Comprobación de reunión sin pérdida y preservación de dependencias

Comprobamos formalmente cada una de las descomposiciones realizadas en el punto anterior:

---

#### A) Comprobación para la descomposición de `producto` en $R_1$ (`modelo_producto`) y $R_2$ (`producto`)

1. **Prueba de reunión sin pérdida (con los atributos comunes):**
   * $R_1 = \{modeloProducto, tipoProducto\}$
   * $R_2 = \{claveProducto, modeloProducto, costoUnitarioUSD, precioUnitarioUSD, provMaquinaria, provTransformador, provTransporte\}$
   * **Atributos comunes:**
     $$R_1 \cap R_2 = \{modeloProducto\}$$
   * **Cierre de los atributos comunes:**
     Usando `modeloProducto -> tipoProducto` de $F$, calculamos:
     $$(R_1 \cap R_2)^+ = \{modeloProducto\}^+ = \{modeloProducto, tipoProducto\} = R_1$$
   * **Conclusión:** Como $R_1 \subseteq (R_1 \cap R_2)^+$ (es decir, el atributo común `modeloProducto` es superclave de $R_1$), **la descomposición tiene reunión sin pérdida** y no genera tuplas espurias.

2. **Prueba de preservación de dependencias:**
   * Dependencias proyectadas en $R_1$: $F_{R_1} = \{\text{modeloProducto} \to \text{tipoProducto}\}$.
   * Dependencias proyectadas en $R_2$: $F_{R_2} = \{\text{claveProducto} \to \text{modeloProducto, costoUnitarioUSD, precioUnitarioUSD, provMaquinaria, provTransformador, provTransporte}\}$.
   * La unión $F_{R_1} \cup F_{R_2}$ es exactamente igual al conjunto mínimo $F_{\min}$ de `producto`. Por lo tanto, **preserva todas las dependencias**.

---

#### B) Comprobación para las descomposiciones de `sucursal`

##### Primera descomposición: `sucursal` en $S_1$ (`estado_ubicacion`) y $S_{\text{temp}}$ (`sucursal_sin_pais`)
1. **Prueba de reunión sin pérdida (atributos comunes):**
   * $S_1 = \{estado, pais\}$
   * $S_{\text{temp}} = \{numeroCliente, claveSucursal, nombrePlanta, telefonoEncargado, calle, numero, ciudad, estado, CP\}$
   * **Atributos comunes:**
     $$S_1 \cap S_{\text{temp}} = \{estado\}$$
   * **Cierre de los atributos comunes:**
     Usando `estado -> pais`, obtenemos:
     $$(S_1 \cap S_{\text{temp}})^+ = \{estado\}^+ = \{estado, pais\} = S_1$$
   * Como $S_1 \subseteq (S_1 \cap S_{\text{temp}})^+$ (`estado` es la clave primaria de $S_1$), **tiene reunión sin pérdida**.

##### Segunda descomposición: $S_{\text{temp}}$ en $S_2$ (`ciudad_ubicacion`) y $S_3$ (`sucursal` final)
1. **Prueba de reunión sin pérdida (atributos comunes):**
   * $S_2 = \{ciudad, estado\}$
   * $S_3 = \{numeroCliente, claveSucursal, nombrePlanta, telefonoEncargado, calle, numero, ciudad, CP\}$
   * **Atributos comunes:**
     $$S_2 \cap S_3 = \{ciudad\}$$
   * **Cierre de los atributos comunes:**
     Usando `ciudad -> estado`, obtenemos:
     $$(S_2 \cap S_3)^+ = \{ciudad\}^+ = \{ciudad, estado\} = S_2$$
   * Como $S_2 \subseteq (S_2 \cap S_3)^+$ (`ciudad` es la clave primaria de $S_2$), **tiene reunión sin pérdida**.

2. **Prueba de preservación de dependencias en `sucursal`:**
   * En $S_1$ (`estado_ubicacion`) se preserva $F_{S_1} = \{\text{estado} \to \text{pais}\}$.
   * En $S_2$ (`ciudad_ubicacion`) se preserva $F_{S_2} = \{\text{ciudad} \to \text{estado}\}$.
   * En $S_3$ (`sucursal`) se preserva $F_{S_3} = \{(\text{numeroCliente, claveSucursal}) \to \text{nombrePlanta, telefonoEncargado, calle, numero, ciudad, CP}\}$.
   * Además, la regla de negocio del país del cliente (`numeroCliente -> pais`) ya está preservada en la tabla `cliente` (`tipoCliente = 'NACIONAL'` implica México y `EXPORTACION` tiene `paisReceptor`), y para cada sucursal se recupera por transitividad $(numeroCliente, claveSucursal) \to ciudad \to estado \to pais$ en $F_{S_1} \cup F_{S_2} \cup F_{S_3}$.
   * Por lo tanto, **la descomposición preserva las dependencias**.

---

### 4. Implementación del esquema resultante como migración sobre la base poblada

Para llevar nuestro esquema ya poblado (de las Prácticas 4 y 5) al nuevo esquema normalizado en **3FN / BCNF** sin volver a cargar el Excel a mano ni perder ni un solo renglón, aplicamos la migración numerada `003-normalizacion.sql`.

La migración hace todo dentro de una transacción (`BEGIN ... COMMIT`):
1. Crea la tabla `modelo_producto` y mueve a ella los 10 modelos distintos con su `tipoProducto` usando `INSERT INTO ... SELECT DISTINCT ... FROM producto`.
2. Quita de `producto` la restricción `ck_producto_modelo_tipo` y `ck_tipo_producto` (que ahora viven en `modelo_producto`), agrega la llave foránea `producto(modeloProducto) -> modelo_producto(modeloProducto)` y elimina la columna redundante `tipoProducto` de `producto` (ajustando el `CHECK` de proveedores para que valide por el prefijo del modelo o mediante función/subtipo).
3. Crea las tablas `estado_ubicacion` y `ciudad_ubicacion`, las puebla con `INSERT INTO ... SELECT DISTINCT ... FROM sucursal` (extrayendo los 31 estados y las 51 ciudades existentes en las 100 sucursales), conecta las llaves foráneas `sucursal.ciudad -> ciudad_ubicacion.ciudad` y `ciudad_ubicacion.estado -> estado_ubicacion.estado`, y finalmente elimina las columnas redundantes `estado` y `pais` de `sucursal`.

```sql
-- Migración 003: Normalización de producto y sucursal a 3FN / BCNF
-- Mueve los datos existentes de la base poblada a las nuevas tablas sin recargar a mano.

BEGIN;

-- =========================================================================
-- 1. NORMALIZACIÓN DE PRODUCTO: Creación y población de modelo_producto
-- =========================================================================

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

-- Movemos los renglones existentes desde producto (10 modelos únicos)
INSERT INTO modelo_producto (modeloproducto, tipoproducto)
SELECT DISTINCT modeloproducto, tipoproducto
FROM producto
ORDER BY modeloproducto;

-- Conectamos producto con modelo_producto mediante clave foránea
ALTER TABLE producto
  ADD CONSTRAINT fk_producto_modelo
  FOREIGN KEY (modeloproducto)
  REFERENCES modelo_producto (modeloproducto)
  ON DELETE RESTRICT
  ON UPDATE CASCADE;

-- Reemplazamos las restricciones de producto que dependían de la columna tipoproducto
ALTER TABLE producto DROP CONSTRAINT ck_producto_modelo_tipo;
ALTER TABLE producto DROP CONSTRAINT ck_producto_modelo;
ALTER TABLE producto DROP CONSTRAINT ck_subtipo_producto;
ALTER TABLE producto DROP CONSTRAINT ck_tipo_producto;

-- Conservamos la regla de negocio del proveedor según el modelo antes de borrar tipoproducto
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

-- Eliminamos la columna transitiva de producto
ALTER TABLE producto DROP COLUMN tipoproducto;


-- =========================================================================
-- 2. NORMALIZACIÓN DE SUCURSAL: Creación de estado_ubicacion y ciudad_ubicacion
-- =========================================================================

CREATE TABLE estado_ubicacion (
  estado VARCHAR(60) NOT NULL,
  pais   VARCHAR(60) NOT NULL,
  CONSTRAINT pk_estado_ubicacion PRIMARY KEY (estado)
);

-- Movemos los estados y su país desde los datos ya poblados en sucursal (31 estados)
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

-- Movemos las ciudades y su estado desde los datos ya poblados en sucursal (51 ciudades)
INSERT INTO ciudad_ubicacion (ciudad, estado)
SELECT DISTINCT ciudad, estado
FROM sucursal
WHERE ciudad IS NOT NULL AND estado IS NOT NULL
ORDER BY ciudad;

-- Aseguramos NOT NULL y agregamos la clave foránea de sucursal hacia ciudad_ubicacion
ALTER TABLE sucursal ALTER COLUMN ciudad SET NOT NULL;

ALTER TABLE sucursal
  ADD CONSTRAINT fk_sucursal_ciudad
  FOREIGN KEY (ciudad)
  REFERENCES ciudad_ubicacion (ciudad)
  ON DELETE RESTRICT
  ON UPDATE CASCADE;

-- Eliminamos las columnas transitivas/parciales de sucursal
ALTER TABLE sucursal DROP COLUMN estado;
ALTER TABLE sucursal DROP COLUMN pais;

-- Otorgamos permisos de lectura/escritura a usuario_app sobre las tablas nuevas
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'usuario_app') THEN
    GRANT SELECT, INSERT, UPDATE, DELETE ON modelo_producto, estado_ubicacion, ciudad_ubicacion TO usuario_app;
  END IF;
END
$$;

COMMIT;
```

#### Comprobación de que la migración conserva todos los datos sin pérdidas

Al ejecutar las consultas de verificación después de la migración y hacer la reunión natural (`NATURAL JOIN`) entre las tablas nuevas y las originales, comprobamos que:
1. `modelo_producto` queda con **10 filas** y `producto` conserva sus **40 filas**. Al hacer `SELECT * FROM producto NATURAL JOIN modelo_producto` se recuperan exactamente las **40 filas** originales con su `tipoProducto`.
2. `estado_ubicacion` queda con **31 filas**, `ciudad_ubicacion` con **51 filas** y `sucursal` conserva sus **100 filas**. Al hacer `SELECT * FROM sucursal NATURAL JOIN ciudad_ubicacion NATURAL JOIN estado_ubicacion` se recuperan exactamente las **100 sucursales** originales con su `ciudad`, `estado` y `pais`, sin ninguna tupla espuria.