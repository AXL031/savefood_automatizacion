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


@dataclass
class EvaluacionTramoCompleto:
    """Evaluación consolidada del tramo histórico completo según POLITICA_EVALUACION.md."""

    version_modelo: str
    fecha_inicio: str
    fecha_fin: str
    fechas_evaluadas: int
    total_pares_evaluables: int
    metricas_globales: MetricasResultado
    evaluaciones_diarias: list[EvaluacionDia] = field(default_factory=list)
    estado: str = "demostracion_historica"

    def as_dict(self) -> dict:
        """Serializa el reporte completo del tramo para el dashboard K04."""
        return {
            "estado": self.estado,
            "version_modelo": self.version_modelo,
            "fecha_inicio": self.fecha_inicio,
            "fecha_fin": self.fecha_fin,
            "fechas_evaluadas": self.fechas_evaluadas,
            "total_pares_evaluables": self.total_pares_evaluables,
            "metricas_globales": self.metricas_globales.as_dict(),
            "serie_diaria": [d.as_dict() for d in self.evaluaciones_diarias],
        }


def consolidar_evaluacion_tramo(
    version_modelo: str,
    fecha_inicio: str,
    fecha_fin: str,
    pares_todos: Sequence[ParEvaluacion],
) -> EvaluacionTramoCompleto:
    """Consolida la evaluación del tramo completo sin promediar porcentajes.

    Regla contractual estricta (POLITICA_EVALUACION.md):
      "Para el tramo completo, calcular MAE con todos los pares producto-día evaluables
      y WAPE con las sumas de error y venta real de esos pares; no promediar los
      porcentajes diarios. Mostrar cuántos pares y fechas fueron evaluables."

    Args:
        version_modelo: Identificador de la versión del artefacto ML.
        fecha_inicio: Fecha inicial del tramo evaluado (YYYY-MM-DD).
        fecha_fin: Fecha final del tramo evaluado (YYYY-MM-DD).
        pares_todos: Todos los pares producto-día del tramo completo.

    Returns:
        EvaluacionTramoCompleto con métricas globales y desglose diario.
    """
    # 1. Agrupar por fecha para la serie temporal del gráfico
    pares_por_fecha: dict[str, list[ParEvaluacion]] = {}
    for p in pares_todos:
        pares_por_fecha.setdefault(p.fecha_local, []).append(p)

    fechas_ordenadas = sorted(pares_por_fecha.keys())
    evaluaciones_diarias = [
        evaluar_dia(f, pares_por_fecha[f]) for f in fechas_ordenadas
    ]

    # 2. Métricas globales evaluando directamente la lista completa de todos los pares
    # (garantiza sumas totales sin promediar porcentajes diarios)
    metricas_globales = evaluar_pares(pares_todos)

    return EvaluacionTramoCompleto(
        version_modelo=version_modelo,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        fechas_evaluadas=len(fechas_ordenadas),
        total_pares_evaluables=metricas_globales.pares_evaluables,
        metricas_globales=metricas_globales,
        evaluaciones_diarias=evaluaciones_diarias,
    )

