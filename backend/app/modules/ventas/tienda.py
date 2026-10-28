"""Registro del canal tienda sobre los mismos tickets y salidas de caja."""
from decimal import Decimal
from sqlalchemy import select, or_
from app.core.errores import ErrorAPI
from app.modules.productos.servicio import catalogo_para_ventas
from app.modules.inventario.ventas import retirar_reserva_confirmada
from app.modules.comercio.catalogo import validar_origen, huella
from app.modules.comercio.reservas import obtener, utc
from .caja import contexto_comercial, _bloquear_clave
from .modelos_caja import CotizacionVenta, TicketVenta, LineaTicketVenta, SalidaLoteVenta


def acuse(t,origen):
    return {'ticket_id':t.id,'numero':f'V-{t.id:08d}','canal':t.canal,'total':f'{t.total:.2f}',
            'moneda':t.moneda,'fecha_local':t.fecha_local.isoformat(),'estado':t.estado,
            'pedido_externo':t.pedido_externo,'origen':origen}


def registrar(s,entrada,integracion_id):
    c=validar_origen(s,entrada.origen)
    cuerpo=entrada.model_dump(mode='json',exclude={'evento_id'})
    cuerpo['pago']['monto']=f'{entrada.pago.monto:.2f}'
    h=huella(cuerpo)
    _bloquear_clave(s,'venta-tienda',integracion_id,str(entrada.pedido_externo))
    # Identidades distintas para evento, pedido y transacción; ninguna se reutiliza.
    previos=list(s.scalars(select(TicketVenta).where(or_(
        (TicketVenta.integracion_id==integracion_id)&(TicketVenta.pedido_externo==str(entrada.pedido_externo)),
        (TicketVenta.integracion_id==integracion_id)&(TicketVenta.clave==str(entrada.evento_id)),
        TicketVenta.pago_externo_id==entrada.pago.transaccion))))
    if previos:
        if len(previos)!=1 or previos[0].integracion_id!=integracion_id or previos[0].huella!=h:
            raise ErrorAPI(409,'VENTA_EXTERNA_EN_CONFLICTO','El evento, pedido o pago corresponde a otra venta.')
        return previos[0],True
    r=obtener(s,entrada.reserva_id,integracion_id,bloquear=True)
    if r.clave!=str(entrada.pedido_externo):
        raise ErrorAPI(409,'RESERVA_OTRO_PEDIDO','La reserva no corresponde a este pedido externo.')
    instante,local,zona,moneda=contexto_comercial(s)
    if r.estado!='ACTIVA' or utc(r.vence_en)<=instante or r.fecha_local!=local.date():
        raise ErrorAPI(409,'RESERVA_VENCIDA','La reserva ya no está vigente. El pago requiere revisión.')
    cot=s.get(CotizacionVenta,r.cotizacion_id)
    if Decimal(cot.total)!=entrada.pago.monto or cot.moneda!=entrada.pago.moneda:
        raise ErrorAPI(409,'IMPORTE_DISTINTO','El pago verificado no coincide con el importe reservado.')
    productos=catalogo_para_ventas(s,[l['producto_id'] for l in cot.lineas],bloquear=True)
    if len(productos)!=len(cot.lineas) or any(not p['activo'] for p in productos):
        raise ErrorAPI(409,'PRODUCTO_NO_DISPONIBLE','Un producto reservado requiere revisión administrativa.')
    t=TicketVenta(cotizacion_id=cot.id,usuario_id=None,nombre_usuario='Tienda · comprador invitado',
        integracion_id=integracion_id,pedido_externo=str(entrada.pedido_externo),pago_externo_id=entrada.pago.transaccion,
        clave=str(entrada.evento_id),huella=h,canal='TIENDA',total=cot.total,moneda=moneda,
        cobro=entrada.pago.model_dump(mode='json'),anulacion=None,vendida_en=instante,fecha_local=local.date(),zona_horaria=zona)
    s.add(t);s.flush()
    r.estado='CONSUMIDA';s.flush()  # Excluir esta reserva, manteniendo protegidas las demás.
    salidas=retirar_reserva_confirmada(s,[a for l in cot.lineas for a in l['asignaciones']],ticket_id=t.id,efectivo=local)
    for l in cot.lineas:
        linea=LineaTicketVenta(ticket_id=t.id,producto_id=l['producto_id'],precio_id=l['precio_id'],nombre=l['nombre'],
            codigo=l['codigo'],cantidad=l['cantidad'],precio=l['precio_unitario_base'],subtotal=l['subtotal'],segmentos=l['segmentos'])
        s.add(linea);s.flush()
        s.add_all(SalidaLoteVenta(linea_id=linea.id,**{k:a[k] for k in ('lote_id','cantidad','movimiento_id')}) for a in salidas if a['producto_id']==l['producto_id'])
    s.flush();return t,False
