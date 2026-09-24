from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.base_datos import obtener_sesion
from app.modules.autenticacion.modelos import Usuario
from app.modules.autenticacion.rutas import usuario_actual
from app.modules.negocios.modelos import Negocio

router = APIRouter(prefix="/negocios", tags=["negocios"])


class CambioNegocio(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=160)
    zona_horaria: str | None = Field(default=None, min_length=1, max_length=80)
    moneda: str | None = Field(default=None, min_length=3, max_length=3)


def serializar(negocio: Negocio):
    return {"id": negocio.id, "nombre": negocio.nombre, "zona_horaria": negocio.zona_horaria, "moneda": negocio.moneda}


@router.get("/actual")
def negocio_actual(_usuario: Usuario = Depends(usuario_actual), sesion: Session = Depends(obtener_sesion)):
    negocio = sesion.get(Negocio, 1)
    if not negocio:
        raise HTTPException(status_code=503, detail="Falta aplicar la migración inicial")
    return {"datos": serializar(negocio)}


@router.patch("/actual")
def actualizar_negocio(
    datos: CambioNegocio,
    usuario: Usuario = Depends(usuario_actual),
    sesion: Session = Depends(obtener_sesion),
):
    if usuario.rol != "ADMINISTRADOR":
        raise HTTPException(status_code=403, detail="Se requiere administrador")
    negocio = sesion.get(Negocio, 1)
    if not negocio:
        raise HTTPException(status_code=503, detail="Falta aplicar la migración inicial")
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        if valor is not None:
            setattr(negocio, campo, valor)
    sesion.commit()
    return {"datos": serializar(negocio)}
