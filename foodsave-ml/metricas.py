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
