"""Métricas de evaluación del pronóstico según POLITICA_EVALUACION.md.

Define las estructuras de datos y contratos para representar pares
de evaluación (predicción vs real) y el resumen métrico resultante.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class ParEvaluacion:
    """Representa una predicción y su valor real observado para un producto en una fecha.

    Atributos:
        producto_id: Identificador o SKU del producto.
        fecha_local: Fecha objetivo en formato ISO (YYYY-MM-DD).
        previsto: Cantidad pronosticada (entera no negativa o flotante).
        real: Unidades vendidas reales observadas, o None si la venta es desconocida
              (política de ausencias = desconocido; no se imputa cero).
    """

    producto_id: str
    fecha_local: str
    previsto: float
    real: float | None

    @property
    def es_evaluable(self) -> bool:
        """Un par es evaluable si y solo si la venta real es conocida."""
        return self.real is not None


@dataclass(frozen=True)
class MetricasResultado:
    """Resultado del cómputo de métricas sobre un lote de pares de pronóstico."""

    total_pronosticados: int
    pares_evaluables: int
    productos_excluidos: int
    cobertura_pct: float
    mae: float | None
    wape_pct: float | None
    dentro_mas_menos_20_pct: float | None
    dentro_mas_menos_10_pct: float | None
    suma_errores_absolutos: float
    suma_reales: float

    def as_dict(self) -> dict:
        """Serializa el resultado a diccionario para persistencia o API JSON."""
        return {
            "total_pronosticados": self.total_pronosticados,
            "pares_evaluables": self.pares_evaluables,
            "productos_excluidos": self.productos_excluidos,
            "cobertura_pct": round(self.cobertura_pct, 2),
            "mae": round(self.mae, 4) if self.mae is not None else None,
            "wape_pct": round(self.wape_pct, 2) if self.wape_pct is not None else None,
            "dentro_mas_menos_20_pct": (
                round(self.dentro_mas_menos_20_pct, 2)
                if self.dentro_mas_menos_20_pct is not None
                else None
            ),
            "dentro_mas_menos_10_pct": (
                round(self.dentro_mas_menos_10_pct, 2)
                if self.dentro_mas_menos_10_pct is not None
                else None
            ),
            "suma_errores_absolutos": round(self.suma_errores_absolutos, 4),
            "suma_reales": round(self.suma_reales, 4),
        }


def calcular_mae(pares_evaluables: Sequence[tuple[float, float]]) -> float | None:
    """Calcula el Error Medio Absoluto (MAE) en unidades.

    Fórmula: suma(|real - previsto|) / cantidad de productos evaluables.

    Args:
        pares_evaluables: Lista de tuplas (real, previsto). Solo pares con venta real conocida.

    Returns:
        MAE en unidades físicas, o None si no hay pares evaluables.
    """
    if not pares_evaluables:
        return None
    suma_abs = sum(abs(r - p) for r, p in pares_evaluables)
    return suma_abs / len(pares_evaluables)


def calcular_wape(pares_evaluables: Sequence[tuple[float, float]]) -> float | None:
    """Calcula el WAPE porcentual: 100 * sum(|real - previsto|) / sum(real).

    Reglas contractuales:
      - Si la suma de las ventas reales es 0, el WAPE NO está definido y devuelve None.
      - WAPE es una métrica de error [0, inf) y puede superar el 100%.
      - NUNCA se debe calcular (100 - WAPE) ni denominarse 'precisión'.

    Args:
        pares_evaluables: Lista de tuplas (real, previsto).

    Returns:
        WAPE en porcentaje o None si no está definido (suma_real == 0 o lista vacía).
    """
    if not pares_evaluables:
        return None
    suma_real = sum(r for r, _ in pares_evaluables)
    if suma_real == 0.0:
        return None
    suma_abs = sum(abs(r - p) for r, p in pares_evaluables)
    return 100.0 * (suma_abs / suma_real)


def calcular_dentro_rango(
    pares_evaluables: Sequence[tuple[float, float]],
    umbral: float = 0.20,
) -> float | None:
    """Calcula el porcentaje de pares cuyo error relativo no supera el umbral.

    Fórmula contractual (POLITICA_EVALUACION.md):
      aciertos = cantidad de pares donde: |real - previsto| / max(real, 1.0) <= umbral
      porcentaje = 100 * aciertos / cantidad_de_pares_evaluables

    Nota contractual: cuando la venta real es cero, el denominador es max(0, 1) = 1,
    por lo que no produce división por cero y evalúa la diferencia absoluta contra el umbral.

    Args:
        pares_evaluables: Lista de tuplas (real, previsto).
        umbral: Tolerancia relativa (0.20 para ±20%, 0.10 para ±10%).

    Returns:
        Porcentaje [0, 100] o None si no hay pares evaluables.
    """
    if not pares_evaluables:
        return None
    aciertos = sum(
        1 for r, p in pares_evaluables if (abs(r - p) / max(r, 1.0)) <= umbral
    )
    return 100.0 * (aciertos / len(pares_evaluables))



