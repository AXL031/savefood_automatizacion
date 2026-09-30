"""API de recetas versionadas (M01)."""

from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.base_datos import obtener_sesion
from app.core.identidad import identidad_actual, requiere_administrador
from app.modules.autenticacion.modelos import Usuario
from app.modules.productos.modelos import Producto
from app.modules.recetas.esquemas import NuevaVersion
from app.modules.recetas.servicio import (
    LineaNueva,
    RecetaLeida,
    crear_version,
    historial_de_producto,
    obtener_receta,
    recetas_activas,
)

router = APIRouter(prefix="/recetas", tags=["recetas"])


def _cantidad(valor) -> str:
    return f"{valor:.3f}"


def _receta(receta: RecetaLeida) -> dict:
    return {
        "receta_id": receta.receta_id,
        "producto_id": receta.producto_id,
        "version": receta.version,
        "activo": receta.activo,
        "motivo": receta.motivo,
        "creado_en": receta.creado_en.isoformat() if receta.creado_en else None,
        "lineas": [
            {
                "ingrediente_id": linea.ingrediente_id,
                "codigo": linea.codigo,
                "nombre": linea.nombre,
                "unidad_base": linea.unidad_base,
                "cantidad_por_unidad": _cantidad(linea.cantidad_por_unidad),
            }
            for linea in receta.lineas
        ],
    }


@router.get("")
def listar(
    solo_demo: bool = Query(False, description="Solo productos marcados para la demostración."),
    _usuario: Usuario = Depends(identidad_actual),
    sesion: Session = Depends(obtener_sesion),
):
    """Productos con su receta activa; `receta` es null si todavía no tiene."""
    consulta = select(Producto).where(Producto.activo.is_(True)).order_by(Producto.nombre)
    if solo_demo:
        consulta = consulta.where(Producto.demostrar.is_(True))
    productos = list(sesion.scalars(consulta))
    activas = recetas_activas(sesion, [producto.id for producto in productos])
    datos = [
        {
            "producto_id": producto.id,
            "producto_codigo": producto.codigo,
            "producto_nombre": producto.nombre,
            "demostrar": producto.demostrar,
            "receta": _receta(activas[producto.id]) if producto.id in activas else None,
        }
        for producto in productos
    ]
    return {"datos": datos, "metadatos": {"total": len(datos), "con_receta": len(activas)}}


@router.get("/productos/{producto_id}/versiones")
def versiones(
    producto_id: int,
    _usuario: Usuario = Depends(identidad_actual),
    sesion: Session = Depends(obtener_sesion),
):
    return {"datos": [_receta(receta) for receta in historial_de_producto(sesion, producto_id)]}


@router.post("/productos/{producto_id}/versiones", status_code=201)
def nueva_version(
    producto_id: int,
    cuerpo: NuevaVersion,
    response: Response,
    admin: Usuario = Depends(requiere_administrador),
    sesion: Session = Depends(obtener_sesion),
):
    resultado = crear_version(
        sesion,
        producto_id,
        [LineaNueva(ingrediente_id=l.ingrediente_id, cantidad_por_unidad=l.cantidad_por_unidad) for l in cuerpo.lineas],
        cuerpo.motivo,
        usuario_id=admin.id,
    )
    sesion.commit()
    if not resultado.creada:
        # Misma composición que la versión activa: no se crea otra.
        response.status_code = 200
    return {"datos": {**_receta(resultado.receta), "creada": resultado.creada}}


@router.get("/{receta_id}")
def detalle(
    receta_id: int,
    _usuario: Usuario = Depends(identidad_actual),
    sesion: Session = Depends(obtener_sesion),
):
    return {"datos": _receta(obtener_receta(sesion, receta_id))}
