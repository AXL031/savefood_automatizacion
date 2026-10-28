"""Administración de publicación y API privada para la integración, sin cuenta de cliente."""
import os
from fastapi import APIRouter, Depends, Response
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.base_datos import obtener_sesion
from app.core.identidad import identidad_actual, requiere_administrador
from app.core.errores import ErrorAPI
from app.modules.ventas.caja import catalogo_caja
from app.modules.ventas.tienda import registrar, acuse
from .seguridad import integracion
from . import esquemas as e, catalogo, reservas, publicaciones
from .modelos import PublicacionProducto, EventoPublicacion, ReservaTienda

router=APIRouter(tags=['comercio-tienda'])


def confirmar(s):
    try:s.commit()
    except IntegrityError:
        s.rollback()
        raise ErrorAPI(409,'OPERACION_EN_CONFLICTO','Otra operación cambió este registro. Recupera su resultado con la misma clave.') from None


@router.get('/tienda-admin/productos')
def productos(u=Depends(identidad_actual),s:Session=Depends(obtener_sesion)):
    base=catalogo_caja(s)
    fichas={f.producto_id:f for f in s.scalars(select(PublicacionProducto))}
    return {'datos':{**base,'productos':[{**p,'ficha':{'version':fichas[p['id']].version,
        'publicado':fichas[p['id']].publicado,**fichas[p['id']].datos} if p['id'] in fichas else
        {'version':0,'publicado':False,'categoria':'otros','descripcion':'','presentacion':'Unidad','imagen':''}} for p in base['productos']]}}


@router.put('/tienda-admin/productos/{id}')
def ficha(id:int,entrada:e.Ficha,u=Depends(requiere_administrador),s:Session=Depends(obtener_sesion)):
    f=catalogo.guardar_ficha(s,id,entrada,u)
    version=f.version
    publicaciones.preparar(s);confirmar(s)
    return {'datos':{'version':version}}


@router.post('/tienda-admin/sincronizar')
def sincronizar(u=Depends(requiere_administrador),s:Session=Depends(obtener_sesion)):
    r=publicaciones.preparar(s)
    salida={'id':r.id,'version':r.version,'estado':r.estado}
    confirmar(s)
    return {'datos':salida}


@router.get('/tienda-admin/estado')
def estado(u=Depends(identidad_actual),s:Session=Depends(obtener_sesion)):
    c=catalogo.configuracion(s)
    registros=list(s.scalars(select(EventoPublicacion).order_by(EventoPublicacion.version.desc()).limit(20)))
    return {'datos':{'habilitada':os.getenv('TIENDA_INTEGRACION_HABILITADA')=='1',
        'credenciales_configuradas':len(os.getenv('TIENDA_INTEGRACION_TOKEN',''))>=32 and len(os.getenv('TIENDA_PUBLICACION_TOKEN',''))>=32,
        'origen':c.origen if c else None,'version':c.version if c else 0,
        'entregas':[{'version':r.version,'estado':r.estado,'intentos':r.intentos,'ultimo_error':r.ultimo_error} for r in registros]}}


@router.get('/tienda-admin/reservas')
def lista_reservas(u=Depends(identidad_actual),s:Session=Depends(obtener_sesion)):
    return {'datos':[reservas.vista(s,r) for r in s.scalars(select(ReservaTienda).order_by(ReservaTienda.creado_en.desc()).limit(100))]}


@router.get('/integracion-tienda/stock')
def stock(i=Depends(integracion),s:Session=Depends(obtener_sesion)):
    datos=catalogo.catalogo_publicado(s)
    return {'datos':{'origen':datos['origen'],'fecha_local':datos['fecha_local'],
        'productos':[{'producto_id':p['id'],'estado_stock':p['estado_stock'],'promocion':p['promocion']} for p in datos['productos']]}}


@router.post('/integracion-tienda/cotizar')
def cotizar(entrada:e.Consulta,i=Depends(integracion),s:Session=Depends(obtener_sesion)):
    return {'datos':catalogo.cotizar(s,entrada)[0]}


@router.post('/integracion-tienda/reservas',status_code=201)
def reservar(entrada:e.CrearReserva,respuesta:Response,i=Depends(integracion),s:Session=Depends(obtener_sesion)):
    r,repetida=reservas.crear(s,entrada,i);salida=reservas.vista(s,r)
    confirmar(s);respuesta.status_code=200 if repetida else 201
    return {'datos':salida}


@router.get('/integracion-tienda/reservas/{id}')
def detalle(id:str,i=Depends(integracion),s:Session=Depends(obtener_sesion)):
    return {'datos':reservas.vista(s,reservas.obtener(s,id,i))}


@router.post('/integracion-tienda/reservas/{id}/liberar')
def liberar(id:str,entrada:e.LiberarReserva,i=Depends(integracion),s:Session=Depends(obtener_sesion)):
    r=reservas.liberar(s,id,i,entrada.motivo);salida=reservas.vista(s,r);confirmar(s)
    return {'datos':salida}


@router.post('/integracion-tienda/ventas',status_code=201)
def vender(entrada:e.ConfirmarVenta,respuesta:Response,i=Depends(integracion),s:Session=Depends(obtener_sesion)):
    t,repetida=registrar(s,entrada,i);salida=acuse(t,str(entrada.origen))
    confirmar(s);respuesta.status_code=200 if repetida else 201
    return {'datos':salida}
