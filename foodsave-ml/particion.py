"""Calcula la partición temporal de entrenamiento/validación/prueba.

Aplica la política definida en POLITICA_EVALUACION.md:

  Historial válido         | Entrenamiento | Validación | Prueba
  24 meses o más           | inicio → v    | 3 meses    | 6 meses
  12 a menos de 24 meses   | inicio → v    | 3 meses    | 3 meses
  6 a menos de 12 meses    | inicio → v    | 1 mes      | 1 mes
  Menos de 6 meses         | Sin evaluación suficiente para la demo

Los cortes se alinean con meses calendario completos. El primer y último mes
incompleto quedan fuera del conteo y de la partición.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd


@dataclass
class Particion:
    """Fechas inclusivas de cada tramo del historial."""

    inicio_entrenamiento: str   # YYYY-MM-DD
    fin_entrenamiento: str      # YYYY-MM-DD (último día antes de validación)
    inicio_validacion: str      # YYYY-MM-DD
    fin_validacion: str         # YYYY-MM-DD (último día antes de prueba)
    inicio_prueba: str          # YYYY-MM-DD
    fin_prueba: str             # YYYY-MM-DD
    meses_validos: int
    meses_validacion: int
    meses_prueba: int

    def as_dict(self) -> dict:
        return {
            "version_politica": "POLITICA_EVALUACION_v1",
            "inicio_entrenamiento": self.inicio_entrenamiento,
            "fin_entrenamiento": self.fin_entrenamiento,
            "inicio_validacion": self.inicio_validacion,
            "fin_validacion": self.fin_validacion,
            "inicio_prueba": self.inicio_prueba,
            "fin_prueba": self.fin_prueba,
            "meses_validos": self.meses_validos,
            "meses_validacion": self.meses_validacion,
            "meses_prueba": self.meses_prueba,
        }


def _primer_dia_mes(year: int, month: int) -> pd.Timestamp:
    return pd.Timestamp(year=year, month=month, day=1)


def _ultimo_dia_mes(year: int, month: int) -> pd.Timestamp:
    return (_primer_dia_mes(year, month) + pd.offsets.MonthEnd(0))


def _meses_completos_entre(primera: pd.Timestamp, ultima: pd.Timestamp) -> list[tuple[int, int]]:
    """Devuelve lista de (año, mes) de meses calendario COMPLETOS entre primera y ultima.

    Un mes es completo si primera_fecha <= primer día del mes y
    ultimo_dia_del_mes <= ultima_fecha.
    """
    meses = []
    cursor = _primer_dia_mes(primera.year, primera.month)
    while cursor <= ultima:
        fin = _ultimo_dia_mes(cursor.year, cursor.month)
        if cursor >= primera and fin <= ultima:
            meses.append((cursor.year, cursor.month))
        cursor += pd.offsets.MonthBegin(1)
    return meses


def calcular_particion(
    csv_path: Path,
    comercio_id: str,
    sucursal_id: str,
) -> Particion:
    """Lee el CSV normalizado y calcula la partición temporal para el comercio/sucursal.

    Raises:
        ValueError: si no hay suficiente historial para la demo (< 6 meses completos).
    """
    df = pd.read_csv(csv_path, usecols=["comercio_id", "sucursal_id", "fecha_local"])
    df["fecha_local"] = pd.to_datetime(df["fecha_local"])
    filtro = (df["comercio_id"] == comercio_id) & (df["sucursal_id"] == sucursal_id)
    subset = df.loc[filtro, "fecha_local"]

    if subset.empty:
        raise ValueError(
            f"No se encontraron ventas para comercio={comercio_id!r}, "
            f"sucursal={sucursal_id!r} en {csv_path}"
        )

    primera = subset.min()
    ultima = subset.max()
    meses_completos = _meses_completos_entre(primera, ultima)
    n = len(meses_completos)

    if n < 6:
        raise ValueError(
            f"Historial insuficiente para la demo: solo {n} mes(es) completo(s). "
            f"Se necesitan al menos 6. Período observado: {primera.date()} a {ultima.date()}"
        )

    # Determinar duración de validación y prueba según política
    if n >= 24:
        meses_prueba = 6
        meses_val = 3
    elif n >= 12:
        meses_prueba = 3
        meses_val = 3
    else:  # 6 <= n < 12
        meses_prueba = 1
        meses_val = 1

    # Separar tramos desde el final de la lista de meses completos
    meses_prueba_list = meses_completos[-meses_prueba:]
    meses_val_list = meses_completos[-(meses_prueba + meses_val):-meses_prueba]
    meses_train_list = meses_completos[:-(meses_prueba + meses_val)]

    if not meses_train_list:
        raise ValueError(
            f"No quedan meses para entrenamiento con {n} mes(es) completo(s), "
            f"validación={meses_val} y prueba={meses_prueba}."
        )

    inicio_train = _primer_dia_mes(*meses_train_list[0])
    fin_train = _ultimo_dia_mes(*meses_train_list[-1])
    inicio_val = _primer_dia_mes(*meses_val_list[0])
    fin_val = _ultimo_dia_mes(*meses_val_list[-1])
    inicio_prueba = _primer_dia_mes(*meses_prueba_list[0])
    fin_prueba = _ultimo_dia_mes(*meses_prueba_list[-1])

    return Particion(
        inicio_entrenamiento=str(inicio_train.date()),
        fin_entrenamiento=str(fin_train.date()),
        inicio_validacion=str(inicio_val.date()),
        fin_validacion=str(fin_val.date()),
        inicio_prueba=str(inicio_prueba.date()),
        fin_prueba=str(fin_prueba.date()),
        meses_validos=n,
        meses_validacion=meses_val,
        meses_prueba=meses_prueba,
    )
