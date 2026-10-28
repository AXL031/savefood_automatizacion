"""HTTP autenticado y accesos públicos limitados del ciclo operativo."""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, Response as HttpResponse
from pydantic import Field
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.core.base_datos import obtener_sesion
from app.core.identidad import identidad_actual, requiere_administrador
from app.core.errores import ErrorAPI
from app.modules.productos.modelos import Producto
from app.modules.inventario.modelos import LoteProducto, LoteIngrediente
from app.modules.ingredientes.modelos import Ingrediente
from app.modules.planificacion.modelos import PlanProduccion, ElementoPlan
from app.modules.compras.modelos import PedidoCompra
from app.modules.compras.servicio import detalle_pedido
from . import esquemas as e
from .modelos import RegistroOperacion, PromocionOperacion, AvisoOperacion, SolicitudProveedor
from .servicio import configuracion, fecha_operativa, producidos, producir
from .proveedores import crear_enlace, detalle_publico, responder, recibir_asistido
from . import enlaces_http  # noqa: F401; oculta token en el log HTTP

router=APIRouter(tags=['operacion-integrada'])


@router.get('/operaciones/salud')
def salud_operativa(s:Session=Depends(obtener_sesion)):
    from sqlalchemy import text
    s.execute(text('SELECT 1'))
    return {'estado':'ok'}


def confirmar(s):
    try:s.commit()
    except IntegrityError:
        s.rollback()
        raise ErrorAPI(409,'OPERACION_EN_CONFLICTO','Otra operación modificó este registro; actualiza antes de continuar.') from None


@router.get('/operaciones/resumen')
def resumen(u=Depends(identidad_actual),s:Session=Depends(obtener_sesion)):
    planes=[]
    for p in s.scalars(select(PlanProduccion).order_by(PlanProduccion.id.desc()).limit(100)):
        hechos=producidos(s,p.id)
        lineas=[]
        for l in s.scalars(select(ElementoPlan).where(ElementoPlan.plan_id==p.id)):
            lineas.append({'producto_id':l.producto_id,'nombre':s.get(Producto,l.producto_id).nombre,
                'previsto':l.cantidad_producir,'producido':hechos.get(l.producto_id,0),
                'pendiente':None if l.cantidad_producir is None else l.cantidad_producir-hechos.get(l.producto_id,0)})
        planes.append({'id':p.id,'fecha':str(p.fecha_objetivo),'lineas':lineas})
    pedidos=[]
    for p in s.scalars(select(PedidoCompra).order_by(PedidoCompra.id.desc()).limit(100)):
        ultimo=s.scalar(select(SolicitudProveedor).where(SolicitudProveedor.pedido_id==p.id).order_by(SolicitudProveedor.id.desc()).limit(1))
        d=detalle_pedido(s,p.id)
        d['respuesta_proveedor']=ultimo.estado if ultimo else 'SIN_ENLACE'
        pedidos.append(d)
    datos={'fecha_operativa':str(fecha_operativa(s)),'configuracion':configuracion(s, crear=False).datos,'planes':planes,'pedidos':pedidos,
        'productos':[{'id':p.id,'nombre':p.nombre,'codigo':p.codigo} for p in s.scalars(select(Producto).where(Producto.activo.is_(True)).order_by(Producto.id))],
        'promociones':[{'id':p.id,'lote_id':p.lote_id,'estado':p.estado,'descuento':p.descuento,'motivo':p.motivo,'fecha':str(p.fecha)} for p in s.scalars(select(PromocionOperacion).order_by(PromocionOperacion.id.desc()).limit(100))],
        'registros':[{'id':r.id,'tipo':r.tipo,'fecha':str(r.fecha),'plan_id':r.plan_id,'resultado':r.resultado} for r in s.scalars(select(RegistroOperacion).order_by(RegistroOperacion.id.desc()).limit(100))]}
    return {'datos':datos}


@router.post('/operaciones/producciones')
def produccion(entrada:e.Produccion,u=Depends(identidad_actual),s:Session=Depends(obtener_sesion)):
    r=producir(s,entrada.model_dump(mode='json'),u.id);resultado={'id':r.id,**r.resultado};confirmar(s);return {'datos':resultado}


@router.put('/operaciones/configuracion')
def configurar(entrada:e.Configuracion,u=Depends(requiere_administrador),s:Session=Depends(obtener_sesion)):
    c=configuracion(s)
    c=s.scalar(select(type(c)).where(type(c).id==1).with_for_update())
    from app.modules.inventario.operacion import bloquear_catalogo
    bloquear_catalogo(s,entrada.producto_ids)
    c.datos=entrada.model_dump(mode='json');c.proxima_revision=None
    confirmar(s);return {'datos':c.datos}


@router.post('/operaciones/revisar')
def revision(u=Depends(requiere_administrador),s:Session=Depends(obtener_sesion)):
    from .monitoreo import revisar
    r=revisar(s,forzar=True);confirmar(s);return {'datos':r}


class Decision(e.Estricto):
    aprobar:bool


@router.post('/operaciones/promociones/{id}/decision')
def decision(id:int,entrada:Decision,u=Depends(requiere_administrador),s:Session=Depends(obtener_sesion)):
    configuracion(s)
    from .modelos import ConfiguracionOperacion
    s.scalar(select(ConfiguracionOperacion).where(ConfiguracionOperacion.id==1).with_for_update())
    p=s.get(PromocionOperacion,id)
    if not p:raise ErrorAPI(404,'PROMOCION_NO_ENCONTRADA','No existe la sugerencia.')
    referencia=s.get(LoteProducto,p.lote_id)
    from app.modules.inventario.operacion import bloquear_catalogo
    bloquear_catalogo(s,[referencia.producto_id])
    lote=s.scalar(select(LoteProducto).where(LoteProducto.id==p.lote_id).with_for_update())
    p=s.scalar(select(PromocionOperacion).where(PromocionOperacion.id==id).with_for_update().execution_options(populate_existing=True))
    estado='APROBADA' if entrada.aprobar else 'RECHAZADA'
    if p.estado==estado:return {'datos':{'estado':estado}}
    if p.estado!='PENDIENTE' or p.fecha!=fecha_operativa(s) or (lote.fecha_ingreso and lote.fecha_ingreso>fecha_operativa(s)) or not lote.fecha_limite_venta or lote.fecha_limite_venta<fecha_operativa(s) or lote.saldo_disponible<=0 or not lote.fecha_caducidad or lote.fecha_caducidad<fecha_operativa(s):
        raise ErrorAPI(409,'PROMOCION_NO_APROBABLE','La sugerencia ya fue resuelta, se agotó o venció.')
    p.estado=estado;p.decidido_por=u.id;confirmar(s);return {'datos':{'estado':estado}}


@router.get('/operaciones/avisos')
def avisos(u=Depends(requiere_administrador),s:Session=Depends(obtener_sesion)):
    return {'datos':[{'id':a.id,'titulo':a.titulo,'datos':a.datos,'leido':a.leido,'resolucion':a.resolucion,'creado_en':a.creado_en.isoformat()} for a in s.scalars(select(AvisoOperacion).order_by(AvisoOperacion.id.desc()).limit(200))]}


class LeerAviso(e.Estricto):
    leido:bool=True
    resolucion:str|None=Field(default=None,min_length=5,max_length=1000)


@router.patch('/operaciones/avisos/{id}')
def leer(id:int,entrada:LeerAviso,u=Depends(requiere_administrador),s:Session=Depends(obtener_sesion)):
    a=s.scalar(select(AvisoOperacion).where(AvisoOperacion.id==id).with_for_update())
    if not a:raise ErrorAPI(404,'AVISO_NO_ENCONTRADO','No existe el aviso.')
    a.leido=entrada.leido
    if entrada.resolucion:
        a.resolucion=entrada.resolucion;a.resuelto_por=u.id
        historial=list(a.datos.get('historial_resoluciones',[]))
        historial.append({'resolucion':entrada.resolucion,'usuario_id':u.id,'fecha':datetime.now(timezone.utc).isoformat()})
        a.datos={**a.datos,'historial_resoluciones':historial}
    confirmar(s);return {'datos':{'id':a.id,'leido':a.leido,'resolucion':a.resolucion}}


@router.post('/operaciones/pedidos/{id}/enlace')
def enlace(id:int,u=Depends(requiere_administrador),s:Session=Depends(obtener_sesion)):
    resultado=crear_enlace(s,id);confirmar(s);return {'datos':resultado}


@router.get('/proveedor/pedidos/{token}')
def publico(token:str,response:HttpResponse,s:Session=Depends(obtener_sesion)):
    response.headers['Cache-Control']='no-store';response.headers['Referrer-Policy']='no-referrer'
    return {'datos':detalle_publico(s,token)}


@router.post('/proveedor/pedidos/{token}')
def respuesta(token:str,entrada:e.Respuesta,s:Session=Depends(obtener_sesion)):
    r=responder(s,token,entrada.model_dump(mode='json'));confirmar(s);return {'datos':{'estado':r.estado}}


@router.post('/operaciones/recepciones/{id}')
def recepcion(id:int,entrada:e.Recepcion,u=Depends(identidad_actual),s:Session=Depends(obtener_sesion)):
    r=recibir_asistido(s,id,entrada.model_dump(mode='json'),u);resultado=r.resultado;confirmar(s);return {'datos':resultado}

