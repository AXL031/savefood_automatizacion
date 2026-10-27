"""HTTP autenticado y accesos públicos limitados del ciclo operativo."""
import csv
import io
import os
from datetime import datetime, timezone
from decimal import Decimal
from fastapi import APIRouter, Depends, Response as HttpResponse
from pydantic import Field
from pwdlib import PasswordHash
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
from app.modules.tienda.autenticacion import cliente_actual, emitir_token_cliente
from app.modules.tienda.modelos import ClienteTienda
from app.modules.compras.modelos import PedidoCompra
from app.modules.compras.servicio import detalle_pedido
from . import esquemas as e
from .modelos import RegistroOperacion, FichaTienda, PromocionOperacion, AvisoOperacion, SolicitudProveedor, CuentaClienteLocal
from .servicio import configuracion, fecha_operativa, producidos, producir, vender, aviso, nuevo
from .proveedores import crear_enlace, detalle_publico, responder, recibir_asistido
from .tienda import catalogo, cotizar, comprar

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
    datos={'fecha_operativa':str(fecha_operativa(s)),'configuracion':configuracion(s).datos,'planes':planes,'pedidos':pedidos,
        'productos':[{'id':p.id,'nombre':p.nombre,'codigo':p.codigo} for p in s.scalars(select(Producto).where(Producto.activo.is_(True)).order_by(Producto.id))],
        'fichas':[{'producto_id':f.producto_id,'precio':str(f.precio),'version':f.version,**f.datos} for f in s.scalars(select(FichaTienda).order_by(FichaTienda.producto_id))],
        'promociones':[{'id':p.id,'lote_id':p.lote_id,'estado':p.estado,'descuento':p.descuento,'motivo':p.motivo,'fecha':str(p.fecha)} for p in s.scalars(select(PromocionOperacion).order_by(PromocionOperacion.id.desc()).limit(100))],
        'registros':[{'id':r.id,'tipo':r.tipo,'fecha':str(r.fecha),'plan_id':r.plan_id,'resultado':r.resultado} for r in s.scalars(select(RegistroOperacion).order_by(RegistroOperacion.id.desc()).limit(100))]}
    confirmar(s)
    return {'datos':datos}


@router.post('/operaciones/producciones')
def produccion(entrada:e.Produccion,u=Depends(identidad_actual),s:Session=Depends(obtener_sesion)):
    r=producir(s,entrada.model_dump(mode='json'),u.id);resultado={'id':r.id,**r.resultado};confirmar(s);return {'datos':resultado}


@router.post('/operaciones/ventas')
def venta(entrada:e.Operacion,u=Depends(identidad_actual),s:Session=Depends(obtener_sesion)):
    r=vender(s,entrada.model_dump(mode='json'),u.id);resultado={'id':r.id,**r.resultado};confirmar(s);return {'datos':resultado}


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
    if p.estado!='PENDIENTE' or p.fecha!=fecha_operativa(s) or lote.saldo_disponible<=0 or not lote.fecha_caducidad or lote.fecha_caducidad<fecha_operativa(s):
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


def guardar_ficha(s,producto_id,entrada,u):
    from app.modules.inventario.operacion import bloquear_catalogo
    bloquear_catalogo(s,[producto_id])
    f=s.get(FichaTienda,producto_id)
    datos=entrada.model_dump(mode='json',exclude={'precio'})
    if f and f.precio==entrada.precio and f.datos==datos:return f
    if not f:f=FichaTienda(producto_id=producto_id,precio=entrada.precio,version=0,datos=datos);s.add(f)
    f.precio=entrada.precio;f.version+=1;f.datos=datos
    nuevo(s,f'precio:{producto_id}:{f.version}','PRECIO',entrada.model_dump(mode='json'),fecha_operativa(s),u.id)
    s.flush();return f


@router.put('/operaciones/productos/{id}/ficha')
def ficha(id:int,entrada:e.Ficha,u=Depends(requiere_administrador),s:Session=Depends(obtener_sesion)):
    f=guardar_ficha(s,id,entrada,u);confirmar(s);return {'datos':{'version':f.version}}


class CsvPrecios(e.Estricto):
    csv:str=Field(max_length=500000)


@router.post('/operaciones/precios/csv')
def precios(entrada:CsvPrecios,u=Depends(requiere_administrador),s:Session=Depends(obtener_sesion)):
    filas=list(csv.DictReader(io.StringIO(entrada.csv)))
    if not 1<=len(filas)<=500:raise ErrorAPI(422,'CSV_INVALIDO','Se requieren 1–500 filas.')
    validadas=[];ids=set()
    try:
        for fila in filas:
            id=int(fila['producto_id'])
            if id in ids:raise ValueError()
            ids.add(id);validadas.append((id,e.Ficha(precio=fila['precio'])))
    except (KeyError,ValueError):raise ErrorAPI(422,'CSV_INVALIDO','Usa producto_id,precio sin duplicados y con precios positivos.') from None
    for id,d in sorted(validadas):
        anterior=s.get(FichaTienda,id)
        if anterior:d=e.Ficha(precio=d.precio,**anterior.datos)
        guardar_ficha(s,id,d,u)
    confirmar(s);return {'datos':{'filas':len(filas)}}


@router.get('/tienda/catalogo')
def catalogo_publico(s:Session=Depends(obtener_sesion)):
    r=catalogo(s);confirmar(s);return {'datos':r}


@router.get('/tienda/stock')
def stock(s:Session=Depends(obtener_sesion)):
    r=[{'producto_id':p['id'],'estado_stock':p['estado_stock'],'promocion_id':p['promocion']['id'] if p['promocion'] else None} for p in catalogo(s)['productos']]
    confirmar(s);return {'datos':r}


@router.post('/tienda/carrito/cotizar')
def cotizacion(entrada:e.Cotizacion,s:Session=Depends(obtener_sesion)):
    r=cotizar(s,entrada.model_dump(mode='json')['lineas']);confirmar(s);return {'datos':r}


@router.post('/tienda/pedidos',status_code=201)
def pedido(entrada:e.Compra,c=Depends(cliente_actual),s:Session=Depends(obtener_sesion)):
    r=comprar(s,entrada.model_dump(mode='json'),c);confirmar(s);return {'datos':r}


@router.get('/tienda/pedidos')
def pedidos_cliente(c=Depends(cliente_actual),s:Session=Depends(obtener_sesion)):
    return {'datos':[r.resultado for r in s.scalars(select(RegistroOperacion).where(RegistroOperacion.tipo=='VENTA_TIENDA',RegistroOperacion.cliente_id==c.id).order_by(RegistroOperacion.id.desc()))]}


@router.get('/tienda/pedidos/{id}')
def pedido_cliente(id:int,c=Depends(cliente_actual),s:Session=Depends(obtener_sesion)):
    r=s.get(RegistroOperacion,id)
    if not r or r.tipo!='VENTA_TIENDA' or r.cliente_id!=c.id:raise ErrorAPI(404,'PEDIDO_NO_ENCONTRADO','El pedido no existe.')
    return {'datos':r.resultado}


class CredencialesCliente(e.Estricto):
    correo:str=Field(min_length=5,max_length=254)
    contrasena:str=Field(min_length=8,max_length=128)


@router.post('/tienda/sesion/local')
def login_local(entrada:CredencialesCliente,s:Session=Depends(obtener_sesion)):
    if os.getenv('HABILITAR_CLIENTE_LOCAL')!='1':raise ErrorAPI(403,'ACCESO_LOCAL_DESHABILITADO','Usa el inicio de sesión con Google.')
    cuenta=s.scalar(select(CuentaClienteLocal).where(CuentaClienteLocal.correo==entrada.correo.strip().lower()))
    if not cuenta or not PasswordHash.recommended().verify(entrada.contrasena,cuenta.hash_contrasena):
        raise ErrorAPI(401,'CREDENCIALES_INVALIDAS','Credenciales inválidas.')
    c=s.get(ClienteTienda,cuenta.cliente_id)
    if not c.activo:raise ErrorAPI(401,'CREDENCIALES_INVALIDAS','Credenciales inválidas.')
    return {'datos':{'token':emitir_token_cliente(c),'cliente':{'id':c.id,'correo':c.correo,'nombre':c.nombre}}}
