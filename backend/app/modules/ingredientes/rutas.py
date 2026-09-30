"""API del catálogo de ingredientes (M01)."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.base_datos import obtener_sesion
from app.core.identidad import identidad_actual, requiere_administrador
from app.modules.autenticacion.modelos import Usuario
from app.modules.ingredientes.esquemas import CambiarIngrediente, CrearIngrediente
from app.modules.ingredientes.modelos import UNIDADES_BASE
from app.modules.ingredientes.servicio import (
    IngredienteLeido,
    UsoIngrediente,
    actualizar_ingrediente,
    crear_ingrediente,
    listar_ingredientes,
    uso_ingrediente,
)

router = APIRouter(prefix="/ingredientes", tags=["ingredientes"])


def _respuesta(ingrediente: IngredienteLeido, uso: UsoIngrediente) -> dict:
    return {
        "id": ingrediente.id,
        "codigo": ingrediente.codigo,
        "nombre": ingrediente.nombre,
        "unidad_base": ingrediente.unidad_base,
        "activo": ingrediente.activo,
        "en_uso": uso.en_uso,
        "lineas_receta": uso.lineas_receta,
        "lotes": uso.lotes,
        # La UI bloquea el selector de unidad con este dato; el servidor igual lo valida.
        "unidad_editable": not uso.en_uso,
    }


@router.get("")
def listar(
    solo_activos: bool = Query(False),
    _usuario: Usuario = Depends(identidad_actual),
    sesion: Session = Depends(obtener_sesion),
):
    filas = listar_ingredientes(sesion, solo_activos=solo_activos)
    return {
        "datos": [_respuesta(ingrediente, uso) for ingrediente, uso in filas],
        "metadatos": {"unidades_permitidas": list(UNIDADES_BASE), "total": len(filas)},
    }


@router.post("", status_code=201)
def crear(
    cuerpo: CrearIngrediente,
    _admin: Usuario = Depends(requiere_administrador),
    sesion: Session = Depends(obtener_sesion),
):
    ingrediente = crear_ingrediente(sesion, cuerpo.codigo, cuerpo.nombre, cuerpo.unidad_base)
    sesion.commit()
    return {"datos": _respuesta(ingrediente, uso_ingrediente(sesion, ingrediente.id))}


@router.patch("/{ingrediente_id}")
def cambiar(
    ingrediente_id: int,
    cuerpo: CambiarIngrediente,
    _admin: Usuario = Depends(requiere_administrador),
    sesion: Session = Depends(obtener_sesion),
):
    ingrediente = actualizar_ingrediente(
        sesion,
        ingrediente_id,
        nombre=cuerpo.nombre,
        unidad_base=cuerpo.unidad_base,
        activo=cuerpo.activo,
    )
    sesion.commit()
    return {"datos": _respuesta(ingrediente, uso_ingrediente(sesion, ingrediente.id))}
