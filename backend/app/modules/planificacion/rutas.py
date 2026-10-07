from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.core.base_datos import obtener_sesion
from app.core.identidad import identidad_actual, requiere_administrador
from app.modules.autenticacion.modelos import Usuario
from app.modules.planificacion.servicio import generar_plan, listar_planes, obtener_plan

router = APIRouter(prefix="/planes", tags=["planificacion"])


class SolicitudPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    corrida_id: int = Field(gt=0, strict=True)
    clave_ejecucion: str = Field(min_length=1, max_length=128, pattern=r"^[A-Za-z0-9._:-]+$")


@router.post("", status_code=201)
def crear(entrada: SolicitudPlan, _admin: Usuario = Depends(requiere_administrador), sesion: Session = Depends(obtener_sesion)):
    plan = generar_plan(sesion, entrada.corrida_id, entrada.clave_ejecucion)
    sesion.commit()
    return {"datos": obtener_plan(sesion, plan.id)}


@router.get("")
def listar(corrida_id: int | None = Query(default=None, gt=0), _usuario: Usuario = Depends(identidad_actual), sesion: Session = Depends(obtener_sesion)):
    return {"datos": listar_planes(sesion, corrida_id)}


@router.get("/{plan_id}")
def detalle(plan_id: int, _usuario: Usuario = Depends(identidad_actual), sesion: Session = Depends(obtener_sesion)):
    return {"datos": obtener_plan(sesion, plan_id)}
