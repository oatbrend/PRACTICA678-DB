# Guía Rápida de Teoría: Prácticas 6, 7 y 8 (Explicada Fácil)

Esta guía resume de forma corta y clara todos los conceptos que pregunta el profesor en la entrega de las Prácticas 6, 7 y 8.

---

## 1. Las 4 Pautas Informales de Diseño (Ejercicio 1.1)

Antes de aplicar fórmulas, revisamos si cada tabla tiene sentido con 4 reglas prácticas:
1. **Semántica clara:** Que cada tabla hable de **una sola cosa**. Si en la misma fila mezclas datos del producto con datos de la línea comercial, o mezclas la dirección de una sucursal con el catálogo de estados y países, la semántica no es clara.
2. **Sin anomalías (de inserción, borrado y actualización):** Cuando un dato se repite muchas veces (redundancia), ocurren 3 problemas:
   * *Actualización:* Si cambias el dato, tienes que editar muchas filas; si olvidas una, la base se contradice.
   * *Inserción:* No puedes registrar un dato nuevo (ej. una ciudad o un modelo) si todavía no existe una sucursal o un producto donde meterlo.
   * *Borrado:* Si borras la última fila que tenía ese dato, pierdes información del catálogo por accidente.
3. **Pocos valores `NULL`:** Evitar tablas donde muchas celdas queden vacías por diseño (pasa mucho cuando juntas subtipos como cliente nacional y cliente de exportación en una sola tabla).
4. **Sin tuplas espurias (filas falsas):** Si partes una tabla en dos, al volver a unirlas con `JOIN` deben salir exactamente las filas originales. Para no inventar filas falsas, la columna que une a las dos tablas **debe ser clave primaria o única** en al menos una de ellas.

---

## 2. Dependencias Funcionales ($X \to Y$) y Cierre ($X^+$) (Ejercicio 1.2)

* **¿Qué es $X \to Y$?** Significa: *«Si conozco el valor de $X$, automáticamente sé qué valor tiene $Y$»* (para cada valor de $X$ solo puede haber un valor de $Y$).
  * *Importante:* Las dependencias salen de las **reglas del negocio**, nunca de ver poquitas filas de ejemplo.
* **¿Qué es el cierre $X^+$?** Es la lista de todas las columnas que puedes descubrir si empiezas conociendo $X$ y sigues las flechas de tus dependencias funcionales como dominós.
* **Conceptos clave:**
  * **Superclave:** Cualquier grupo de columnas cuyo cierre da **todas las columnas de la tabla**.
  * **Clave candidata:** Una superclave **mínima** (sin columnas de más).
  * **Atributo primo:** Columna que forma parte de alguna clave candidata. **No primo:** Columna que no es parte de ninguna clave candidata.
* **Truco para hallar claves candidatas:** Busca las columnas que **nunca aparecen al lado derecho** de ninguna flecha. Esas columnas tienen que estar a fuerza en toda clave candidata. Calcula su cierre; si da toda la tabla, ya encontraste la clave candidata.

---

## 3. Conjunto Mínimo (Cubrimiento Mínimo) en 3 Pasos (Ejercicio 1.2.3)

Sirve para limpiar un conjunto de dependencias $F$ quitando lo repetido sin perder reglas:
1. **Paso 1 (Lados derechos simples):** Si una flecha tiene varias columnas a la derecha ($X \to A, B$), sepárala en flechas de una sola columna a la derecha ($X \to A$ y $X \to B$).
2. **Paso 2 (Sin atributos sobrantes a la izquierda):** Si una flecha tiene dos o más columnas a la izquierda ($A, B \to C$), prueba si sobra $B$ calculando $\{A\}^+$. Si en $\{A\}^+$ ya sale $B$ (o sale $C$), entonces $B$ está sobrando a la izquierda y lo borras, dejando $A \to C$.
3. **Paso 3 (Sin dependencias redundantes):** Para ver si una flecha completa $X \to Y$ sale sobrando, tápala temporalmente y calcula $X^+$ usando solo las demás flechas. Si aun sin ella llegas a $Y$, esa flecha es redundante y se borra.

* **¿Cómo demostrar que el conjunto $F$ de tu equipo y el $G$ de otro equipo son equivalentes?**
  Calculas el cierre del lado izquierdo de cada regla de $G$ usando $F$ (para ver que $F$ cubre a $G$), y luego al revés: calculas el cierre de cada regla de $F$ usando $G$ (para ver que $G$ cubre a $F$).

---

## 4. Las Formas Normales: 1FN, 2FN, 3FN y BCNF (Ejercicio 1.3)

Son niveles de limpieza acumulativos ($1\text{FN} \implies 2\text{FN} \implies 3\text{FN} \implies \text{BCNF}$):

1. **1FN (Atributos atómicos):** Cada celda guarda un solo valor (no listas ni tablas adentro).
2. **2FN (Sin dependencias parciales):** Ningún atributo no primo debe depender de **solo un pedazo** de una clave candidata compuesta.
   * *Atajo:* Si la clave primaria de la tabla es de **1 sola columna**, ¡es imposible partirla en pedazos!, así que **automáticamente está en 2FN**.
3. **3FN (Sin dependencias transitivas):** Ningún atributo no primo debe depender de otra columna que no sea clave ($\text{Clave} \to Y \to Z$).
   * *Cómo se corrige:* Sacas $Y$ y $Z$ a una tabla nueva donde $Y$ sea la clave primaria ($T_{\text{nueva}}(\underline{Y}, Z)$), y en la tabla original borras $Z$ y dejas $Y$ como llave foránea.
4. **BCNF (Boyce-Codd):** En **toda** flecha $X \to A$, el lado izquierdo $X$ debe ser superclave.
   * *¿Cuándo chocan 3FN y BCNF?* Cuando un atributo no clave determina a un pedazo de una clave compuesta (por ejemplo, `(ciudad, calle) -> CP` y `CP -> ciudad`). Ahí está en 3FN pero no en BCNF; si la partes para BCNF, pierdes la flecha `(ciudad, calle) -> CP`.

### Dos pruebas obligatorias al partir una tabla $R$ en $R_1$ y $R_2$:
* **Reunión sin pérdida (prueba de atributos comunes):** Mira qué columna quedó en común ($R_1 \cap R_2$). Si esa columna común es la **clave primaria (superclave) de $R_1$ o de $R_2$**, la unión no inventa filas falsas.
* **Preservación de dependencias:** Que todas las flechas originales hayan quedado dentro de $R_1$ o dentro de $R_2$, sin que ninguna regla se haya roto.

---

## 5. Desnormalización en el Data Warehouse (Ejercicio 1.4)

* En una base de ventas del día a día (**OLTP**, como ERGON) normalizamos hasta **3FN / BCNF** para no tener errores al insertar o actualizar.
* En un almacén de reportes (**Data Warehouse / OLAP**, como el proyecto asignado de obras públicas), las **tablas de dimensión** se dejan **en 2FN a propósito** (con dependencias transitivas como `colonia -> barrio -> comunidad` o `fecha -> mes -> trimestre -> anio`) para que los reportes analíticos sean muy rápidos y solo hagan un `JOIN` en vez de muchos.

---

## 6. Operadores del Álgebra Relacional y RelaX (Parte 2)

El álgebra relacional recibe tablas y devuelve una nueva tabla. Aquí tienes la traducción directa entre símbolo, **RelaX** y **SQL**:

| Operador | Símbolo | En RelaX | En SQL | Qué hace en palabras simples |
| :--- | :---: | :--- | :--- | :--- |
| **Selección** | $\sigma_{\text{cond}}(R)$ | `sigma cond (R)` | `WHERE cond` | Filtra **filas** que cumplen una condición. |
| **Proyección** | $\pi_{\text{cols}}(R)$ | `pi col1, col2 (R)` | `SELECT DISTINCT col1, col2` | Elige **columnas** y elimina filas repetidas. |
| **Renombramiento** | $\rho_{S}(R)$ | `rho S (R)` | `FROM R AS S` | Cambia el nombre de una tabla o columna. |
| **Unión** | $R \cup S$ | `R union S` | `UNION` | Junta filas de $R$ y $S$ (requiere mismas columnas/tipos). |
| **Intersección** | $R \cap S$ | `R intersect S` | `INTERSECT` | Filas que están al mismo tiempo en $R$ y en $S$. |
| **Diferencia** | $R - S$ | `R - S` | `EXCEPT` | Filas que están en $R$ pero **no** están en $S$. |
| **Prod. cartesiano** | $R \times S$ | `R cross join S` | `CROSS JOIN` | Combina todas las filas de $R$ con todas las de $S$ (casi nunca se usa solo porque mezcla filas sin relación). |
| **Reunión natural** | $R \bowtie S$ | `R natural join S` | `NATURAL JOIN` | Une por las columnas que se llamen igual en ambas tablas. |
| **Reunión theta** | $R \bowtie_\theta S$ | `R join cond S` | `JOIN S ON cond` | Une usando una condición escrita por ti ($=, <, >$). |
| **Reunión ext. izq.** | $R \ S$ | `R left outer join S` | `LEFT JOIN` | Conserva todas las filas de la izquierda aunque no tengan pareja a la derecha (rellena con `NULL`). |
| **Agrupación** | $\gamma_{G; \text{agg}}(R)$ | `gamma G; sum(x)->s (R)` | `GROUP BY G` | Agrupa filas y calcula `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`. |
| **División** | $R(A,B) \div S(B)$ | `R / S` | `GROUP BY A HAVING COUNT(DISTINCT B) = ...` | Responde preguntas con **«todos»**: devuelve los $A$ que están relacionados en $R$ con **todos** los valores de $B$ en $S$. |
