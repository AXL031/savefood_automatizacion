"""Adaptador M02 al motor: inferencia, propuesta y evaluación, sin commit."""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

from app.core.errores import ErrorAPI
from app.modules.planificacion.servicio import generar_plan
from app.modules.compras.servicio import generar_pedidos
from app.modules.pronosticos.evaluacion import solicitar_evaluacion_corrida
from app.modules.pronosticos.servicio import generar_corrida
from app.workers.retry.politica import ErrorDatos

if TYPE_CHECKING:
    from app.workers.tasks.manejadores import ContextoEjecucion


def generar_propuesta(sesion: Session, contexto: ContextoEjecucion) -> dict:
    entrada = contexto.datos_entrada
    parametros = entrada.get("parametros")
    if not isinstance(parametros, dict):
        raise ErrorDatos("Faltan los parámetros de la propuesta programada.")
    try:
        objetivo = date.fromisoformat(parametros["fecha_objetivo_demo"])
        productos = parametros["producto_ids"]
        if (not isinstance(productos, list) or not 1 <= len(productos) <= 5 or
                any(type(p) is not int or p <= 0 for p in productos) or len(set(productos)) != len(productos)):
            raise ValueError("Se necesitan de uno a cinco productos únicos.")
        corrida = generar_corrida(sesion, ejecucion_id=contexto.id,
                                  clave_ejecucion=f"propuesta-{contexto.id}", fecha_objetivo=objetivo,
                                  producto_ids=productos)
        plan = generar_plan(sesion, corrida_id=corrida.id, clave_ejecucion=f"plan-propuesta-{contexto.id}")
        try:
            propuesta = generar_pedidos(sesion, plan.id, modo_envio=parametros.get("modo_envio_pedidos"))
            compra = {"propuesta_compra_id": propuesta.id, "pedidos_estado": propuesta.estado}
        except ErrorAPI as exc:
            if exc.codigo != "RECOMPRA_FECHA":
                raise
            compra = {"propuesta_compra_id": None, "pedidos_estado": "RECOMPRA_FECHA", "pedidos_motivo": str(exc.detail)}
        evaluacion = solicitar_evaluacion_corrida(sesion, corrida.id)
    except ErrorAPI as exc:
        raise ErrorDatos(str(exc.detail)) from exc
    except (KeyError, ValueError, TypeError) as exc:
        raise ErrorDatos(f"Entrada de propuesta inválida: {exc}") from exc
    return {"corrida_id": corrida.id, "plan_id": plan.id, "evaluacion_ejecucion_id": evaluacion.id,
            "alcance": "PLAN_PEDIDOS_L02", "necesidades_estado": plan.necesidades_estado, **compra}
