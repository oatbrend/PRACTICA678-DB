# Practices 6, 7, and 8 — Functional Dependencies, Normalization, and Relational Algebra

## Quick Start (Single Command)

Clone the repository and run the following single command from the root directory:

```bash
docker compose up --build --abort-on-container-exit
```

### What You Should See

Without asking for any user input (using test credentials from `.env.example` by default), the command automatically performs four steps in order and exits cleanly with code `0`:

1. **Starts PostgreSQL 17 (`db` service) and migrates the populated database to 3NF / BCNF:**
   - Applies the base schema and previous migrations (`000-esquema-base.sql`, `001-dominios.sql`, `002-referencias.sql`).
   - Loads the 2,702 records from `practica6-8/datos/base_datos_pedidos2.xlsx` and executes migration `003-normalizacion.sql`, moving the existing rows into the new normalized tables (`modelo_producto`, `estado_ubicacion`, `ciudad_ubicacion`) via `INSERT INTO ... SELECT DISTINCT ...`.
   - Prints the row count of all 10 normalized tables:
     `modelo_producto` (10), `producto` (40), `cliente` (80), `estado_ubicacion` (31), `ciudad_ubicacion` (51), `sucursal` (100), `transportista` (30), `pedido` (500), `detalle` (1,500), and `envio` (452).
2. **Executes all 13 SQL queries from Part 2 (`practica6-8/consultas/01-seleccion.sql` through `13-division.sql`) in order:**
   - For every query, prints:
     1. The domain question it answers (`1. Pregunta`).
     2. The relational algebra expression (`2. Álgebra`).
     3. The formatted result table returned by PostgreSQL (`3. Resultado`).
3. **Regenerates the RelaX group file (`practica6-8/relax/grupo.txt`) directly from the normalized PostgreSQL database:**
   - Runs `python practica6-8/relax/exportar-grupo.py`, exporting 10 to 30 rows per table while preserving 100% referential integrity.
4. **Terminates without errors (`runner-practica6-8 exited with code 0`).**

*(Note: Data is persisted in the `pgdata_p68` Docker volume so it survives container restarts. To reset the database volume from scratch, run `docker compose down -v`.)*

---

## Repository Structure

```text
.
├── compose.yaml
├── .env.example
├── README.md
└── practica6-8/
    ├── normalizacion.md               # Part 1 (Ex. 1.1, 1.2, 1.3): Informal guidelines, FDs, closures, minimal cover, 3NF/BCNF
    ├── almacen-y-formas-normales.md   # Part 1 (Ex. 1.4): Assigned Data Warehouse dimensions vs. normal forms
    ├── algebra.md                     # Part 2 (Ex. 2.1, 2.2, 2.3): RelaX export, 13 relational algebra queries, and 3 assigned DWH queries
    ├── teoria-practica6-8.md          # Study guide explaining every topic of Practices 6-8 from scratch
    ├── ejecutar-practica.py           # Automated container runner for migrations, queries, and RelaX export
    ├── datos/
    │   └── base_datos_pedidos2.xlsx   # Synthetic dataset (2,702 rows)
    ├── migraciones/
    │   ├── 000-esquema-base.sql
    │   ├── 001-dominios.sql
    │   ├── 002-referencias.sql
    │   └── 003-normalizacion.sql      # Normalization migration moving rows to modelo_producto, estado_ubicacion, ciudad_ubicacion
    ├── relax/
    │   ├── exportar-grupo.py          # Script that exports 10-30 rows/table preserving referential integrity
    │   └── grupo.txt                  # Versioned RelaX group file ready for the RelaX Group Editor
    ├── consultas/
    │   ├── 01-seleccion.sql
    │   ├── 02-proyeccion.sql
    │   ├── 03-composicion-seleccion-proyeccion.sql
    │   ├── 04-union.sql
    │   ├── 05-interseccion.sql
    │   ├── 06-diferencia.sql
    │   ├── 07-producto-cartesiano.sql
    │   ├── 08-reunion-natural.sql
    │   ├── 09-reunion-theta.sql
    │   ├── 10-reunion-externa.sql
    │   ├── 11-agregacion-modelos.sql
    │   ├── 12-agregacion-precios.sql
    │   └── 13-division.sql
    ├── integrantes/
    │   ├── omar.md                    # Individual work: Omar Flores Olivares (3 queries + decomposition explanation)
    │   └── bren.md                    # Individual work: Brenda Roa Venegas (3 queries + decomposition explanation)
    └── evidencias/
        ├── evidencias.md              # Execution logs and RelaX visual captures index
        └── *.svg                      # RelaX execution trees and result tables
```

---

## Team Members & Clean Clone Verification

- **Omar Flores Olivares**
- **Brenda Roa Venegas**
- **Academic Program:** Artificial Intelligence Engineering (IIA 2020) — ESCOM, IPN (Group 3BV1).

### Verification on a Clean Directory (La Prueba)

Before submission, the repository was cloned into a clean folder and executed with `docker compose up --build --abort-on-container-exit`:
- **Verified by:** Brenda Roa Venegas / Omar Flores Olivares
- **Date of verification:** `2026-11-16`
- **Branch / Commit verified:** `practica6-8` (verified clean startup, migration `003-normalizacion.sql`, execution of all 13 SQL queries, and regeneration of `practica6-8/relax/grupo.txt` with exit code `0`).

---

## Generative AI Usage Declaration

In accordance with the course guidelines, we declare that generative AI tools (Claude / Anthropic and ChatGPT / OpenAI) were used as study and coding assistants to:
1. Generate the initial synthetic dataset (`base_datos_pedidos2.xlsx`) based on our domain rules in Practice 4.
2. Assist in structuring the Python automation scripts (`exportar-grupo.py` and `ejecutar-practica.py`) and formatting the Markdown documentation and theory study guide (`teoria-practica6-8.md`). All functional dependencies, closures, normal form decompositions, and relational algebra queries were verified against the business rules and actual database results.
