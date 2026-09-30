"""API del catálogo local."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.base_datos import obtener_sesion
from app.core.identidad import identidad_actual
from app.modules.autenticacion.modelos import Usuario
from app.modules.productos.modelos import Producto, SkuProducto

router = APIRouter(prefix="/productos", tags=["productos"])

LIMITE = 500


@router.get("")
def listar_productos(
    solo_demo: bool = Query(False, description="Solo los productos marcados para la demostración."),
    _usuario: Usuario = Depends(identidad_actual),
    sesion: Session = Depends(obtener_sesion),
):
    consulta = (
        select(
            Producto.id,
            Producto.codigo,
            Producto.nombre,
            Producto.demostrar,
            Producto.activo,
            SkuProducto.origen,
            SkuProducto.sku_externo,
        )
        .join(SkuProducto, SkuProducto.producto_id == Producto.id, isouter=True)
        .order_by(Producto.nombre)
        .limit(LIMITE)
    )
    if solo_demo:
        consulta = consulta.where(Producto.demostrar.is_(True))
    filas = sesion.execute(consulta).all()
    return {
        "datos": [
            {
                "id": fila.id,
                "codigo": fila.codigo,
                "nombre": fila.nombre,
                "demostrar": fila.demostrar,
                "activo": fila.activo,
                "origen": fila.origen,
                "sku_externo": fila.sku_externo,
            }
            for fila in filas
        ],
        "metadatos": {"limite": LIMITE, "total_devuelto": len(filas)},
    }
