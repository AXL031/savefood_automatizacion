"""Ensayo transaccional de la jornada: hace rollback de pronóstico/plan/pedidos."""
import json
import os
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from sqlalchemy import select, func
from sqlalchemy.engine import make_url

if os.getenv('PREPARAR_JORNADA_AUTORIZADA')!='2026-10-28' or make_url(os.environ['DATABASE_URL']).database!='foodsave':
    raise RuntimeError('La verificación exige la jornada autorizada en la aplicación actual.')

from app.principal import app  # noqa
from app.core.base_datos import SessionLocal
from app.modules.automatizaciones.servicio import crear_o_recuperar_ejecucion
from app.modules.planificacion.manejadores import generar_propuesta
from app.modules.compras.modelos import PedidoCompra, LineaPedido
from app.modules.pronosticos.modelos import Pronostico
from app.modules.ventas.modelos_caja import TicketVenta, LineaTicketVenta
from app.modules.ventas.modelos import VentaDiaria
from app.modules.comercio.modelos import ReservaTienda

evidencia=Path('/evidencia');esc=json.loads((evidencia/'escenario.json').read_text())
with SessionLocal() as s:
    antes=s.scalar(select(func.count()).select_from(PedidoCompra))
    datos={'parametros':{'fecha_objetivo_demo':esc['fecha'],'producto_ids':esc['producto_ids'],
        'modelo_id':esc['modelo_id'],'modo_envio_pedidos':'REQUIERE_APROBACION','prueba_repetible':True}}
    e=crear_o_recuperar_ejecucion(s,'GENERAR_PROPUESTA','qa-transaccional-'+esc['fecha'],datos)
    resultado=generar_propuesta(s,SimpleNamespace(id=e.id,datos_entrada=datos))
    pronosticos=list(s.scalars(select(Pronostico).where(Pronostico.corrida_id==resultado['corrida_id'])))
    assert len(pronosticos)==12 and all(p.estado=='DISPONIBLE' for p in pronosticos)
    pedidos=list(s.scalars(select(PedidoCompra).where(PedidoCompra.propuesta_id==resultado['propuesta_compra_id'])))
    assert pedidos,'El escenario debe producir faltantes y pedidos.'
    lineas=list(s.scalars(select(LineaPedido).where(LineaPedido.pedido_id.in_([p.id for p in pedidos]))))
    assert lineas
    assert resultado['pedidos_estado']=='GENERADA',resultado
    assert all(p.estado!='ENVIADO' for p in pedidos)
    from app.modules.compras.servicio import construir_mensaje
    from app.modules.negocios.servicio import nombre_negocio
    mensajes=[construir_mensaje(s,p) for p in pedidos]
    assert all(nombre_negocio(s) in m and 'Insumos:' in m for m in mensajes)
    (evidencia/'mensajes-previstos.txt').write_text('\n\n'.join(mensajes)+'\n')
    fecha_ayer=date.fromisoformat(esc['ayer'])
    venta_diaria=dict(s.execute(select(VentaDiaria.producto_id,VentaDiaria.unidades_vendidas).where(VentaDiaria.fecha_local==fecha_ayer,VentaDiaria.producto_id.in_(esc['producto_ids']))).all())
    agregados=dict(s.execute(select(LineaTicketVenta.producto_id,func.sum(LineaTicketVenta.cantidad)).join(TicketVenta).where(
        TicketVenta.fecha_local==fecha_ayer,TicketVenta.clave.like('prueba-jornada-'+esc['fecha']+'-ticket-ayer-%')).group_by(LineaTicketVenta.producto_id)).all())
    assert venta_diaria==agregados,'Tickets de ayer e histórico sintético deben coincidir.'
    informe={'fecha':esc['fecha'],'pronosticos':len(pronosticos),'unidades_pronosticadas':sum(p.cantidad_pronosticada for p in pronosticos),
        'pedidos_preparables':len(pedidos),'lineas_insumos':len(lineas),'estado_propuesta':resultado['pedidos_estado'],
        'tickets_ayer_coherentes':True,'mensajes_previstos':len(mensajes),'rollback':True,'envios_externos':0}
    s.rollback()
    assert s.scalar(select(func.count()).select_from(PedidoCompra))==antes
    assert s.scalar(select(func.count()).select_from(ReservaTienda).where(ReservaTienda.estado=='ACTIVA'))==0
    (evidencia/'verificacion-flujo.json').write_text(json.dumps(informe,indent=2)+'\n')
    print(json.dumps(informe))
