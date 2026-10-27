"""Venta interna agregada, con revisión y reserva de evaluación, sin commit."""
from sqlalchemy import select
from .modelos import VentaDiaria, RevisionVenta


def agregar_venta_operativa(s, producto_id, fecha, cantidad, usuario_id):
    from app.modules.pronosticos.evaluacion import solicitar_reevaluaciones_venta
    v = s.scalar(select(VentaDiaria).where(VentaDiaria.producto_id == producto_id, VentaDiaria.fecha_local == fecha).with_for_update())
    if not v:
        v = VentaDiaria(producto_id=producto_id, fecha_local=fecha, unidades_vendidas=0, revision_actual=1)
        s.add(v); s.flush()
    else: v.revision_actual += 1
    v.unidades_vendidas += cantidad
    s.add(RevisionVenta(venta_id=v.id, numero_revision=v.revision_actual, unidades_vendidas=v.unidades_vendidas,
        origen_cambio='VENTA_OPERATIVA', motivo='Venta interna confirmada con salida de inventario', usuario_id=usuario_id))
    s.flush()
    solicitar_reevaluaciones_venta(s, producto_id, fecha)
