#!/usr/bin/env python3
"""Script principal del contenedor (Parte 3):
1. Verifica si la base ya fue poblada y migrada a 3FN/BCNF (003-normalizacion.sql);
   si está recién inicializada, carga los 2,702 registros base y aplica la migración 003
   moviendo los renglones existentes a las tablas nuevas.
2. Ejecuta en orden las 13 consultas SQL de la Parte 2 mostrando la pregunta,
   la expresión en álgebra relacional y la tabla de resultados devuelta por PostgreSQL.
3. Regenera el archivo de grupo de RelaX (practica6-8/relax/grupo.txt) desde la base.
4. Termina sin errores y sin pedir datos al usuario.
"""
from __future__ import annotations

import csv
import os
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET
from io import StringIO
from pathlib import Path

import psycopg2
from psycopg2 import sql

ROOT = Path(__file__).resolve().parent
XLSX_FILE = ROOT / "datos" / "base_datos_pedidos2.xlsx"
MIG_003 = ROOT / "migraciones" / "003-normalizacion.sql"
CONSULTAS_DIR = ROOT / "consultas"
EXPORTAR_SCRIPT = ROOT / "relax" / "exportar-grupo.py"

BASE_TABLES = [
    ("cliente", ["numerocliente", "razonsocial", "correocliente", "telefonocliente",
                 "tipocliente", "rfc", "regimenfiscal", "estadoorigen",
                 "idfiscalglobal", "paisreceptor"]),
    ("transportista", ["clavetransportista", "nombreempresa", "telefonoatencion", "email",
                       "esnacional", "esinternacional", "rfc", "codigoaduanal", "agenciaaduanal"]),
    ("producto", ["claveproducto", "modeloproducto", "costounitariousd", "preciounitariousd",
                  "tipoproducto", "provmaquinaria", "provtransformador", "provtransporte"]),
    ("sucursal", ["numerocliente", "clavesucursal", "nombreplanta", "telefonoencargado",
                  "calle", "numero", "ciudad", "estado", "pais", "cp"]),
    ("pedido", ["folio", "numerocliente", "estatus", "dia", "mes", "anio", "activo"]),
    ("detalle", ["folio", "claveparcial", "claveproducto", "costoproduccion",
                  "precioaplicado", "cantidad"]),
    ("envio", ["numeroguia", "folio", "clavetransportista", "numerocliente",
                "clavesucursal", "costoflete", "dia", "mes", "anio"]),
]


def conectar():
    return psycopg2.connect(
        dbname=os.environ.get("DB_NAME", "ventas_industriales"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("POSTGRES_PASSWORD", "ergon_test_pwd_2026"),
        host=os.environ.get("DB_HOST", "db"),
        port=os.environ.get("DB_PORT", "5432"),
    )


def leer_hojas_xlsx(ruta: Path) -> dict[str, list[list[str | None]]]:
    z = zipfile.ZipFile(ruta)
    ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    sheets: dict[str, list[list[str | None]]] = {}
    for idx, sh in enumerate(wb.iter(ns + "sheet"), 1):
        name = sh.attrib["name"]
        if name == "Notas":
            continue
        root = ET.fromstring(z.read(f"xl/worksheets/sheet{idx}.xml"))
        rows = []
        for r in list(root.iter(ns + "row"))[1:]:
            vals = []
            for c in r.iter(ns + "c"):
                if c.attrib.get("t") == "inlineStr":
                    v = "".join(x.text or "" for x in c.iter(ns + "t"))
                else:
                    vn = c.find(ns + "v")
                    v = vn.text if vn is not None else ""
                vals.append(None if v == "" else v)
            if vals and any(x is not None for x in vals):
                rows.append(vals)
        sheets[name] = rows
    return sheets


def poblar_y_migrar_si_hace_falta(conn) -> None:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT EXISTS (SELECT 1 FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_name = 'modelo_producto')"
        )
        ya_migrada = cur.fetchone()[0]

        if not ya_migrada:
            print("==> 1. Poblando base desde base_datos_pedidos2.xlsx (2,702 registros)...")
            sheets = leer_hojas_xlsx(XLSX_FILE)
            for tabla, columnas in BASE_TABLES:
                filas = sheets[tabla]
                buf = StringIO()
                writer = csv.writer(buf, lineterminator="\n")
                writer.writerows(filas)
                buf.seek(0)
                cols_sql = sql.SQL(", ").join(sql.Identifier(c) for c in columnas)
                copy_q = sql.SQL("COPY public.{} ({}) FROM STDIN WITH (FORMAT CSV, NULL '')").format(
                    sql.Identifier(tabla), cols_sql
                )
                cur.copy_expert(copy_q.as_string(cur), buf)
            print("==> 2. Aplicando migración 003-normalizacion.sql sobre la base poblada...")
            cur.execute(MIG_003.read_text(encoding="utf-8"))
            conn.commit()
            print("    Migración 003 aplicada con éxito (esquema en 3FN/BCNF).")
        else:
            print("==> 1. La base ya se encuentra poblada y normalizada en 3FN/BCNF.")

        print("\nResumen de tablas en PostgreSQL (esquema normalizado):")
        tablas_norm = [
            "modelo_producto", "producto", "cliente", "estado_ubicacion",
            "ciudad_ubicacion", "sucursal", "transportista", "pedido", "detalle", "envio"
        ]
        for t in tablas_norm:
            cur.execute(sql.SQL("SELECT COUNT(*) FROM public.{}").format(sql.Identifier(t)))
            n = cur.fetchone()[0]
            print(f"  - {t:<18}: {n:>5} filas")


def formatear_tabla(encabezados: list[str], filas: list[tuple]) -> str:
    str_filas = [[("NULL" if v is None else str(v)) for v in f] for f in filas]
    anchos = [len(h) for h in encabezados]
    for f in str_filas:
        for i, val in enumerate(f):
            anchos[i] = max(anchos[i], len(val))
    sep = "+-" + "-+-".join("-" * w for w in anchos) + "-+"
    hdr = "| " + " | ".join(h.ljust(w) for h, w in zip(encabezados, anchos)) + " |"
    lineas = [sep, hdr, sep]
    for f in str_filas:
        lineas.append("| " + " | ".join(v.ljust(w) for v, w in zip(f, anchos)) + " |")
    lineas.append(sep)
    lineas.append(f"({len(filas)} filas)")
    return "\n".join(lineas)


def ejecutar_consultas(conn) -> None:
    print("\n" + "=" * 78)
    print("PARTE 2: EJECUCIÓN DE LAS CONSULTAS EN ÁLGEBRA RELACIONAL Y SQL")
    print("=" * 78)

    archivos = sorted(CONSULTAS_DIR.glob("*.sql"))
    with conn.cursor() as cur:
        for idx, archivo in enumerate(archivos, 1):
            texto = archivo.read_text(encoding="utf-8")
            pregunta = ""
            algebra = ""
            sentencias = []
            for linea in texto.splitlines():
                if linea.startswith("-- PREGUNTA:"):
                    pregunta = linea.replace("-- PREGUNTA:", "").strip()
                elif linea.startswith("-- ALGEBRA:"):
                    algebra = linea.replace("-- ALGEBRA:", "").strip()
                elif not linea.strip().startswith("--"):
                    sentencias.append(linea)
            sql_query = "\n".join(sentencias).strip()

            cur.execute(sql_query)
            filas = cur.fetchall()
            cols = [desc[0] for desc in cur.description]

            print(f"\n--- Consulta {idx:02d} ({archivo.name}) ---")
            print(f"1. Pregunta : {pregunta}")
            print(f"2. Álgebra  : {algebra}")
            print("3. Resultado:")
            print(formatear_tabla(cols, filas))


def main() -> int:
    conn = conectar()
    try:
        poblar_y_migrar_si_hace_falta(conn)
        ejecutar_consultas(conn)
    finally:
        conn.close()

    print("\n" + "=" * 78)
    print("PARTE 3: REGENERACIÓN DEL GRUPO DE RELAX DESDE LA BASE NORMALIZADA")
    print("=" * 78)
    res = subprocess.run([sys.executable, str(EXPORTAR_SCRIPT)], check=True)
    return res.returncode


if __name__ == "__main__":
    raise SystemExit(main())
