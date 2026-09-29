"""Evaluador de pronósticos diarios e históricos según POLITICA_EVALUACION.md.

Implementa la lógica para estructurar los resultados de evaluación por fecha:
  - Total previsto y total real sumados exclusivamente sobre los mismos productos evaluables.
  - Conteo de productos excluidos debido a venta real desconocida.
  - Desglose individual de cada producto (previsto, real, diferencia absoluta y tolerancia).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

from metricas import ParEvaluacion, MetricasResultado, evaluar_pares


@dataclass
class EvaluacionDia:
    """Evaluación de un día específico para visualización y dashboard."""

    fecha_local: str
    total_previsto_evaluable: float
    total_real_conocido: float
    productos_evaluables: int
    productos_excluidos: int
    metricas: MetricasResultado
    desglose_productos: list[dict] = field(default_factory=list)

    def as_dict(self) -> dict:
        """Serializa a diccionario para API REST y componentes del panel."""
        return {
            "fecha_local": self.fecha_local,
            "total_previsto_evaluable": round(self.total_previsto_evaluable, 2),
            "total_real_conocido": round(self.total_real_conocido, 2),
            "productos_evaluables": self.productos_evaluables,
            "productos_excluidos": self.productos_excluidos,
            "metricas": self.metricas.as_dict(),
            "desglose_productos": self.desglose_productos,
        }


def evaluar_dia(
    fecha_local: str,
    pares_dia: Sequence[ParEvaluacion],
) -> EvaluacionDia:
    """Calcula la evaluación de un día específico.

    Regla contractual estricta (POLITICA_EVALUACION.md):
      "total previsto frente a total real conocido, sumados ambos sobre los mismos
      productos evaluables de ese día; mostrar también cuántos productos quedaron fuera.
      Al seleccionar un día: barras por producto y diferencia absoluta en unidades."

    Args:
        fecha_local: Fecha evaluada (YYYY-MM-DD).
        pares_dia: Lista de pares (predicción, real) para los productos del día.

    Returns:
        EvaluacionDia con métricas y desglose por producto.
    """
    metricas = evaluar_pares(pares_dia)

    desglose = []
    tot_prev_eval = 0.0
    tot_real_eval = 0.0

    for p in pares_dia:
        if p.es_evaluable and p.real is not None:
            tot_prev_eval += p.previsto
            tot_real_eval += p.real
            error_abs = abs(p.real - p.previsto)
            desglose.append({
                "producto_id": p.producto_id,
                "previsto": round(p.previsto, 2),
                "real": round(p.real, 2),
                "diferencia_absoluta": round(error_abs, 2),
                "dentro_mas_menos_20": (error_abs / max(p.real, 1.0)) <= 0.20,
            })
        else:
            desglose.append({
                "producto_id": p.producto_id,
                "previsto": round(p.previsto, 2),
                "real": None,
                "diferencia_absoluta": None,
                "dentro_mas_menos_20": None,
                "motivo_exclusion": "VENTA_REAL_DESCONOCIDA",
            })

    return EvaluacionDia(
        fecha_local=fecha_local,
        total_previsto_evaluable=tot_prev_eval,
        total_real_conocido=tot_real_eval,
        productos_evaluables=metricas.pares_evaluables,
        productos_excluidos=metricas.productos_excluidos,
        metricas=metricas,
        desglose_productos=desglose,
    )
