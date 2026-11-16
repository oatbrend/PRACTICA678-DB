# Guía de Teoría desde Cero: Prácticas 6, 7 y 8 (Normalización y Álgebra Relacional)

Esta guía explica **absolutamente todos los temas** que abarca la práctica conjunta 6, 7 y 8, pensada para leerse como si nunca hubiéramos visto estos temas en clase. No tiene relleno: va directo a qué significa cada concepto, por qué existe y **cómo se resuelven los ejercicios paso a paso**.

---

## 1. Panorama General: ¿De qué trata toda esta práctica?

Hasta las Prácticas 4 y 5 aprendimos a crear tablas en SQL (`CREATE TABLE`), meterles restricciones (`CHECK`, `UNIQUE`, `FOREIGN KEY`) y poblarlas con datos. Sin embargo, que una base de datos funcione en PostgreSQL **no significa que esté bien diseñada**.

Esta práctica se divide en tres grandes bloques:
1. **Parte 1 (Normalización y Dependencias Funcionales):** Cómo detectar si nuestras tablas tienen datos repetidos o mal acomodados, y usar un método matemático sencillo (dependencias funcionales, cierres y formas normales) para partir las tablas problemáticas en tablas limpias sin perder un solo dato.
2. **Parte 2 (Álgebra Relacional):** Es el lenguaje matemático que está "detrás" de SQL. Antes de que existiera `SELECT ... FROM ... WHERE ...`, Codd inventó operadores con símbolos ($\sigma, \pi, \bowtie, \gamma, \div$) para consultar tablas. Aquí aprenderemos qué hace cada símbolo, cómo escribirlo en la herramienta **RelaX** y a qué consulta SQL equivale.
3. **Parte 3 (Contenedor Docker):** Empaquetar la base ya normalizada, sus datos migrados y todas las consultas en un `compose.yaml` que corra solo con un comando.

---

## 2. Las 4 Pautas Informales de Diseño (Ejercicio 1.1)

Antes de usar fórmulas, los autores clásicos de bases de datos (como Elmasri y Navathe) proponen **4 reglas de sentido común** (llamadas *pautas informales*) para revisar si una tabla está bien pensada.

La mejor forma de empezar a evaluar una tabla es completar la frase: **«Cada fila de esta tabla es...»**. Si para describir una fila tienes que usar muchos "y además...", probablemente la tabla mezcla cosas que no deberían ir juntas.

### Pauta 1: Semántica clara de los atributos (No mezclar conceptos distintos)
* **¿Qué significa?** Cada tabla debe hablar de **una sola cosa** (una entidad o una relación). No debes meter en una misma fila datos de dos conceptos distintos.
* **Ejemplo malo:** Tener una tabla `pedido` que incluya las columnas `folio`, `fecha`, `numeroCliente`, `razonSocialCliente` y `rfcCliente`. Si preguntas «¿qué es cada fila?», tendrías que responder: *«Es un pedido, pero también guarda los datos fiscales del cliente»*.
* **Cómo se corrige:** Cada concepto va en su propia tabla (`pedido` solo guarda `numeroCliente` como llave foránea, y los datos del cliente viven en `cliente`).

### Pauta 2: Evitar información redundante y Anomalías de actualización
* **¿Qué significa?** Si un mismo dato se repite innecesariamente en muchas filas, tarde o temprano la base de datos se va a contradecir. Además de gastar espacio, la redundancia provoca **tres anomalías** (problemas prácticos):
  1. **Anomalía de inserción:** No puedes registrar un dato nuevo si no tienes otro dato que no viene al caso. *(Ejemplo: En nuestra tabla `producto`, donde guardamos `modeloProducto` y `tipoProducto` en cada presentación, no podemos dar de alta en el sistema que un nuevo modelo pertenece a la línea `HYVOLT` hasta que no inventemos al menos una presentación concreta con clave, costo y precio).*
  2. **Anomalía de borrado:** Al borrar una fila que ya no quieres, borras sin querer información importante que solo estaba guardada ahí. *(Ejemplo: Si damos de baja las 4 presentaciones del modelo `HYVOLT II`, desaparece de toda la base de datos el hecho de que el modelo `HYVOLT II` pertenece a la línea `HYVOLT`).*
  3. **Anomalía de modificación (o actualización):** Si quieres cambiar un dato que está repetido en 10 filas, tienes que acordarte de actualizar las 10 filas. Si actualizas 9 y se te pasa 1, la base queda inconsistente. *(Ejemplo: Si una ciudad cambia su nombre oficial o corregimos el estado al que pertenece en la tabla `sucursal`, tendríamos que actualizar todas las sucursales de esa ciudad una por una).*

### Pauta 3: Reducir al mínimo los valores `NULL` en las filas
* **¿Qué significa?** Evitar diseñar tablas donde muchas columnas se vayan a quedar vacías (`NULL`) en la mayoría de los renglones.
* **¿Por qué son problemáticos los `NULL`?** Desperdician espacio, confunden porque un `NULL` puede significar tres cosas distintas (*"no aplica"*, *"sí tiene pero no lo sabemos todavía"* o *"Aún no se captura"*), y complican las funciones como `COUNT` o `AVG` y las uniones (`JOIN`).
* **¿Cuándo pasa mucho esto?** Cuando en el modelo Entidad-Relación Extendido (EER) teníamos una **jerarquía de subtipos** (por ejemplo, clientes Nacionales vs. de Exportación, o productos `OMNIGOLD`, `HYVOLT` y `HYPRENE`) y decidimos meter todos los subtipos en **una sola tabla con discriminador**. Los atributos exclusivos del cliente nacional quedan `NULL` en todos los clientes extranjeros y viceversa.

### Pauta 4: Evitar la generación de tuplas espurias (filas falsas)
* **¿Qué significa?** *Tupla* = fila; *espuria* = falsa o inventada. Cuando divides una tabla en dos, debes asegurarte de que al volver a juntarlas con un `JOIN` obtengas **exactamente las mismas filas originales**, ni una más ni una menos.
* **¿Cuándo salen tuplas espurias?** Cuando partes una tabla usando como puente una columna que **NO es clave primaria ni única** en ninguna de las dos tablas resultantes.
* **Ejemplo rápido:** Imagina que partes la tabla `sucursal` en dos tablas usando únicamente la columna `ciudad` como puente: Tabla A `(numeroCliente, claveSucursal, ciudad)` y Tabla B `(ciudad, calle, CP)`. Si en Monterrey hay 3 sucursales con distinta calle y distinto CP, cuando hagas `TablaA JOIN TablaB ON ciudad`, PostgreSQL va a cruzar cada sucursal de Monterrey con las 3 direcciones de Monterrey, inventando $3 \times 3 = 9$ filas falsas (tuplas espurias).
* **Regla de oro:** Solo se deben reunir tablas a través de columnas que sean **clave primaria / única** en al menos una de las tablas.

---

## 3. Dependencias Funcionales ($X \to Y$) (Ejercicio 1.2.1)

### ¿Qué es una Dependencia Funcional (DF)?
Es una regla entre dos grupos de columnas de una misma tabla. Se escribe:
$$X \to Y$$
Y se lee: **«$X$ determina funcionalmente a $Y$»** o **«$Y$ depende funcionalmente de $X$»**.

En español sencillo significa:
> **«Si dos filas tienen el mismo valor en $X$, a fuerza tienen que tener el mismo valor en $Y$.»**
> O dicho de otro modo: **«Conocer el valor de $X$ me basta para saber con total seguridad cuál es el valor de $Y$ (solo hay un valor de $Y$ posible para ese $X$).»**

* Al lado izquierdo ($X$) se le llama **determinante**.
* Al lado derecho ($Y$) se le llama **dependiente**.

### Ejemplo con nuestro proyecto (ERGON):
* `numeroCliente -> razonSocial`: Si te doy el número de cliente `1001`, solo hay una razón social posible para ese número (`Distribuidora Metrópoli S.A.B. de C.V.`). Por lo tanto, `numeroCliente` determina a `razonSocial`.
* ¿Al revés se cumple? ¿`estatus -> folio` en la tabla `pedido`? **¡No!** Si te digo que el estatus es `'ENTREGADO'`, hay 444 folios distintos con ese estatus. No sabes a qué folio me refiero. Por lo tanto, `estatus` NO determina a `folio`.
* Una dependencia puede tener **varias columnas a la izquierda** (eso significa que necesitas conocer ambas al mismo tiempo):
  * En la tabla `detalle`, conocer solo `folio` no te dice qué `claveProducto` es (porque un pedido tiene varios renglones). Conocer solo `claveParcial` (ej. renglón `1`) tampoco te dice qué producto es (porque todos los pedidos tienen renglón `1`). Pero si conoces **los dos juntos**, `(folio, claveParcial) -> claveProducto, cantidad, precioAplicado`.

### ¡Cuidado con el error más común! (Advertencia de la página 4 del PDF)
Las dependencias funcionales **salen de las reglas del negocio**, NUNCA de ver 5 filas de ejemplo.
* **Ejemplo de trampa:** Si ves una tabla con 4 empleados y da la casualidad de que los 4 se llaman diferente, podrías pensar que `nombre -> sueldo`. ¡Falso! En cuanto entre un segundo "Juan Pérez" con otro sueldo, se rompe. Solo es dependencia funcional si una **regla de la empresa o de la realidad** garantiza que para cada valor de $X$ siempre existirá un único valor de $Y$.

---

## 4. Cierre de Atributos ($X^+$) y Claves Candidatas (Ejercicio 1.2.2)

### ¿Qué es el cierre de un conjunto de atributos ($X^+$)?
Si tienes un conjunto de reglas (dependencias funcionales) $F$, el **cierre de $X$** (que se escribe $X^+$) es **la lista de todas las columnas de la tabla que puedes llegar a descubrir si empiezas conociendo $X$ y aplicas las flechas de $F$ como dominós**.

### Receta paso a paso para calcular $X^+$ a mano:
Imagina que una tabla tiene las columnas $(A, B, C, D, E)$ y tienes estas reglas en $F$:
1. $A \to B$
2. $B \to C$
3. $C, D \to E$

**Pregunta:** ¿Cuál es el cierre de $\{A, D\}$, es decir, $\{A, D\}^+$?
* **Paso 0 (Base):** Empiezas con lo que ya tienes por defecto (si conoces $A$ y $D$, pues ya tienes $A$ y $D$):
  $$\{A, D\}^+ = \{A, D\}$$
* **Paso 1:** Revisas tus flechas. La regla 1 dice $A \to B$. ¿Ya tienes $A$ en tu bolsa? ¡Sí! Entonces agregas $B$ a la bolsa:
  $$\{A, D\}^+ = \{A, D, B\}$$
* **Paso 2:** La regla 2 dice $B \to C$. ¿Ya tienes $B$ en tu bolsa? ¡Sí, lo acabas de meter! Entonces agregas $C$:
  $$\{A, D\}^+ = \{A, D, B, C\}$$
* **Paso 3:** La regla 3 dice $C, D \to E$. ¿Ya tienes **tanto $C$ como $D$** en tu bolsa? ¡Sí! Entonces agregas $E$:
  $$\{A, D\}^+ = \{A, B, C, D, E\}$$
* **Resultado:** Como ya no hay más flechas ni columnas por descubrir, terminamos.

---

### ¿Para qué sirve el cierre? ¡Para encontrar las Claves Candidatas!

Aquí están las definiciones clave que debes dominar (todas se basan en el cierre):

1. **Superclave (Superllave):** Es cualquier grupo de columnas $K$ cuyo cierre $K^+$ **contiene absolutamente todas las columnas de la tabla**. *(En el ejemplo de arriba, como $\{A, D\}^+ = \{A, B, C, D, E\}$, entonces $\{A, D\}$ es una superclave. También $\{A, B, D\}$ sería superclave, aunque tiene grasa de más).*
2. **Clave Candidata:** Es una **superclave mínima** (sin columnas sobrantes). Es decir, su cierre da todas las columnas de la tabla, pero **si le quitas cualquiera de sus columnas, deja de dar todas**. *(En el ejemplo de arriba, si a $\{A, D\}$ le quitas $D$, $\{A\}^+ = \{A, B, C\}$ ya no alcanza a $E$; y si le quitas $A$, $\{D\}^+ = \{D\}$ tampoco. Como no le sobra nada, $\{A, D\}$ es **clave candidata**).*
3. **Clave Primaria (PK):** Es simplemente la clave candidata que tú elegiste en SQL como principal (si una tabla tiene dos claves candidatas, como `numeroGuia` y `folio` en `envio`, eliges una como PK y la otra queda como `UNIQUE`).
4. **Atributo Primo vs. Atributo No Primo:**
   * **Atributo primo:** Cualquier columna que forme parte de **alguna** clave candidata.
   * **Atributo no primo:** Cualquier columna que **no** forme parte de ninguna clave candidata.

### Truco infalible para encontrar rápido las claves candidatas de una tabla:
Cuando ves las flechas $F$ de una tabla, clasifica sus columnas en tres cubetas:
1. **Izquierda pura (nunca aparecen al lado derecho de ninguna flecha):** Como nadie las determina, **tienen que ir a fuerza en TODA clave candidata**. ¡Empieza siempre calculando el cierre de estas columnas!
2. **Derecha pura (solo aparecen al lado derecho y nunca a la izquierda):** No determinan a nadie, así que **jamás** formarán parte de una clave candidata.
3. **Ambas (aparecen a la izquierda y a la derecha):** Solo las pruebas combinándolas con las de "Izquierda pura" si el cierre de la primera cubeta no alcanzó para cubrir toda la tabla.

---

## 5. Conjunto Mínimo (Cubrimiento Mínimo) y Equivalencia (Ejercicios 1.2.3 y 1.2.4)

Cuando escribimos las dependencias funcionales a partir de las reglas del negocio, muchas veces escribimos reglas con varios atributos a la derecha, o con atributos de más a la izquierda, o flechas que se podrían deducir de otras dos.
Reducir $F$ a un **conjunto mínimo** (también llamado *cubrimiento mínimo* o *canónico*) significa dejar el conjunto de flechas lo más limpio y corto posible **sin perder ninguna regla**.

Se hace siempre con **3 pasos en orden estricto**:

### Paso 1: Lados derechos simples (un solo atributo a la derecha)
Si una flecha tiene dos o más atributos a la derecha, la separas en varias flechas con una sola columna a la derecha.
* **Antes:** `modeloProducto -> tipoProducto, provMaquinaria`
* **Después:**
  * `modeloProducto -> tipoProducto`
  * `modeloProducto -> provMaquinaria`

### Paso 2: Sin atributos sobrantes (extraños) a la izquierda
Solo se revisan las flechas que tengan **2 o más atributos a la izquierda** (por ejemplo, $A, B \to C$). Queremos saber si $A$ o $B$ sale sobrando.
* **¿Cómo se comprueba con un cierre?**
  * Para ver si $B$ sobra en $A, B \to C$, calculas el cierre de lo que quedaría sin $B$, es decir, calculas $\{A\}^+$.
  * Si en $\{A\}^+$ aparece $B$ (o aparece directamente $C$), ¡entonces $B$ estaba de adorno! Lo borras del lado izquierdo y la flecha queda simplemente $A \to C$.
* **Ejemplo real de nuestra base:** Si tenemos en `sucursal` la dependencia `(numeroCliente, claveSucursal) -> pais` y además sabemos por regla de negocio que `numeroCliente -> pais`, probamos si `claveSucursal` sobra a la izquierda calculando $\{numeroCliente\}^+$. Como `pais` ya está en $\{numeroCliente\}^+$, `claveSucursal` es un atributo sobrante y la regla se simplifica a `numeroCliente -> pais`.

### Paso 3: Sin dependencias redundantes (flechas que se deducen de otras)
Revisamos si alguna flecha completa $X \to Y$ sale sobrando porque hay un "camino alternativo" (un puente) usando las demás flechas.
* **¿Cómo se comprueba con un cierre?**
  * Tapas temporalmente con el dedo la flecha $X \to Y$ que quieres probar (a eso se le llama usar el conjunto $F - \{X \to Y\}$).
  * Calculas el cierre de $X$ ($X^+$) **sin usar esa flecha**.
  * Si aun sin usar esa flecha logras llegar a $Y$ (es decir, $Y \in X^+$), entonces la flecha $X \to Y$ **es redundante** y se elimina definitivamente.
* **Ejemplo real de nuestra base (`producto`):**
  Tenemos:
  1. `claveProducto -> modeloProducto`
  2. `modeloProducto -> tipoProducto`
  3. `claveProducto -> tipoProducto`
  ¿Es redundante la 3 (`claveProducto -> tipoProducto`)? La quitamos temporalmente y calculamos $\{claveProducto\}^+$ usando solo la 1 y la 2:
  * Empezamos con $\{claveProducto\}$.
  * Por la 1 llegamos a `modeloProducto`: $\{claveProducto, modeloProducto\}$.
  * Por la 2 llegamos a `tipoProducto`: $\{claveProducto, modeloProducto, tipoProducto\}$.
  Como llegamos a `tipoProducto` sin usar la flecha 3, queda demostrado con el cierre que `claveProducto -> tipoProducto` es **redundante** y se elimina.

---

### ¿Cómo demostrar que el conjunto $F$ de nuestro equipo y el conjunto $G$ de otro equipo son equivalentes? (Ejercicio 1.2.4)
Dos conjuntos de dependencias funcionales $F$ y $G$ sobre el mismo esquema son **equivalentes** ($F \equiv G$) si expresan exactamente las mismas reglas del negocio, aunque estén escritas distinto.
Para demostrarlo matemáticamente sin adivinar, se hacen **dos pruebas con cierres**:
1. **Demostrar que $F$ cubre a $G$ ($F \models G$):** Para cada flecha $X \to Y$ del otro equipo ($G$), calculas el cierre de $X$ usando **tus** reglas ($[X]_F^+$). Si siempre aparece $Y$ adentro, tus reglas cubren todas las suyas.
2. **Demostrar que $G$ cubre a $F$ ($G \models F$):** Ahora al revés: para cada flecha $A \to B$ de tu conjunto ($F$), calculas el cierre de $A$ usando **las reglas del otro equipo** ($[A]_G^+$). Si siempre aparece $B$ adentro, sus reglas cubren todas las tuyas.
* Si se cumplen ambas direcciones, ¡queda demostrado al 100% que $F$ y $G$ son equivalentes! (Si falla alguna flecha en cualquiera de los dos sentidos, no son equivalentes y muestras exactamente qué flecha falló).

---

## 6. Las Formas Normales: 1FN, 2FN, 3FN y BCNF (Ejercicio 1.3)

Las Formas Normales son como "niveles de certificación de limpieza" de una tabla. Son acumulativas: para estar en 2FN primero debes estar en 1FN; para estar en 3FN debes estar en 2FN; y para estar en BCNF debes estar en 3FN.

$$1\text{FN} \implies 2\text{FN} \implies 3\text{FN} \implies \text{BCNF}$$

Una frase famosa resume 2FN, 3FN y BCNF:
> **«Cada atributo que no sea clave debe depender de la clave (1FN), de TODA la clave (2FN) y de NADA MÁS que la clave (3FN / BCNF).»**

Vamos a ver una por una:

### Primera Forma Normal (1FN): Valores atómicos
* **Regla:** Cada celda de la tabla (la intersección de una fila y una columna) debe guardar **un solo valor indivisible** (atómico). No se valen listas separadas por comas (ej. `telefonos = "551234, 559876"`), ni arreglos, ni tablas anidadas dentro de una celda.
* **En nuestro proyecto:** Como en la Práctica 3 descompusimos los atributos compuestos (`fecha` en `dia, mes, anio` y `direccion` en `calle, numero, ciudad, estado, pais, CP`) y no tenemos listas en ninguna celda, **todas nuestras tablas parten al menos de 1FN**.

---

### Segunda Forma Normal (2FN): Sin dependencias parciales
* **Regla:** Está en 1FN y **ningún atributo no primo depende parcialmente de una clave candidata**.
* **¿Qué es una dependencia parcial?** Ocurre cuando una clave candidata es **compuesta** (formada por 2 o más columnas, digamos $(A, B)$) y existe una columna $C$ (que no es parte de ninguna clave) a la que **le basta con una sola parte de la clave** para quedar determinada (por ejemplo, $A \to C$ o $B \to C$, sin necesitar la pareja completa $(A, B)$).
* **¡Atajo importantísimo!** Si una tabla tiene como únicas claves candidatas columnas **individuales** (de 1 solo atributo, como `folio` en `pedido` o `claveProducto` en `producto`), **es imposible partir en pedazos una clave de 1 sola columna**. Por lo tanto:
  > **Toda tabla en 1FN cuya clave candidata sea de un solo atributo está AUTOMÁTICAMENTE en 2FN.**
* **Ejemplo donde SÍ falla 2FN en nuestra base (`sucursal`):**
  * La clave primaria de `sucursal` es compuesta: `(numeroCliente, claveSucursal)`.
  * Por regla de negocio de ERGON, un cliente nacional opera en México y uno de exportación en su único país receptor, así que con saber el puro `numeroCliente` ya sabes en qué `pais` están sus sucursales (`numeroCliente -> pais`).
  * Como `pais` es un atributo no primo y depende solo de `numeroCliente` (una mitad de la clave primaria compuesta `(numeroCliente, claveSucursal)`), esa es una **dependencia parcial** y hace que `sucursal` viole 2FN.

---

### Tercera Forma Normal (3FN): Sin dependencias transitivas
* **Regla:** Está en 2FN y **ningún atributo no primo depende transitivamente de una clave candidata**.
* **¿Qué es una dependencia transitiva?** Es un "puente" o "intermediario":
  $$\text{Clave} \to Y \to Z$$
  donde $Y$ **NO es superclave** y $Z$ **NO es atributo primo** (no es parte de ninguna clave). Es decir, $Z$ está en la tabla no por culpa de la clave primaria, sino porque depende de otra columna normal $Y$.
* **Definición formal equivalente de 3FN:** Para toda dependencia funcional no trivial $X \to A$ de la tabla, debe cumplirse al menos una de estas dos cosas:
  1. $X$ es una **superclave** de la tabla, O BIEN
  2. $A$ es un **atributo primo** (forma parte de alguna clave candidata).
* **Ejemplos reales donde falla 3FN en nuestra base:**
  1. **En `producto`:**
     * La clave primaria es `claveProducto` (1 sola columna, así que sí está en 2FN).
     * Pero `claveProducto -> modeloProducto` y a su vez `modeloProducto -> tipoProducto`.
     * Como `modeloProducto` no es clave de la tabla (hay 4 productos por cada modelo) y `tipoProducto` no es parte de ninguna clave, tenemos la dependencia transitiva `claveProducto -> modeloProducto -> tipoProducto`. Por eso `producto` se queda en **2FN** y **no está en 3FN**.
  2. **En `sucursal`:**
     * Además del problema con `pais`, la clave `(numeroCliente, claveSucursal)` determina la `ciudad`, pero `ciudad -> estado` y `estado -> pais`.
     *Ni `ciudad` ni `estado` son superclaves de `sucursal`, y determinan a otros atributos no primos (`estado` y `pais`). Esas son **dependencias transitivas** que violan **3FN**.

---

### Forma Normal de Boyce-Codd (BCNF): Todo determinante es superclave
* **Regla:** Es una versión más estricta y más fácil de recordar que 3FN. Una tabla está en **BCNF** si para absolutamente toda dependencia funcional no trivial $X \to A$:
  > **$X$ (el lado izquierdo) SIEMPRE es una superclave de la tabla.** (Aquí ya no se perdona el "permiso especial" de 3FN donde $A$ era atributo primo).
* **¿Cuándo una tabla está en 3FN pero NO en BCNF?**
  Solo ocurre en un caso muy específico: cuando la tabla tiene **dos o más claves candidatas compuestas que se traslapan** y un atributo no clave determina a un pedacito de una clave (un atributo primo).
  * **Ejemplo clásico (Direcciones con Código Postal):** Imagina una tabla `direccion(ciudad, calle, cp)` donde:
    * Si sabes `(ciudad, calle)` sabes el `cp`: `(ciudad, calle) -> cp`.
    * Y si sabes el `cp` sabes a qué `ciudad` pertenece: `cp -> ciudad`.
    * Aquí las claves candidatas son `{ciudad, calle}` y `{cp, calle}`. Nota que `ciudad` es un **atributo primo** (porque es parte de la clave `{ciudad, calle}`).
    * ¿Está en **3FN**? ¡Sí! Porque en `cp -> ciudad`, aunque `cp` no es superclave, el lado derecho (`ciudad`) es un **atributo primo** (entra por el permiso especial de 3FN).
    * ¿Está en **BCNF**? **¡No!** Porque en `cp -> ciudad`, el lado izquierdo (`cp`) no es superclave.
    * **¿Por qué a veces decidimos quedarnos en 3FN en vez de pasar a BCNF?** Porque si partes esa tabla para llevarla a BCNF creando `T1(cp, ciudad)` y `T2(cp, calle)`, **pierdes la dependencia `(ciudad, calle) -> cp`** (quedan `ciudad` en `T1` y `calle` en `T2`, separadas, así que ya no puedes vigilar la regla `(ciudad, calle) -> cp` sin hacer un `JOIN`).

---

### ¿Cómo se lleva una tabla a 3FN / BCNF paso a paso? (Receta de descomposición)
Cada vez que encuentras una dependencia $X \to Y$ que viola 2FN o 3FN (donde $X$ no es superclave):
1. **Creas una tabla nueva** que tenga como columnas a $X \cup Y$, donde **$X$ será la clave primaria** de esa tabla nueva.
2. **En la tabla original**, **eliminas las columnas $Y$** (las del lado derecho de la flecha problemática), pero **dejas $X$** adentro para que sirva como **llave foránea (FK)** que apunte a la tabla nueva.

---

## 7. Reunión sin Pérdida y Preservación de Dependencias (Ejercicio 1.3.3)

Siempre que partes una tabla $R$ en dos tablas $R_1$ y $R_2$, el profesor pide demostrar dos propiedades obligatorias:

### Propiedad 1: Reunión sin pérdida (Lossless-Join Decomposition)
Significa que al hacer $R_1 \bowtie R_2$ (reunión natural) recuperas exactamente las filas originales de $R$, sin que aparezcan **tuplas espurias** (filas falsas).
* **¿Cómo se demuestra con la «prueba de los atributos comunes»?**
  1. Calculas la intersección $R_1 \cap R_2$ (es decir, qué columna o columnas quedaron repetidas en ambas tablas como puente).
  2. Calculas el cierre de esa intersección: $(R_1 \cap R_2)^+$.
  3. **La prueba pasa si $(R_1 \cap R_2)^+$ contiene TODOS los atributos de $R_1$ o TODOS los atributos de $R_2$** (dicho en corto: los atributos comunes deben ser **superclave de $R_1$ o superclave de $R_2$**).
* **Ejemplo con `producto`:**
  * $R_1(\text{modeloProducto}, \text{tipoProducto})$
  * $R_2(\text{claveProducto}, \text{modeloProducto}, \text{costoUnitarioUSD}, \dots)$
  * Atributos comunes: $R_1 \cap R_2 = \{\text{modeloProducto}\}$.
  * Como `modeloProducto -> tipoProducto`, el cierre es $\{\text{modeloProducto}\}^+ = \{\text{modeloProducto}, \text{tipoProducto}\} = R_1$.
  * Como los atributos comunes determinan a toda $R_1$ (son la clave primaria de $R_1$), **la descomposición tiene reunión sin pérdida**.

### Propiedad 2: Preservación de dependencias
Significa que todas las reglas del negocio ($F$) se pueden seguir vigilando en las tablas separadas ($R_1, R_2, \dots$) sin tener que hacer `JOIN` entre ellas.
* **¿Cómo se comprueba?**
  * Ves qué dependencias de $F$ quedaron dentro de $R_1$ ($F_{R_1}$) y cuáles quedaron dentro de $R_2$ ($F_{R_2}$).
  * Si la unión $F_{R_1} \cup F_{R_2}$ implica todas las dependencias originales de $F$ (es decir, ninguna flecha quedó con su lado izquierdo en una tabla y su lado derecho en otra tabla sin puente equivalente), entonces **preserva las dependencias**.

---

## 8. Desnormalización y Almacenes de Datos (Data Warehouse) (Ejercicio 1.4)

En la vida real existen dos tipos de bases de datos muy distintos:

1. **Bases Transaccionales (OLTP - *Online Transaction Processing*):** Como **nuestro proyecto propio (ERGON)**. Aquí todo el día se están insertando pedidos, actualizando estatus y registrando envíos. Por eso **necesitamos 3FN / BCNF**: para que las actualizaciones sean rápidas, seguras y sin anomalías.
2. **Almacenes de Datos / Bases Analíticas (OLAP / Data Warehouse - DWH):** Como **el proyecto asignado (`PublicMunicipalWorks_DWH`)**. Un almacén dimensional se organiza en **esquema estrella**:
   * En el centro hay una **Tabla de Hechos** (*Fact Table*, ej. `Fact_Obras`) con números y métricas y puras llaves foráneas.
   * Alrededor hay **Tablas de Dimensión** (*Dimension Tables*, ej. `Dim_Ubicacion`, `Dim_Tiempo`, `Dim_Contratista`) que sirven para filtrar y agrupar en gráficas y reportes.

### ¿Por qué las dimensiones de un Data Warehouse están desnormalizadas a propósito (en 2FN)?
Porque una dimensión guarda toda una jerarquía junta en la misma tabla (por ejemplo, en `Dim_Ubicacion` están `id_ubicacion [PK] -> municipio -> estado -> region`, o en `Dim_Tiempo` están `id_tiempo [PK] -> fecha -> mes -> trimestre -> anio`).
* Esas cadenas (`municipio -> estado -> region`) son **dependencias transitivas**, por lo que la dimensión está en **2FN y NO en 3FN**.
* **¿Qué gana el almacén al conservar la dependencia transitiva?** Cuando un directivo pide un reporte de miles de obras agrupadas por región o por trimestre, el motor ejecuta un solo `JOIN` entre la tabla de hechos y la dimensión, en vez de hacer 3 o 4 `JOIN`s en cadena (`hechos -> municipio -> estado -> region`). Como en un almacén de datos casi no se hacen `UPDATE`s sueltos (se carga por lotes controlados o ETL), vale la pena sacrificar 3FN a cambio de velocidad de lectura y consultas simples.

---

## 9. Álgebra Relacional y RelaX (Parte 2: Ejercicios 2.1, 2.2 y 2.3)

El **álgebra relacional** es un conjunto de operadores que reciben una o dos tablas (relaciones) como entrada y **devuelven siempre una nueva tabla como resultado**. Como el resultado de cualquier operador es otra tabla, puedes meter un operador adentro de otro (componerlos) o guardar pasos intermedios con el símbolo de asignación ($\leftarrow$).

En la práctica usamos **RelaX** (un simulador web de álgebra relacional). A continuación tienes **todos los operadores que pide la práctica**, qué hacen, su símbolo matemático, cómo se escriben en RelaX y su traducción a SQL:

### 9.1. Selección ($\sigma$) — Filtrar filas (horizontal)
* **¿Qué hace?** Funciona igual que el `WHERE` de SQL: revisa fila por fila y deja pasar solo las que cumplen una condición lógica ($=, \neq, <, >, \leq, \geq, \land \text{ [AND]}, \lor \text{ [OR]}, \neg \text{ [NOT]}$). Conserva todas las columnas originales.
* **Notación matemática:** $\sigma_{\text{tipoCliente} = \text{'EXPORTACION'}}(\text{cliente})$
* **En RelaX:** `sigma tipoCliente = 'EXPORTACION' (cliente)`
* **En SQL:** `SELECT * FROM cliente WHERE tipocliente = 'EXPORTACION';`

### 9.2. Proyección ($\pi$) — Elegir columnas (vertical) y quitar repetidos
* **¿Qué hace?** Elige solo las columnas que le pidas y desecha las demás. **¡Detalle crucial!** Como en el álgebra relacional las relaciones son conjuntos matemáticos, **$\pi$ elimina automáticamente las filas duplicadas** (equivale a `SELECT DISTINCT`, no a `SELECT` simple).
* **Notación matemática:** $\pi_{\text{razonSocial}, \text{paisReceptor}}(\text{cliente})$
* **En RelaX:** `pi razonSocial, paisReceptor (cliente)`
* **En SQL:** `SELECT DISTINCT razonsocial, paisreceptor FROM cliente;`
* **Composición ($\pi$ con $\sigma$):** Primero filtras filas con $\sigma$ adentro y luego proyectas columnas con $\pi$ afuera:
  $$\pi_{\text{razonSocial}, \text{paisReceptor}}(\sigma_{\text{tipoCliente} = \text{'EXPORTACION'}}(\text{cliente}))$$

### 9.3. Renombramiento ($\rho$)
* **¿Qué hace?** Le cambia el nombre a una tabla o a sus columnas (útil cuando necesitas unir una tabla consigo misma o hacer compatibles dos tablas para una unión).
* **En RelaX:** `rho nuevo_nombre (tabla)` o para renombrar columna `rho col_nueva <- col_vieja (tabla)`.

### 9.4. Operadores de Teoría de Conjuntos: Unión ($\cup$), Intersección ($\cap$) y Diferencia ($-$)
Para poder aplicar $\cup$, $\cap$ o $-$ entre dos tablas $R$ y $S$, ambas deben cumplir la **Compatibilidad de Unión** (también llamada compatibilidad de esquema):
1. Tener **exactamente el mismo número de columnas** (mismo grado).
2. Que cada columna de $R$ sea del **mismo tipo de dato / dominio** que la columna en la misma posición de $S$. *(Por eso casi siempre aplicamos antes una proyección $\pi$ a ambas tablas para dejarles la misma columna, por ejemplo $\pi_{\text{numeroCliente}}(A) \cup \pi_{\text{numeroCliente}}(B)$).*

* **Unión ($R \cup S$):** Filas que están en $R$, o en $S$, o en ambas (sin duplicados).
  * **En RelaX:** `(pi numeroCliente (A)) union (pi numeroCliente (B))`
  * **En SQL:** `SELECT numerocliente FROM A UNION SELECT numerocliente FROM B;`
* **Intersección ($R \cap S$):** Filas que están **al mismo tiempo** en $R$ y en $S$.
  * **En RelaX:** `(pi numeroCliente (A)) intersect (pi numeroCliente (B))`
  * **En SQL:** `SELECT numerocliente FROM A INTERSECT SELECT numerocliente FROM B;`
* **Diferencia ($R - S$):** Filas que están en $R$ **pero NO están** en $S$ (el orden importa: $R - S \neq S - R$).
  * **En RelaX:** `(pi numeroCliente (cliente)) - (pi numeroCliente (pedido))` *(clientes que nunca han hecho un pedido)*.
  * **En SQL:** `SELECT numerocliente FROM cliente EXCEPT SELECT numerocliente FROM pedido;`

### 9.5. Producto Cartesiano ($\times$)
* **¿Qué hace?** Toma cada fila de la tabla $R$ y la pega con **absolutamente todas las filas** de la tabla $S$. Si $R$ tiene 80 clientes y $S$ tiene 500 pedidos, $R \times S$ genera $80 \times 500 = 40,000$ renglones, mezclando pedidos con clientes que ni siquiera los compraron.
* **¿Por qué casi nunca se usa solo?** Porque sin una condición $\sigma$ que filtre las filas donde coinciden la clave primaria y la clave foránea ($R.\text{id} = S.\text{id}$), produce miles de combinaciones sin sentido en el mundo real y explota en memoria.
* **En RelaX:** `R cross join S`
* **En SQL:** `SELECT * FROM R CROSS JOIN S;`

### 9.6. Reuniones (Joins): Natural ($\bowtie$), Theta ($\bowtie_\theta$) y Externas ($\, \, \$)
Un Join no es más que un producto cartesiano seguido de un filtro para emparejar solo las filas relacionadas:
1. **Reunión Natural ($R \bowtie S$):** Busca automáticamente las columnas que **se llamen exactamente igual** en $R$ y en $S$, empareja las filas donde esas columnas tengan el mismo valor y deja una sola copia de la columna repetida.
   * **En RelaX:** `cliente natural join pedido`
   * **En SQL:** `SELECT * FROM cliente NATURAL JOIN pedido;`
2. **Reunión Theta ($R \bowtie_\theta S$):** Une dos tablas usando una condición explícita $\theta$ que tú escribes (puede ser $=$, $<$, $>$, etc.). Si la condición usa solo $=$, también se le llama *equijoin*.
   * **En RelaX:** `pedido join pedido.folio = envio.folio and envio.costoFlete > 5000 envio`
   * **En SQL:** `SELECT * FROM pedido JOIN envio ON pedido.folio = envio.folio AND envio.costoflete > 5000;`
3. **Reuniones Externas (Outer Joins):**
   * En un join normal (interno: $\bowtie$ o $\bowtie_\theta$), **las filas que no tienen pareja en la otra tabla SE PIERDEN** (por ejemplo, un pedido `'CANCELADO'` que no tiene envío desaparece al hacer `pedido natural join envio`).
   * Las reuniones externas **conservan las filas sin pareja**, rellenando con `NULL` las columnas de la tabla donde no hubo coincidencia:
     * **Izquierda ($\$ / `left outer join`):** Conserva todas las filas de la tabla de la izquierda aunque no tengan pareja a la derecha.
     * **Derecha ($\$ / `right outer join`):** Conserva todas las filas de la tabla de la derecha.
     * **Completa ($\$ / `full outer join`):** Conserva las filas sin pareja de ambos lados.

### 9.7. Agrupación y Funciones Agregadas ($\gamma$)
* **¿Qué hace?** Equivale al `GROUP BY` de SQL junto con funciones de resumen (`COUNT`, `SUM`, `AVG`, `MIN`, `MAX`).
* **Notación matemática:**
  $$\gamma_{\text{columnas\_grupo};\; \text{FUNC}(\text{col}) \to \text{alias}}(R)$$
  * A la izquierda del punto y coma van las columnas por las que agrupas (si no pones ninguna, resume toda la tabla en 1 sola fila).
  * A la derecha van los cálculos agregados con su nombre de columna resultante.
* **En RelaX:** `gamma tipoCliente; count(numeroCliente)->totalClientes (cliente)`
* **En SQL:** `SELECT tipocliente, COUNT(numerocliente) AS totalclientes FROM cliente GROUP BY tipocliente;`

### 9.8. División ($R \div S$) — El operador para preguntas con «TODOS»
* **¿Cuándo se usa?** Siempre que la pregunta del negocio diga **«...que se relacionan con TODOS los...»**.
  * *Ejemplo:* «Obtener los folios de los pedidos que incluyeron **todos** los productos del modelo `'HYVOLT II'`».
* **¿Cómo funciona formalmente?**
  Supón que tienes:
  * **Dividendo $R(A, B)$:** Una tabla de dos columnas (o dos grupos de columnas), por ejemplo $R(\text{folio}, \text{claveProducto})$ obtenida de `detalle`.
  * **Divisor $S(B)$:** Una tabla con la columna $B$ que contiene el conjunto de cosas que quieres exigir al 100%, por ejemplo $S(\text{claveProducto})$ con las claves de los productos `'HYVOLT II'`.
  * **Resultado de $R \div S$:** Devuelve una tabla con únicamente la columna $A$ (`folio`), dejando **solo aquellos valores de $A$ que estaban emparejados en $R$ con CADA UNO de los valores de $B$ que existen en $S$**.
* **¿Por qué se llama división?** Porque es el inverso del producto cartesiano: si un `folio` aparece combinado con todos los productos de $S$, entonces el par $(\text{folio} \times S)$ está contenido dentro de $R$.
* **Fórmula equivalente con operadores básicos** (por si el profesor pregunta en clase cómo se hace la división sin usar el símbolo $\div$):
  $$R(A, B) \div S(B) \;=\; \pi_A(R) \;-\; \pi_A\Big( (\pi_A(R) \times S) - R \Big)$$
  *(Traducción intuitiva: «Todos los folios posibles» MENOS «los folios a los que les faltó al menos un producto de $S$»).*
* **En RelaX:** `R / S` o `R ÷ S`
* **En SQL:** En SQL no existe la palabra `DIVIDE`, así que se escribe con `GROUP BY ... HAVING COUNT(DISTINCT B) = (SELECT COUNT(*) FROM S)` o con doble `NOT EXISTS`.

---

## 10. Resumen Rápido de Símbolos para RelaX y Clase

| Operador | Símbolo | Cómo se escribe en RelaX | Equivalente en SQL |
| :--- | :---: | :--- | :--- |
| **Selección** | $\sigma_{c}(R)$ | `sigma condicion (R)` | `SELECT * FROM R WHERE condicion` |
| **Proyección** | $\pi_{L}(R)$ | `pi col1, col2 (R)` | `SELECT DISTINCT col1, col2 FROM R` |
| **Renombramiento** | $\rho_{S}(R)$ | `rho S (R)` | `FROM R AS S` |
| **Asignación (pasos)** | $T \leftarrow E$ | `T = expresion` | `WITH T AS (SELECT ...)` |
| **Unión** | $R \cup S$ | `R union S` | `SELECT ... UNION SELECT ...` |
| **Intersección** | $R \cap S$ | `R intersect S` | `SELECT ... INTERSECT SELECT ...` |
| **Diferencia** | $R - S$ | `R - S` | `SELECT ... EXCEPT SELECT ...` |
| **Producto cartesiano** | $R \times S$ | `R cross join S` | `SELECT * FROM R CROSS JOIN S` |
| **Reunión natural** | $R \bowtie S$ | `R natural join S` | `SELECT * FROM R NATURAL JOIN S` |
| **Reunión theta** | $R \bowtie_\theta S$ | `R join cond S` | `SELECT * FROM R JOIN S ON cond` |
| **Reunión ext. izq.** | $R \ S$ | `R left outer join S` | `SELECT * FROM R LEFT JOIN S ON ...` |
| **Reunión ext. der.** | $R \ S$ | `R right outer join S` | `SELECT * FROM R RIGHT JOIN S ON ...` |
| **Reunión ext. comp.** | $R \ S$ | `R full outer join S` | `SELECT * FROM R FULL JOIN S ON ...` |
| **Agrupación / Agreg.** | $\gamma_{G; F}(R)$ | `gamma G; count(c)->n (R)` | `SELECT G, COUNT(c) AS n FROM R GROUP BY G` |
| **División** | $R \div S$ | `R / S` | `GROUP BY A HAVING COUNT(DISTINCT B) = ...` |
