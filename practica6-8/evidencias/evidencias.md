# Evidencias de Ejecución — Prácticas 6, 7 y 8

En esta carpeta se almacenan las capturas visuales de los árboles de ejecución y tablas de resultados de **RelaX** correspondientes a:

1. **Consultas del equipo (`algebra.md` — Ejercicio 2.2):**
   - [`relax-q01.svg`](./relax-q01.svg) — Consulta 1: Selección y proyección sobre `producto` (`costounitariousd > 1850`).
   - [`relax-q02.svg`](./relax-q02.svg) — Consulta 2: Selección y proyección sobre `modelo_producto` (`HYPRENE` o `HYVOLT`).
   - [`relax-q03.svg`](./relax-q03.svg) — Consulta 3: Composición de selección y proyección sobre `cliente` (`NACIONAL` y `numerocliente <= 1004`).
   - [`relax-q04.svg`](./relax-q04.svg) — Consulta 4: Unión ($\cup$) entre modelos `'HYVOLT II'` y `'HYPRENE BO150'`.
   - [`relax-q05.svg`](./relax-q05.svg) — Consulta 5: Intersección ($\cap$) entre clientes nacionales y sucursales `'S02'`.
   - [`relax-q06.svg`](./relax-q06.svg) — Consulta 6: Diferencia ($-$) de clientes sin pedidos en los primeros 4 folios.
   - [`relax-q07.svg`](./relax-q07.svg) — Consulta 7: Producto cartesiano ($\times$) entre 2 modelos y 2 productos.
   - [`relax-q08.svg`](./relax-q08.svg) — Consulta 8: Reunión natural ($\bowtie$) entre `producto` y `modelo_producto`.
   - [`relax-q09.svg`](./relax-q09.svg) — Consulta 9: Reunión theta ($\bowtie_\theta$) entre `pedido` y `envio` con `costoflete > 3000`.
   - [`relax-q10.svg`](./relax-q10.svg) — Consulta 10: Reunión externa izquierda ($\) entre `pedido` y `envio` conservando el pedido cancelado `100003`.
   - [`relax-q11.svg`](./relax-q11.svg) — Consulta 11: Agrupación y agregación ($\gamma$) de modelos por `tipoproducto`.
   - [`relax-q12.svg`](./relax-q12.svg) — Consulta 12: Agrupación y agregación ($\gamma$) de costo promedio, precio mínimo y máximo por modelo.
   - [`relax-q13.svg`](./relax-q13.svg) — Consulta 13: División ($\div$) de pedidos que incluyen todos los productos de `'Tráileres Monterrey'`.

2. **Consultas individuales de Omar Flores Olivares (`integrantes/omar.md`):**
   - [`relax-omar-q1.svg`](./relax-omar-q1.svg) — División ($\div$): clientes que compraron todas las presentaciones de `'HYPRENE BO150'`.
   - [`relax-omar-q2.svg`](./relax-omar-q2.svg) — Reunión externa izquierda ($\) entre `transportista` y `envio`.
   - [`relax-omar-q3.svg`](./relax-omar-q3.svg) — Reunión natural y agrupación ($\gamma$) por línea comercial.

3. **Consultas individuales de Brenda Roa Venegas (`integrantes/bren.md`):**
   - [`relax-bren-q1.svg`](./relax-bren-q1.svg) — División ($\div$): pedidos que compraron todos los productos de `'Tres Guerras Logística'`.
   - [`relax-bren-q2.svg`](./relax-bren-q2.svg) — Reunión externa izquierda ($\) entre `cliente` y `pedido`.
   - [`relax-bren-q3.svg`](./relax-bren-q3.svg) — Reunión natural de `sucursal`, `ciudad_ubicacion` y `estado_ubicacion`.
