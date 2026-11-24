#!/usr/bin/env python3
"""Ejercicio 2.1: Exporta una muestra de la base normalizada (10 a 30 filas por tabla)
conservando la integridad referencial al formato de grupo de RelaX (grupo.txt).
"""
from __future__ import annotations

import argparse
import os
import zipfile
import xml.etree.ElementTree as ET
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = Path(__file__).resolve().parent / "grupo.txt"
DEFAULT_XLSX = ROOT / "datos" / "base_datos_pedidos2.xlsx"

CLIENT_IDS = (1001, 1002, 1003, 1004, 1008, 1014, 1019, 1026, 1031, 1037, 1049, 1052, 1065, 1071)
PRODUCT_IDS = (
    "HV2-01", "HV2-02", "HV2-03", "HV2-04",
    "HPB-01", "HPB-02", "HPB-03", "HPB-04",
    "OA1-01", "OA1-02", "OA1-03", "OA1-04",
    "HG5-01", "HG5-02", "HG5-03", "HG5-04",
    "HGL-04", "HP1-02", "HPL-01",
)
SUCURSAL_KEYS = (
    (1001, "S01"), (1002, "S01"), (1003, "S01"), (1004, "S01"), (1008, "S01"), (1014, "S01"),
    (1019, "S01"), (1026, "S01"), (1031, "S01"), (1037, "S01"), (1049, "S01"), (1052, "S01"), (1065, "S01"), (1071, "S01"),
    (1019, "S02"), (1052, "S02"), (1019, "S03"), (1004, "S02"), (1004, "S03"), (1052, "S03"),
)
FOLIO_IDS = (
    100001, 100002, 100003, 100004, 100010, 100016, 100023, 100031,
    100036, 100042, 100044, 100059, 100136, 100245, 100281,
)

SCHEMAS = [
    ("modelo_producto", [("modeloproducto", "string"), ("tipoproducto", "string")]),
    ("producto", [
        ("claveproducto", "string"), ("modeloproducto", "string"),
        ("costounitariousd", "number"), ("preciounitariousd", "number"),
        ("provmaquinaria", "string"), ("provtransformador", "string"), ("provtransporte", "string"),
    ]),
    ("cliente", [
        ("numerocliente", "number"), ("razonsocial", "string"), ("correocliente", "string"),
        ("telefonocliente", "string"), ("tipocliente", "string"), ("rfc", "string"),
        ("regimenfiscal", "string"), ("estadoorigen", "string"),
        ("idfiscalglobal", "string"), ("paisreceptor", "string"),
    ]),
    ("estado_ubicacion", [("estado", "string"), ("pais", "string")]),
    ("ciudad_ubicacion", [("ciudad", "string"), ("estado", "string")]),
    ("sucursal", [
        ("numerocliente", "number"), ("clavesucursal", "string"), ("nombreplanta", "string"),
        ("telefonoencargado", "string"), ("calle", "string"), ("numero", "string"),
        ("ciudad", "string"), ("cp", "string"),
    ]),
    ("transportista", [
        ("clavetransportista", "string"), ("nombreempresa", "string"),
        ("telefonoatencion", "string"), ("email", "string"),
        ("esnacional", "boolean"), ("esinternacional", "boolean"),
        ("rfc", "string"), ("codigoaduanal", "string"), ("agenciaaduanal", "string"),
    ]),
    ("pedido", [
        ("folio", "number"), ("numerocliente", "number"), ("estatus", "string"),
        ("dia", "number"), ("mes", "number"), ("anio", "number"), ("activo", "boolean"),
    ]),
    ("detalle", [
        ("folio", "number"), ("claveparcial", "number"), ("claveproducto", "string"),
        ("costoproduccion", "number"), ("precioaplicado", "number"), ("cantidad", "number"),
    ]),
    ("envio", [
        ("numeroguia", "string"), ("folio", "number"), ("clavetransportista", "string"),
        ("numerocliente", "number"), ("clavesucursal", "string"), ("costoflete", "number"),
        ("dia", "number"), ("mes", "number"), ("anio", "number"),
    ]),
]


def fmt_val(val, tipo: str) -> str:
    if val is None or val == "":
        return "null"
    if tipo == "boolean":
        if isinstance(val, bool):
            return "true" if val else "false"
        s = str(val).strip().lower()
        return "true" if s in ("1", "true", "t", "yes") else "false"
    if tipo == "number":
        if isinstance(val, (int, Decimal)):
            return str(val)
        f = float(val)
        if f.is_integer():
            return str(int(f))
        return f"{f:.2f}".rstrip("0").rstrip(".")
    s = str(val).replace("'", "\\'")
    return f"'{s}'"


def cargar_desde_postgres() -> dict[str, list[tuple]]:
    import psycopg2

    conn = psycopg2.connect(
        dbname=os.environ.get("DB_NAME", "ventas_industriales"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("POSTGRES_PASSWORD", os.environ.get("APP_DB_PASSWORD", "postgres_test_pwd")),
        host=os.environ.get("DB_HOST", "127.0.0.1"),
        port=os.environ.get("DB_PORT", "5434"),
    )
    tablas: dict[str, list[tuple]] = {}
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT modeloproducto, tipoproducto FROM modelo_producto ORDER BY modeloproducto")
            tablas["modelo_producto"] = cur.fetchall()

            cur.execute(
                "SELECT claveproducto, modeloproducto, costounitariousd, preciounitariousd, "
                "provmaquinaria, provtransformador, provtransporte "
                "FROM producto WHERE claveproducto IN %s ORDER BY claveproducto",
                (PRODUCT_IDS,),
            )
            tablas["producto"] = cur.fetchall()

            cur.execute(
                "SELECT numerocliente, razonsocial, correocliente, telefonocliente, tipocliente, "
                "rfc, regimenfiscal, estadoorigen, idfiscalglobal, paisreceptor "
                "FROM cliente WHERE numerocliente IN %s ORDER BY numerocliente",
                (CLIENT_IDS,),
            )
            tablas["cliente"] = cur.fetchall()

            cur.execute(
                "SELECT numerocliente, clavesucursal, nombreplanta, telefonoencargado, calle, numero, ciudad, cp "
                "FROM sucursal WHERE (numerocliente, clavesucursal) IN %s ORDER BY numerocliente, clavesucursal",
                (SUCURSAL_KEYS,),
            )
            tablas["sucursal"] = cur.fetchall()
            ciudades_usadas = tuple({r[6] for r in tablas["sucursal"]})

            cur.execute(
                "SELECT ciudad, estado FROM ciudad_ubicacion WHERE ciudad IN %s ORDER BY ciudad",
                (ciudades_usadas,),
            )
            tablas["ciudad_ubicacion"] = cur.fetchall()
            estados_usados = tuple({r[1] for r in tablas["ciudad_ubicacion"]})

            cur.execute(
                "SELECT estado, pais FROM estado_ubicacion WHERE estado IN %s ORDER BY estado",
                (estados_usados,),
            )
            tablas["estado_ubicacion"] = cur.fetchall()

            cur.execute(
                "SELECT folio, numerocliente, estatus, dia, mes, anio, activo "
                "FROM pedido WHERE folio IN %s ORDER BY folio",
                (FOLIO_IDS,),
            )
            tablas["pedido"] = cur.fetchall()

            cur.execute(
                "SELECT numeroguia, folio, clavetransportista, numerocliente, clavesucursal, costoflete, dia, mes, anio "
                "FROM envio WHERE folio IN %s ORDER BY folio",
                (FOLIO_IDS,),
            )
            tablas["envio"] = cur.fetchall()
            transp_usados = tuple({r[2] for r in tablas["envio"]})

            cur.execute(
                "SELECT clavetransportista, nombreempresa, telefonoatencion, email, esnacional, esinternacional, rfc, codigoaduanal, agenciaaduanal "
                "FROM transportista WHERE clavetransportista IN %s "
                "UNION "
                "(SELECT clavetransportista, nombreempresa, telefonoatencion, email, esnacional, esinternacional, rfc, codigoaduanal, agenciaaduanal "
                " FROM transportista WHERE clavetransportista NOT IN %s ORDER BY clavetransportista LIMIT %s) "
                "ORDER BY clavetransportista",
                (transp_usados, transp_usados, max(0, 15 - len(transp_usados))),
            )
            tablas["transportista"] = cur.fetchall()

            cur.execute(
                "SELECT folio, claveparcial, claveproducto, costoproduccion, precioaplicado, cantidad "
                "FROM ("
                "  SELECT folio, claveparcial, claveproducto, costoproduccion, precioaplicado, cantidad "
                "  FROM detalle WHERE folio IN %s AND claveproducto IN %s "
                "  ORDER BY (CASE WHEN claveproducto LIKE 'HPB%%' OR claveproducto LIKE 'HPL%%' OR claveproducto LIKE 'HV2%%' THEN 0 ELSE 1 END), folio, claveparcial "
                "  LIMIT 28"
                ") sub ORDER BY folio, claveparcial",
                (FOLIO_IDS, PRODUCT_IDS),
            )
            tablas["detalle"] = cur.fetchall()
    finally:
        conn.close()
    return tablas


def cargar_desde_excel(ruta_xlsx: Path) -> dict[str, list[tuple]]:
    z = zipfile.ZipFile(ruta_xlsx)
    ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    wb = ET.fromstring(z.read("xl/workbook.xml"))
    sheets = {}
    for idx, sh in enumerate(wb.iter(ns + "sheet"), 1):
        name = sh.attrib["name"]
        if name == "Notas":
            continue
        root = ET.fromstring(z.read(f"xl/worksheets/sheet{idx}.xml"))
        rows = []
        for r in root.iter(ns + "row"):
            vals = []
            for c in r.iter(ns + "c"):
                if c.attrib.get("t") == "inlineStr":
                    vals.append("".join(x.text or "" for x in c.iter(ns + "t")))
                else:
                    v = c.find(ns + "v")
                    vals.append(v.text if v is not None else "")
            rows.append(vals)
        sheets[name] = rows[1:]

    tablas: dict[str, list[tuple]] = {}
    modelos = sorted({(r[1], r[4]) for r in sheets["producto"]})
    tablas["modelo_producto"] = modelos

    prods = [
        (r[0], r[1], r[2], r[3], r[5], r[6], r[7])
        for r in sheets["producto"]
        if r[0] in PRODUCT_IDS
    ]
    tablas["producto"] = sorted(prods, key=lambda x: x[0])

    clientes = [tuple(r) for r in sheets["cliente"] if int(r[0]) in CLIENT_IDS]
    tablas["cliente"] = sorted(clientes, key=lambda x: int(x[0]))

    suc_set = set(SUCURSAL_KEYS)
    sucursales = [r for r in sheets["sucursal"] if (int(r[0]), r[1]) in suc_set]
    ciudades = sorted({(r[6], r[7]) for r in sucursales})
    estados_set = {e for _, e in ciudades}
    estados = sorted({(r[7], r[8]) for r in sucursales if r[7] in estados_set})
    tablas["estado_ubicacion"] = estados
    tablas["ciudad_ubicacion"] = ciudades
    tablas["sucursal"] = sorted(
        [(int(r[0]), r[1], r[2], r[3], r[4], r[5], r[6], r[9]) for r in sucursales],
        key=lambda x: (x[0], x[1]),
    )

    folio_set = {str(f) for f in FOLIO_IDS}
    pedidos_sel = sorted([r for r in sheets["pedido"] if int(r[0]) in FOLIO_IDS], key=lambda r: int(r[0]))
    tablas["pedido"] = [(int(r[0]), int(r[1]), r[2], int(r[3]), int(r[4]), int(r[5]), r[6]) for r in pedidos_sel]

    envios_sel = sorted([r for r in sheets["envio"] if r[1] in folio_set], key=lambda r: int(r[1]))
    tablas["envio"] = [
        (r[0], int(r[1]), r[2], int(r[3]), r[4], r[5], int(r[6]), int(r[7]), int(r[8]))
        for r in envios_sel
    ]

    transp_usados = {r[2] for r in envios_sel}
    extra_transp = [r[0] for r in sheets["transportista"] if r[0] not in transp_usados][: max(0, 15 - len(transp_usados))]
    transp_set = transp_usados | set(extra_transp)
    transp_sel = sorted([r for r in sheets["transportista"] if r[0] in transp_set], key=lambda r: r[0])
    tablas["transportista"] = [tuple(r) for r in transp_sel]

    detalles_cand = [r for r in sheets["detalle"] if r[0] in folio_set and r[2] in PRODUCT_IDS]
    detalles_cand.sort(key=lambda r: (0 if r[2].startswith(("HPB", "HPL", "HV2")) else 1, int(r[0]), int(r[1])))
    detalles_sel = sorted(detalles_cand[:28], key=lambda r: (int(r[0]), int(r[1])))
    tablas["detalle"] = [(int(r[0]), int(r[1]), r[2], r[3], r[4], int(r[5])) for r in detalles_sel]

    return tablas


def generar_grupo_txt(tablas: dict[str, list[tuple]]) -> str:
    lineas = [
        "group: Proyecto Propio ERGON (Esquema Normalizado 3FN/BCNF)",
        "description: Muestra de 10 a 30 filas por tabla con integridad referencial completa.",
        "",
    ]
    for nombre_tabla, cols in SCHEMAS:
        filas = tablas[nombre_tabla]
        if not (10 <= len(filas) <= 30):
            raise ValueError(f"La tabla {nombre_tabla} tiene {len(filas)} filas (debe tener entre 10 y 30).")
        encabezado_cols = ", ".join(f"{c}:{t}" for c, t in cols)
        lineas.append(f"{nombre_tabla} = {{")
        lineas.append(f"  {encabezado_cols}")
        for fila in filas:
            valores_fmt = ", ".join(fmt_val(v, t) for v, (_, t) in zip(fila, cols))
            lineas.append(f"  {valores_fmt}")
        lineas.append("}")
        lineas.append("")
    return "\n".join(lineas)


def main() -> int:
    parser = argparse.ArgumentParser(description="Exporta muestra normalizada al formato de grupo de RelaX.")
    parser.add_argument("--salida", type=Path, default=DEFAULT_OUT, help="Ruta de grupo.txt")
    parser.add_argument("--offline", action="store_true", help="Usar el Excel si PostgreSQL no está levantado")
    args = parser.parse_args()

    try:
        if args.offline:
            raise RuntimeError("Modo offline solicitado")
        tablas = cargar_desde_postgres()
        origen = "PostgreSQL (ventas_industriales)"
    except Exception:
        tablas = cargar_desde_excel(DEFAULT_XLSX)
        origen = f"Excel normalizado ({DEFAULT_XLSX.name})"

    contenido = generar_grupo_txt(tablas)
    args.salida.write_text(contenido, encoding="utf-8")
    print(f"Grupo de RelaX regenerado desde {origen} en: {args.salida}")
    for nombre_tabla, _ in SCHEMAS:
        print(f"  - {nombre_tabla}: {len(tablas[nombre_tabla])} renglones")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
