"""Interfaz pública de stock para caja; transacción a cargo del módulo consumidor."""
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import select
from app.core.errores import ErrorAPI
from .modelos import LoteProducto, MovimientoInventario
from .servicio import _aplicar


def _vendible(lote, fecha):
    return ((lote.fecha_ingreso is None or lote.fecha_ingreso <= fecha)
            and lote.fecha_limite_venta is not None and lote.fecha_limite_venta >= fecha
            and (lote.fecha_caducidad is None or lote.fecha_caducidad >= fecha))


def _lotes(sesion, ids, bloquear=False):
    q = select(LoteProducto).where(LoteProducto.producto_id.in_(sorted(ids))).order_by(LoteProducto.id)
    if bloquear:
        q = q.with_for_update().execution_options(populate_existing=True)
    return list(sesion.scalars(q))


def lotes_para_comercio(sesion, ids, *, bloquear=False):
    """Lotes del dominio para cotización/reserva en la transacción del consumidor."""
    return _lotes(sesion, ids, bloquear=bloquear)


def lote_vendible(lote, fecha):
    return _vendible(lote, fecha)


def disponibilidad_para_venta(sesion, ids: list[int], fecha: date) -> dict:
    lotes = _lotes(sesion, ids)
    from .reservas import cantidades_reservadas
    reservas = cantidades_reservadas(sesion, [l.id for l in lotes])
    return {id_: {"stock_conocido": any(l.producto_id == id_ for l in lotes),
                  "disponible": sum(max(0,l.saldo_disponible-reservas.get(l.id,0)) for l in lotes if l.producto_id == id_ and _vendible(l, fecha)),
                  "reservado": sum(reservas.get(l.id,0) for l in lotes if l.producto_id == id_ and _vendible(l, fecha)),
                  "aviso_caducidad": any(l.producto_id == id_ and _vendible(l, fecha) and l.fecha_caducidad is None for l in lotes)}
            for id_ in ids}


def retirar_productos_por_venta(sesion, cantidades: dict[int, int], *, ticket_id: int, usuario_id: int, efectivo: datetime):
    lotes = _lotes(sesion, cantidades, bloquear=True)
    from .reservas import cantidades_reservadas
    reservas = cantidades_reservadas(sesion, [l.id for l in lotes])
    asignaciones = []
    # Primero validar TODO el carrito, antes de tocar el primer saldo.
    for id_, cantidad in sorted(cantidades.items()):
        candidatos = [l for l in lotes if l.producto_id == id_]
        if not candidatos:
            raise ErrorAPI(409, "STOCK_DESCONOCIDO", f"El producto #{id_} no tiene stock observado.")
        elegibles = sorted([l for l in candidatos if _vendible(l, efectivo.date())],
                           key=lambda l: (l.fecha_limite_venta, l.fecha_caducidad or date.max, l.id))
        if sum(max(0,l.saldo_disponible-reservas.get(l.id,0)) for l in elegibles) < cantidad:
            raise ErrorAPI(409, "STOCK_INSUFICIENTE", f"No hay {cantidad} unidades vendibles del producto #{id_}.")
        for lote in elegibles:
            tomar = min(cantidad, max(0,lote.saldo_disponible-reservas.get(lote.id,0)))
            if tomar:
                asignaciones.append((id_, lote, tomar))
                cantidad -= tomar
            if not cantidad:
                break
    resultado = []
    for id_, lote, cantidad in asignaciones:
        m = _aplicar(sesion, tipo="producto", lote=lote, delta=Decimal(-cantidad), tipo_movimiento="VENTA",
                     clave=f"venta-{ticket_id}-lote-{lote.id}", motivo=f"Venta presencial #{ticket_id}",
                     efectivo_en_demo=efectivo, usuario_id=usuario_id)
        resultado.append({"producto_id": id_, "lote_id": lote.id, "cantidad": cantidad, "movimiento_id": m.movimiento_id})
    return resultado


def retirar_reserva_confirmada(sesion, asignaciones, *, ticket_id, efectivo):
    """El llamador bloqueó productos/reserva y marcó su consumo en esta transacción."""
    ids = sorted({a['lote_id'] for a in asignaciones})
    lotes = {l.id:l for l in sesion.scalars(select(LoteProducto).where(LoteProducto.id.in_(ids))
             .order_by(LoteProducto.id).with_for_update().execution_options(populate_existing=True))}
    if len(lotes) != len(ids) or any(not _vendible(lotes[a['lote_id']],efectivo.date()) for a in asignaciones):
        raise ErrorAPI(409,'RESERVA_NO_VENDIBLE','Un lote reservado dejó de estar vigente.')
    resultado=[]
    for a in sorted(asignaciones,key=lambda a:a['lote_id']):
        lote=lotes[a['lote_id']]
        m=_aplicar(sesion,tipo='producto',lote=lote,delta=Decimal(-a['cantidad']),tipo_movimiento='VENTA',
                   clave=f'venta-{ticket_id}-lote-{lote.id}',motivo=f'Venta de tienda #{ticket_id}',
                   efectivo_en_demo=efectivo,usuario_id=None)
        resultado.append({'producto_id':lote.producto_id,'lote_id':lote.id,'cantidad':a['cantidad'],'movimiento_id':m.movimiento_id})
    return resultado


def reintegrar_venta(sesion, movimiento_ids: list[int], *, ticket_id: int, usuario_id: int, efectivo: datetime):
    originales = list(sesion.scalars(select(MovimientoInventario).where(MovimientoInventario.id.in_(movimiento_ids))))
    if len(originales) != len(movimiento_ids) or any(m.tipo != "VENTA" or not m.clave_operacion.startswith(f"venta-{ticket_id}-lote-") for m in originales):
        raise ErrorAPI(409, "SALIDA_INVALIDA", "Las salidas no pertenecen a esta venta.")
    ids = sorted({m.lote_producto_id for m in originales})
    lotes = {l.id: l for l in sesion.scalars(select(LoteProducto).where(LoteProducto.id.in_(ids)).order_by(LoteProducto.id)
              .with_for_update().execution_options(populate_existing=True))}
    resultado = {}
    for m in sorted(originales, key=lambda m: m.lote_producto_id):
        r = _aplicar(sesion, tipo="producto", lote=lotes[m.lote_producto_id], delta=-m.delta,
                     tipo_movimiento="ANULA_VENTA", clave=f"anular-venta-{ticket_id}-mov-{m.id}",
                     motivo=f"Anulación de venta presencial #{ticket_id}", efectivo_en_demo=efectivo, usuario_id=usuario_id)
        resultado[m.id] = r.movimiento_id
    return resultado
