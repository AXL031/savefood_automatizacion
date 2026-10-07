"""A03 → K02 → M02/M03 → K03. Compras pendientes; sin efectos externos."""

from datetime import date

from app.core.errores import ErrorAPI
from app.modules.planificacion.servicio import generar_plan
from app.modules.pronosticos.evaluacion import solicitar_evaluacion_corrida
from app.modules.pronosticos.servicio import generar_corrida
from app.workers.retry.politica import ErrorDatos


def generar_propuesta(sesion, contexto):
    entrada = contexto.datos_entrada.get("parametros", {})
    try:
        fecha = date.fromisoformat(entrada["fecha_objetivo_demo"])
        ids = entrada["producto_ids"]
        if not isinstance(ids, list) or not 1 <= len(ids) <= 5 or any(type(id_) is not int or id_ <= 0 for id_ in ids):
            raise ValueError("Selecciona entre 1 y 5 productos válidos.")
        corrida = generar_corrida(sesion, ejecucion_id=contexto.id, clave_ejecucion=f"propuesta-{contexto.id}",
                                  fecha_objetivo=fecha, producto_ids=ids)
        plan = generar_plan(sesion, corrida.id, f"plan-propuesta-{contexto.id}")
        evaluacion = solicitar_evaluacion_corrida(sesion, corrida.id)
    except ErrorAPI as exc:
        raise ErrorDatos(str(exc.detail)) from exc
    except (KeyError, TypeError, ValueError) as exc:
        raise ErrorDatos(f"Datos de propuesta inválidos: {exc}") from exc
    return {"corrida_id": corrida.id, "plan_id": plan.id, "evaluacion_ejecucion_id": evaluacion.id,
            "pedidos_estado": "PENDIENTE_IMPLEMENTACION"}
