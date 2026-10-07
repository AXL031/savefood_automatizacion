"""API de ventas diarias y de sus correcciones auditables."""

from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.base_datos import obtener_sesion
from app.core.errores import ErrorAPI
from app.core.identidad import identidad_actual, requiere_administrador
from app.modules.autenticacion.modelos import Usuario
from app.modules.productos.modelos import Producto, SkuProducto
from app.modules.ventas.esquemas import CorregirVenta
from app.modules.ventas.modelos import RevisionVenta, VentaDiaria
from app.modules.ventas.servicio import corregir_venta

router = APIRouter(prefix="/ventas", tags=["ventas"])

LIMITE_MAXIMO = 500


@router.get("")
def listar_ventas(
    producto_id: int | None = Query(None),
    desde: date | None = Query(None),
    hasta: date | None = Query(None, description="Inclusive."),
    limite: int = Query(100, ge=1, le=LIMITE_MAXIMO),
    desplazamiento: int = Query(0, ge=0),
    _usuario: Usuario = Depends(identidad_actual),
    sesion: Session = Depends(obtener_sesion),
):
    """Lista ventas diarias conocidas.

    Una fecha sin fila no aparece y no se rellena con cero: sigue siendo
    desconocida. Un cero explícito sí se devuelve.
    """
    if desde and hasta and desde > hasta:
        raise ErrorAPI(422, "RANGO_INVALIDO", "La fecha inicial no puede ser posterior a la final.")

    consulta = (
        select(
            VentaDiaria.id,
            VentaDiaria.producto_id,
            Producto.nombre,
            SkuProducto.sku_externo,
            VentaDiaria.fecha_local,
            VentaDiaria.unidades_vendidas,
            VentaDiaria.revision_actual,
            VentaDiaria.actualizado_en,
        )
        .join(Producto, Producto.id == VentaDiaria.producto_id)
        .join(SkuProducto, SkuProducto.producto_id == VentaDiaria.producto_id, isouter=True)
        .order_by(VentaDiaria.fecha_local.desc(), VentaDiaria.producto_id, VentaDiaria.id)
    )
    if producto_id is not None:
        consulta = consulta.where(VentaDiaria.producto_id == producto_id)
    if desde is not None:
        consulta = consulta.where(VentaDiaria.fecha_local >= desde)
    if hasta is not None:
        consulta = consulta.where(VentaDiaria.fecha_local <= hasta)

    total = sesion.scalar(select(func.count()).select_from(consulta.order_by(None).subquery()))
    filas = sesion.execute(consulta.offset(desplazamiento).limit(limite)).all()
    return {
        "datos": [
            {
                "id": fila.id,
                "producto_id": fila.producto_id,
                "producto": fila.nombre,
                "sku_externo": fila.sku_externo,
                "fecha_local": fila.fecha_local.isoformat(),
                "unidades_vendidas": fila.unidades_vendidas,
                "revision_actual": fila.revision_actual,
                "actualizado_en": fila.actualizado_en.isoformat() if fila.actualizado_en else None,
            }
            for fila in filas
        ],
        "metadatos": {"limite": limite, "desplazamiento": desplazamiento, "total": total, "total_devuelto": len(filas)},
    }


@router.get("/{venta_id}/revisiones")
def listar_revisiones(
    venta_id: int,
    _usuario: Usuario = Depends(identidad_actual),
    sesion: Session = Depends(obtener_sesion),
):
    """Historia completa de una venta. Una corrección no borra el valor anterior."""
    if sesion.scalar(select(VentaDiaria.id).where(VentaDiaria.id == venta_id)) is None:
        raise ErrorAPI(404, "VENTA_NO_ENCONTRADA", "La venta no existe.")
    filas = sesion.scalars(
        select(RevisionVenta)
        .where(RevisionVenta.venta_id == venta_id)
        .order_by(RevisionVenta.numero_revision)
    ).all()
    return {
        "datos": [
            {
                "id": fila.id,
                "numero_revision": fila.numero_revision,
                "unidades_vendidas": fila.unidades_vendidas,
                "origen_cambio": fila.origen_cambio,
                "motivo": fila.motivo,
                "usuario_id": fila.usuario_id,
                "importacion_id": fila.importacion_id,
                "creado_en": fila.creado_en.isoformat() if fila.creado_en else None,
            }
            for fila in filas
        ]
    }


@router.patch("/{venta_id}")
def corregir(
    venta_id: int,
    entrada: CorregirVenta,
    admin: Usuario = Depends(requiere_administrador),
    sesion: Session = Depends(obtener_sesion),
):
    """Corrige una venta creando una revisión nueva.

    Kevin debe reevaluar las corridas que usaron la revisión anterior: el valor
    viejo se conserva para que la evaluación histórica siga siendo reproducible.
    """
    revision_id = corregir_venta(sesion, venta_id, entrada.unidades_vendidas, entrada.motivo, admin.id)
    sesion.commit()
    venta = sesion.get(VentaDiaria, venta_id)
    return {
        "datos": {
            "venta_id": venta_id,
            "revision_venta_id": revision_id,
            "revision_actual": venta.revision_actual,
            "unidades_vendidas": venta.unidades_vendidas,
        }
    }
