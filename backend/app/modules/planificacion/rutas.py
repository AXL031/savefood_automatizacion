"""M02: crear propuesta desde corrida y consultar sus snapshots."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.base_datos import obtener_sesion
from app.core.identidad import identidad_actual, requiere_administrador
from app.modules.autenticacion.modelos import Usuario
from app.modules.planificacion.esquemas import SolicitarPlan
from app.modules.planificacion.servicio import calcular_necesidades, detalle_plan, generar_plan, listar_planes

router = APIRouter(prefix="/planes", tags=["planificacion"])


@router.post("/{plan_id}/necesidades")
def completar_necesidades(plan_id: int, _admin: Usuario = Depends(requiere_administrador),
                         sesion: Session = Depends(obtener_sesion)):
    calcular_necesidades(sesion, plan_id)
    sesion.commit()
    return {"datos": detalle_plan(sesion, plan_id)}


@router.post("", status_code=201)
def crear_plan(entrada: SolicitarPlan, _admin: Usuario = Depends(requiere_administrador),
               sesion: Session = Depends(obtener_sesion)):
    plan = generar_plan(sesion, corrida_id=entrada.corrida_id, clave_ejecucion=entrada.clave_ejecucion)
    sesion.commit()
    return {"datos": detalle_plan(sesion, plan.id)}


@router.get("")
def planes(corrida_id: int | None = Query(None, gt=0), _usuario: Usuario = Depends(identidad_actual),
           sesion: Session = Depends(obtener_sesion)):
    return {"datos": listar_planes(sesion, corrida_id)}


@router.get("/{plan_id}")
def plan(plan_id: int, _usuario: Usuario = Depends(identidad_actual), sesion: Session = Depends(obtener_sesion)):
    return {"datos": detalle_plan(sesion, plan_id)}
