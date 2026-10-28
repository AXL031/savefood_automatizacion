"""Disponibilidad apartada por comercio; saldo físico solo cambia al vender."""
from sqlalchemy import select, func


def cantidades_reservadas(sesion, lote_ids):
    if not lote_ids:
        return {}
    from app.modules.comercio.modelos import AsignacionReserva, ReservaTienda
    from app.modules.ventas.caja import ahora
    q = select(AsignacionReserva.lote_id, func.sum(AsignacionReserva.cantidad)).join(
        ReservaTienda, ReservaTienda.id == AsignacionReserva.reserva_id).where(
        AsignacionReserva.lote_id.in_(list(lote_ids)), ReservaTienda.estado == 'ACTIVA',
        ReservaTienda.vence_en > ahora()).group_by(AsignacionReserva.lote_id)
    return dict(sesion.execute(q).all())
