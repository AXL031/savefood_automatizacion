"""Reserva y lectura propia. Sin red ni commits; lotes bloqueados en orden."""
import os
from datetime import datetime, timedelta, time, timezone
from uuid import uuid4
from zoneinfo import ZoneInfo
from sqlalchemy import select
from app.core.errores import ErrorAPI
from app.modules.ventas.caja import contexto_comercial, bloquear_clave_comercial
from app.modules.ventas.modelos_caja import CotizacionVenta
from .modelos import ReservaTienda, AsignacionReserva
from .catalogo import cotizar, huella


def utc(t):
    return t.replace(tzinfo=timezone.utc) if t.tzinfo is None else t.astimezone(timezone.utc)


def obtener(s,id_,integracion_id,*,bloquear=False):
    q=select(ReservaTienda).where(ReservaTienda.id==str(id_),ReservaTienda.integracion_id==integracion_id)
    if bloquear:q=q.with_for_update().execution_options(populate_existing=True)
    r=s.scalar(q)
    if not r:raise ErrorAPI(404,'RESERVA_NO_ENCONTRADA','No se encontró la reserva de esta integración.')
    return r


def vista(s,r):
    instante=contexto_comercial(s)[0]
    cot=s.get(CotizacionVenta,r.cotizacion_id)
    return {'id':r.id,'estado':'EXPIRADA' if r.estado=='ACTIVA' and utc(r.vence_en)<=instante else r.estado,
            'vence_en':utc(r.vence_en).isoformat(),'cotizacion':{'lineas':[{k:v for k,v in l.items() if k!='asignaciones'} for l in cot.lineas],
             'total':f'{cot.total:.2f}','moneda':cot.moneda},'fecha_local':r.fecha_local.isoformat()}


def crear(s,entrada,integracion_id):
    datos=entrada.model_dump(mode='json');h=huella(datos)
    bloquear_clave_comercial(s,'reserva',integracion_id,entrada.clave_idempotencia)
    r=s.scalar(select(ReservaTienda).where(ReservaTienda.integracion_id==integracion_id,ReservaTienda.clave==entrada.clave_idempotencia))
    if r:
        if r.huella!=h:raise ErrorAPI(409,'CLAVE_REUTILIZADA','La reserva ya corresponde a otro contenido.')
        return r,True
    publico,lineas=cotizar(s,entrada,bloquear=True)
    if any(not l['disponible'] for l in lineas):raise ErrorAPI(409,'STOCK_INSUFICIENTE','Ya no hay stock suficiente para reservar la canasta.')
    if publico['huella']!=entrada.cotizacion_hash:raise ErrorAPI(409,'COTIZACION_CAMBIO','Cambió la cotización. Revisa los importes antes de pagar.')
    instante,local,zona,moneda=contexto_comercial(s)
    minutos=max(5,min(60,int(os.getenv('RESERVA_TIENDA_MINUTOS','20'))))
    medianoche=datetime.combine(local.date()+timedelta(days=1),time.min,ZoneInfo(zona)).astimezone(timezone.utc)
    vence=min(instante+timedelta(minutes=minutos),medianoche)
    cot=CotizacionVenta(id=str(uuid4()),usuario_id=None,canal='TIENDA',integracion_id=integracion_id,
        clave=entrada.clave_idempotencia,huella=h,lineas=lineas,total=publico['total'],moneda=moneda,
        creado_en=instante,vence_en=vence)
    s.add(cot);s.flush()
    r=ReservaTienda(id=str(uuid4()),cotizacion_id=cot.id,integracion_id=integracion_id,clave=entrada.clave_idempotencia,
                   huella=h,estado='ACTIVA',fecha_local=local.date(),zona_horaria=zona,vence_en=vence)
    s.add(r);s.flush()
    s.add_all(AsignacionReserva(reserva_id=r.id,lote_id=a['lote_id'],cantidad=a['cantidad']) for l in lineas for a in l['asignaciones'])
    s.flush();return r,False


def liberar(s,id_,integracion_id,motivo):
    r=obtener(s,id_,integracion_id,bloquear=True)
    if r.estado=='CONSUMIDA':raise ErrorAPI(409,'RESERVA_CONSUMIDA','La reserva tiene una venta; revisar el pedido y el pago.')
    r.estado='LIBERADA';r.motivo_liberacion=motivo;s.flush()
    return r
