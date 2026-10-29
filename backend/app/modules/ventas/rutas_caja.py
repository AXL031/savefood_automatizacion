"""API de caja presencial; se registra antes de las rutas históricas dinámicas."""
from datetime import date
from typing import Literal
from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.base_datos import obtener_sesion
from app.core.identidad import identidad_actual, requiere_administrador
from app.core.errores import ErrorAPI
from .esquemas_caja import PrecioCrear, CotizarVenta, RegistrarVenta, AnularVenta
from .modelos_caja import TicketVenta, LineaTicketVenta
from . import caja

router = APIRouter(prefix="/ventas", tags=["ventas-presenciales"])


def confirmar(s):
    try:
        s.commit()
    except IntegrityError:
        s.rollback()
        raise ErrorAPI(409, "OPERACION_EN_CONFLICTO", "Otra operación modificó los datos. Consulta el resultado antes de repetir.") from None


@router.get("/catalogo")
def catalogo(usuario=Depends(identidad_actual), s: Session = Depends(obtener_sesion)):
    return {"datos": caja.catalogo_caja(s)}


@router.put("/precios/{producto_id}")
def precio(producto_id: int, entrada: PrecioCrear, usuario=Depends(requiere_administrador), s: Session = Depends(obtener_sesion)):
    p, _ = caja.guardar_precio(s, producto_id, entrada, usuario)
    confirmar(s)
    return {"datos": {"id": p.id, "producto_id": p.producto_id, "version": p.version, "precio": caja._dinero(p.precio)}}


@router.post("/cotizaciones", status_code=201)
def cotizacion(entrada: CotizarVenta, respuesta: Response, usuario=Depends(identidad_actual), s: Session = Depends(obtener_sesion)):
    c, repetida = caja.cotizar(s, entrada, usuario)
    confirmar(s)
    respuesta.status_code = 200 if repetida else 201
    return {"datos": {"id": c.id, "moneda": c.moneda, "total": caja._dinero(c.total), "lineas": c.lineas,
                      "vence_en": caja._utc(c.vence_en).isoformat(), "canal": "PRESENCIAL"}}


@router.post("/tickets", status_code=201)
def registrar(entrada: RegistrarVenta, respuesta: Response, usuario=Depends(identidad_actual), s: Session = Depends(obtener_sesion)):
    t, repetida = caja.registrar_ticket(s, entrada, usuario)
    confirmar(s)
    respuesta.status_code = 200 if repetida else 201
    return {"datos": caja.detalle_ticket(s, t.id)}


@router.get("/tickets")
def listar(desde: date | None = None, hasta: date | None = None, estado: Literal["CONFIRMADA", "ANULADA"] | None = None,
           canal: Literal['PRESENCIAL','TIENDA'] | None = None,
           producto_id: int | None = Query(None, gt=0), limite: int = Query(25, ge=1, le=100), desplazamiento: int = Query(0, ge=0),
           usuario=Depends(identidad_actual), s: Session = Depends(obtener_sesion)):
    if desde and hasta and desde > hasta:
        raise ErrorAPI(422, "RANGO_INVALIDO", "La fecha inicial supera la final.")
    filtros = []
    if desde: filtros.append(TicketVenta.fecha_local >= desde)
    if hasta: filtros.append(TicketVenta.fecha_local <= hasta)
    if estado: filtros.append(TicketVenta.estado == estado)
    if canal: filtros.append(TicketVenta.canal == canal)
    if producto_id: filtros.append(select(LineaTicketVenta.id).where(LineaTicketVenta.ticket_id == TicketVenta.id, LineaTicketVenta.producto_id == producto_id).exists())
    q = select(TicketVenta).where(*filtros)
    total = s.scalar(select(func.count()).select_from(q.subquery()))
    filas = list(s.scalars(q.order_by(TicketVenta.id.desc()).offset(desplazamiento).limit(limite)))
    suma = s.scalar(select(func.coalesce(func.sum(TicketVenta.total), 0)).where(*filtros, TicketVenta.estado == "CONFIRMADA"))
    unidades = dict(s.execute(select(LineaTicketVenta.ticket_id, func.sum(LineaTicketVenta.cantidad))
        .where(LineaTicketVenta.ticket_id.in_([t.id for t in filas])).group_by(LineaTicketVenta.ticket_id)).all())
    return {"datos": [{**caja.resumen_ticket(t), "unidades": unidades.get(t.id, 0)} for t in filas],
            "metadatos": {"total": total, "limite": limite, "desplazamiento": desplazamiento, "importe_confirmado": caja._dinero(suma)}}


@router.get("/tickets/{ticket_id}")
def detalle(ticket_id: int, usuario=Depends(identidad_actual), s: Session = Depends(obtener_sesion)):
    return {"datos": caja.detalle_ticket(s, ticket_id)}


@router.get("/tickets/por-clave/{clave}")
def por_clave(clave: str, usuario=Depends(identidad_actual), s: Session = Depends(obtener_sesion)):
    id_ = s.scalar(select(TicketVenta.id).where(TicketVenta.usuario_id == usuario.id, TicketVenta.clave == clave))
    if id_ is None:
        raise ErrorAPI(404, "VENTA_NO_ENCONTRADA", "No se ha confirmado una venta con esa clave para tu usuario.")
    return {"datos": caja.detalle_ticket(s, id_)}


@router.post("/tickets/{ticket_id}/anular")
def anular(ticket_id: int, entrada: AnularVenta, usuario=Depends(requiere_administrador), s: Session = Depends(obtener_sesion)):
    caja.anular_ticket(s, ticket_id, entrada, usuario)
    confirmar(s)
    return {"datos": caja.detalle_ticket(s, ticket_id)}
