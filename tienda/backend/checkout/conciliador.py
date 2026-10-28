"""Recupera entregas confirmadas sin depender de que el cliente mantenga la página abierta."""
import time
from sqlalchemy import select
from sqlalchemy.orm import Session
from .base_datos import engine, preparar
from .modelos import PedidoComercial
from .integracion import ahora, sincronizar_pago


def ciclo():
    with Session(engine) as s:
        ids=list(s.scalars(select(PedidoComercial.pago_id).where(PedidoComercial.estado.in_(
            ['PENDIENTE_VENTA','LIBERACION_PENDIENTE']),PedidoComercial.proximo_intento<=ahora()).limit(25)))
    for id_ in ids:
        with Session(engine) as s:sincronizar_pago(s,id_)


if __name__=='__main__':
    preparar()
    while True:
        try:ciclo()
        except Exception:print('Conciliación pendiente; se conserva la entrega para el próximo ciclo.',flush=True)
        time.sleep(10)
