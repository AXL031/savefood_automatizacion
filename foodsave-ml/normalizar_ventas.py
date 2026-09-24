"""Valida ventas diarias de un comercio y genera un CSV uniforme.

Uso:
  python foodsave-ml/normalizar_ventas.py --entrada ventas.csv --salida carpeta
  python foodsave-ml/normalizar_ventas.py --entrada tickets.csv \
      --formato transacciones --salida carpeta
  python foodsave-ml/normalizar_ventas.py --entrada bakery_sales_limpio.csv \
      --formato bakery --comercio piloto --sucursal principal --salida carpeta
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


COLUMNAS = [
    "comercio_id", "sucursal_id", "fecha_local", "producto_id", "unidades_vendidas"
]


def _validar_ids(frame: pd.DataFrame) -> None:
    for col in ["comercio_id", "sucursal_id", "producto_id"]:
        frame[col] = frame[col].astype("string").str.strip()
        if frame[col].isna().any() or frame[col].eq("").any():
            raise ValueError(f"{col} tiene valores vacíos")


def _validar_fechas(frame: pd.DataFrame) -> None:
    originales = frame["fecha_local"].astype("string")
    convertidas = pd.to_datetime(originales, format="%Y-%m-%d", errors="coerce")
    if convertidas.isna().any() or not originales.eq(convertidas.dt.strftime("%Y-%m-%d")).all():
        raise ValueError("fecha_local debe usar fechas válidas YYYY-MM-DD")
    frame["fecha_local"] = convertidas.dt.strftime("%Y-%m-%d")


def _validar_cantidades(frame: pd.DataFrame) -> None:
    cantidad = pd.to_numeric(frame["unidades_vendidas"], errors="coerce")
    if cantidad.isna().any() or not np.isfinite(cantidad).all():
        raise ValueError("unidades_vendidas debe ser numérica y finita")
    if (cantidad < 0).any() or (cantidad % 1 != 0).any():
        raise ValueError("unidades_vendidas debe ser un entero no negativo")
    frame["unidades_vendidas"] = cantidad.astype("int64")


def normalizar(entrada: Path, formato: str, comercio: str | None, sucursal: str | None):
    original = pd.read_csv(entrada, dtype="string")
    original.columns = original.columns.str.strip()
    if original.empty:
        raise ValueError("El archivo no tiene filas")

    negativos_excluidos = 0
    if formato == "estandar":
        faltan = set(COLUMNAS) - set(original.columns)
        if faltan:
            raise ValueError(f"Faltan columnas: {sorted(faltan)}")
        frame = original[COLUMNAS].copy()
    elif formato == "transacciones":
        requeridas = set(COLUMNAS + ["transaccion_id", "linea_id"])
        faltan = requeridas - set(original.columns)
        if faltan:
            raise ValueError(f"Faltan columnas de transacciones: {sorted(faltan)}")
        frame = original[COLUMNAS + ["transaccion_id", "linea_id"]].copy()
        for col in ["transaccion_id", "linea_id"]:
            frame[col] = frame[col].astype("string").str.strip()
            if frame[col].isna().any() or frame[col].eq("").any():
                raise ValueError(f"{col} tiene valores vacíos")
    elif formato == "bakery":
        faltan = {"date", "article", "Quantity"} - set(original.columns)
        if faltan:
            raise ValueError(f"Faltan columnas legacy: {sorted(faltan)}")
        if not comercio or not sucursal:
            raise ValueError("El formato bakery requiere --comercio y --sucursal")
        frame = original[["date", "article", "Quantity"]].rename(
            columns={"date": "fecha_local", "article": "producto_id",
                     "Quantity": "unidades_vendidas"}
        ).copy()
        frame.insert(0, "sucursal_id", sucursal)
        frame.insert(0, "comercio_id", comercio)
        cantidad = pd.to_numeric(frame["unidades_vendidas"], errors="coerce")
        if cantidad.isna().any():
            raise ValueError("Quantity contiene valores no numéricos")
        negativos_excluidos = int((cantidad < 0).sum())
        frame = frame.loc[cantidad >= 0].copy()
    else:
        raise ValueError("formato debe ser estandar, transacciones o bakery")

    if frame.empty:
        raise ValueError("No quedan ventas después de limpiar")
    _validar_ids(frame)
    _validar_fechas(frame)
    _validar_cantidades(frame)

    claves = COLUMNAS[:4]
    if formato == "estandar":
        duplicadas = frame.duplicated(claves, keep=False)
        if duplicadas.any():
            raise ValueError(
                f"Hay {int(duplicadas.sum())} filas con clave sucursal-fecha-producto duplicada"
            )
    elif formato == "transacciones":
        clave_linea = [
            "comercio_id", "sucursal_id", "fecha_local", "transaccion_id", "linea_id"
        ]
        if frame.duplicated(clave_linea, keep=False).any():
            raise ValueError("Hay líneas de transacción duplicadas")
        frame = frame.groupby(claves, as_index=False)["unidades_vendidas"].sum()
    else:
        frame = frame.groupby(claves, as_index=False)["unidades_vendidas"].sum()

    frame = frame[COLUMNAS].sort_values(claves).reset_index(drop=True)
    resumen = []
    for (comercio_id, sucursal_id), grupo in frame.groupby(
        ["comercio_id", "sucursal_id"], sort=True
    ):
        fechas = pd.DatetimeIndex(pd.to_datetime(grupo.fecha_local.unique()))
        periodo = pd.date_range(fechas.min(), fechas.max(), freq="D")
        dias_con_ventas = grupo.loc[grupo.unidades_vendidas > 0, "fecha_local"].nunique()
        resumen.append({
            "comercio_id": str(comercio_id), "sucursal_id": str(sucursal_id),
            "primera_fecha": str(fechas.min().date()),
            "ultima_fecha": str(fechas.max().date()),
            "fechas_con_registro": int(len(fechas)),
            "fechas_con_ventas": int(dias_con_ventas),
            "fechas_sin_registro": int(len(periodo.difference(fechas))),
            "productos": int(grupo.producto_id.nunique()),
            "filas_producto_dia": int(len(grupo)),
            "unidades": int(grupo.unidades_vendidas.sum()),
            "pasa_minimo_180_fechas_con_ventas": bool(dias_con_ventas >= 180),
        })

    informe = {
        "formato_entrada": formato,
        "filas_originales": int(len(original)),
        "negativos_excluidos": negativos_excluidos,
        "filas_diarias_normalizadas": int(len(frame)),
        "politica_ausencias": "desconocido; no se imputan ceros",
        "sucursales": resumen,
    }
    return frame, informe


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", required=True, type=Path)
    parser.add_argument("--salida", required=True, type=Path)
    parser.add_argument(
        "--formato", choices=["estandar", "transacciones", "bakery"], default="estandar"
    )
    parser.add_argument("--comercio")
    parser.add_argument("--sucursal")
    args = parser.parse_args()
    frame, informe = normalizar(args.entrada, args.formato, args.comercio, args.sucursal)
    args.salida.mkdir(parents=True, exist_ok=True)
    frame.to_csv(args.salida / "ventas_diarias_normalizadas.csv", index=False)
    (args.salida / "calidad.json").write_text(
        json.dumps(informe, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(informe, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
