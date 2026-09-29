"""Construcción del vector de 13 características del contrato de inferencia.

Las características y su orden son contractuales (CONTRATO_ARTEFACTO_INFERENCIA.md):

  1.  article          — SKU externo textual (categoría CatBoost)
  2.  dia_semana       — lunes=0 … domingo=6
  3.  mes              — 1..12
  4.  dia_mes          — 1..31
  5.  fin_semana       — 1 si sáb/dom, 0 en otro caso
  6.  ventas_ayer      — valor un día antes o NaN
  7.  ventas_hace_7_dias
  8.  promedio_7_dias  — promedio de observaciones conocidas de los 7 días anteriores; NaN si ninguna
  9.  promedio_14_dias
 10.  promedio_28_dias
 11.  conteo_7_dias    — cantidad de observaciones conocidas en 7 días
 12.  conteo_14_dias
 13.  conteo_28_dias

Las ventanas avanzan por DÍAS CALENDARIO, no por filas.
Un día ausente conserva valor faltante (NaN); NO se imputa cero.
Todas las entradas son ANTERIORES a fecha_objetivo.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


# Orden contractual — no reordenar sin cambiar version_modelo y metadata.json
FEATURES: list[str] = [
    "article",
    "dia_semana",
    "mes",
    "dia_mes",
    "fin_semana",
    "ventas_ayer",
    "ventas_hace_7_dias",
    "promedio_7_dias",
    "promedio_14_dias",
    "promedio_28_dias",
    "conteo_7_dias",
    "conteo_14_dias",
    "conteo_28_dias",
]

# Características categóricas que CatBoost debe conocer
CAT_FEATURES: list[str] = ["article"]


def _pivot_diario(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte el CSV normalizado en una tabla pivote (fecha × producto).

    Solo se consideran filas con unidades_vendidas > 0 observadas
    (ausencia de fila = venta desconocida, no cero).
    """
    pivot = df.pivot_table(
        index="fecha_local",
        columns="producto_id",
        values="unidades_vendidas",
        aggfunc="sum",
    )
    return pivot


def _ventana_promedio(serie: pd.Series, dias: int) -> pd.Series:
    """Promedio de observaciones CONOCIDAS en la ventana deslizante de `dias` días.

    Usa min_periods=1 para calcular cuando hay al menos una observación;
    devuelve NaN solo si no hay ninguna observación en la ventana.
    """
    return serie.rolling(window=dias, min_periods=1).mean().shift(1)


def _ventana_conteo(serie: pd.Series, dias: int) -> pd.Series:
    """Cuenta de días con observación CONOCIDA en la ventana deslizante."""
    return serie.notna().rolling(window=dias, min_periods=0).sum().shift(1).fillna(0).astype(int)


def construir_features(
    csv_path: Path,
    comercio_id: str,
    sucursal_id: str,
    inicio: str,
    fin: str,
) -> pd.DataFrame:
    """Construye el DataFrame de features para el rango [inicio, fin] inclusive.

    Args:
        csv_path: CSV normalizado (comercio_id, sucursal_id, fecha_local,
                  producto_id, unidades_vendidas).
        comercio_id: ID del comercio a filtrar.
        sucursal_id: ID de la sucursal a filtrar.
        inicio: Fecha inicial del rango objetivo (YYYY-MM-DD).
        fin: Fecha final del rango objetivo (YYYY-MM-DD).

    Returns:
        DataFrame con columnas FEATURES más 'fecha_objetivo' y 'unidades_vendidas'.
        Cada fila es un par (producto, fecha_objetivo).
    """
    df = pd.read_csv(csv_path)
    df["fecha_local"] = pd.to_datetime(df["fecha_local"])

    mask = (df["comercio_id"] == comercio_id) & (df["sucursal_id"] == sucursal_id)
    df = df.loc[mask].copy()

    if df.empty:
        raise ValueError(
            f"Sin datos para comercio={comercio_id!r}, sucursal={sucursal_id!r}"
        )

    productos = df["producto_id"].unique()

    # Pivot: índice=fecha, columnas=producto
    pivot = df.pivot_table(
        index="fecha_local",
        columns="producto_id",
        values="unidades_vendidas",
        aggfunc="sum",
    )

    # Rango completo por días calendario para cubrir ausencias
    rango_completo = pd.date_range(
        start=pivot.index.min() - pd.Timedelta(days=28),
        end=pd.Timestamp(fin),
        freq="D",
    )
    pivot = pivot.reindex(rango_completo)  # NaN donde no hay venta conocida

    registros: list[dict] = []

    for producto in productos:
        if producto not in pivot.columns:
            continue

        serie = pivot[producto]

        ventas_ayer = serie.shift(1)
        ventas_hace_7 = serie.shift(7)
        prom_7 = _ventana_promedio(serie, 7)
        prom_14 = _ventana_promedio(serie, 14)
        prom_28 = _ventana_promedio(serie, 28)
        conteo_7 = _ventana_conteo(serie, 7)
        conteo_14 = _ventana_conteo(serie, 14)
        conteo_28 = _ventana_conteo(serie, 28)

        fechas_objetivo = pd.date_range(inicio, fin, freq="D")

        for fecha in fechas_objetivo:
            if fecha not in serie.index:
                continue

            registros.append({
                "fecha_objetivo": fecha,
                "article": producto,
                "dia_semana": fecha.dayofweek,
                "mes": fecha.month,
                "dia_mes": fecha.day,
                "fin_semana": int(fecha.dayofweek >= 5),
                "ventas_ayer": ventas_ayer.get(fecha, np.nan),
                "ventas_hace_7_dias": ventas_hace_7.get(fecha, np.nan),
                "promedio_7_dias": prom_7.get(fecha, np.nan),
                "promedio_14_dias": prom_14.get(fecha, np.nan),
                "promedio_28_dias": prom_28.get(fecha, np.nan),
                "conteo_7_dias": conteo_7.get(fecha, 0),
                "conteo_14_dias": conteo_14.get(fecha, 0),
                "conteo_28_dias": conteo_28.get(fecha, 0),
                "unidades_vendidas": serie.get(fecha, np.nan),
            })

    if not registros:
        raise ValueError(
            f"No se pudo construir ninguna fila de features para el rango {inicio}–{fin}"
        )

    result = pd.DataFrame(registros)
    result["conteo_7_dias"] = result["conteo_7_dias"].astype(int)
    result["conteo_14_dias"] = result["conteo_14_dias"].astype(int)
    result["conteo_28_dias"] = result["conteo_28_dias"].astype(int)

    # Verificar orden contractual
    for col in FEATURES:
        if col not in result.columns:
            raise RuntimeError(
                f"La columna contractual '{col}' no fue generada. "
                "Revisar CONTRATO_ARTEFACTO_INFERENCIA.md"
            )

    return result
