"""Solo HTTP a FoodSave; esta aplicación nunca importa su código ni abre su base."""
import hashlib
import hmac
import json
import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID
import httpx
from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from .base_datos import obtener_sesion
from .errores import ErrorAPI
from .modelos import CatalogoPublicado, PedidoComercial, PagoTiendaPrueba, TransaccionPaymePrueba

router=APIRouter(tags=['integracion-foodsave'])
APROBADOS={'AUTORIZADO','LIQUIDADO','DEPOSITADO'}
TERMINALES={'DENEGADO','INVALIDO','EXPIRADO','CANCELADO','EXTORNADO'}


def ahora():return datetime.now(timezone.utc)


def modo():return 'api' if os.getenv('TIENDA_MODO','ejemplo')=='api' else 'ejemplo'


def foodsave(ruta,metodo='GET',cuerpo=None):
    base=os.getenv('FOODSAVE_API_INTERNA_URL','').rstrip('/')
    token=os.getenv('FOODSAVE_INTEGRACION_TOKEN','')
    if len(token)<32 or not base.startswith(('http://','https://')):
        raise ErrorAPI(503,'INTEGRACION_NO_CONFIGURADA','La conexión de tienda con FoodSave está pendiente de configuración.')
    try:
        with httpx.Client(timeout=5,follow_redirects=False) as cliente:
            r=cliente.request(metodo,base+'/api/v1/integracion-tienda'+ruta,
                              headers={'Authorization':'Bearer '+token},json=cuerpo)
        if len(r.content)>2_000_000:raise ValueError()
        datos=r.json()
    except (httpx.RequestError,ValueError):
        raise ErrorAPI(503,'FOODSAVE_NO_DISPONIBLE','No se pudo comunicar con FoodSave. Conservamos la operación para recuperarla.') from None
    if not 200<=r.status_code<300:
        error=datos.get('error',{})
        raise ErrorAPI(r.status_code if r.status_code in (400,401,403,404,409,422,503) else 502,
                       error.get('codigo','FOODSAVE_NO_DISPONIBLE'),error.get('mensaje','FoodSave no confirmó la operación.'))
    if 'datos' not in datos:raise ErrorAPI(502,'ACUSE_INVALIDO','FoodSave no entregó una respuesta válida.')
    return datos['datos']


def autorizar_publicacion(authorization:str=Header(default='')):
    esperado=os.getenv('FOODSAVE_PUBLICACION_TOKEN','')
    if len(esperado)<32:raise ErrorAPI(503,'PUBLICACION_NO_CONFIGURADA','La recepción del catálogo no está configurada.')
    recibido=authorization[7:] if authorization.startswith('Bearer ') else ''
    if not hmac.compare_digest(recibido,esperado):raise ErrorAPI(401,'PUBLICACION_NO_AUTORIZADA','La publicación no está autorizada.')


class Publicacion(BaseModel):
    model_config=ConfigDict(extra='forbid')
    origen:UUID
    version:int=Field(gt=0,strict=True)
    fecha_generacion:datetime
    fecha_local:str=Field(pattern=r'^\d{4}-\d{2}-\d{2}$')
    moneda:str=Field(pattern=r'^PEN$')
    categorias:list[dict]=Field(max_length=20)
    productos:list[dict]=Field(max_length=2000)


def recibir(s,entrada):
    datos=entrada.model_dump(mode='json')
    # Validar identidad, importes y campos públicos sin confiar en posiciones del array.
    ids=set()
    for p in datos['productos']:
        if (not isinstance(p.get('id'),int) or isinstance(p['id'],bool) or p['id']<=0 or p['id'] in ids
            or not isinstance(p.get('nombre'),str) or not 1<=len(p['nombre'])<=160
            or p.get('estado_stock') not in ('DISPONIBLE','ULTIMAS_UNIDADES','AGOTADO')
            or p.get('moneda')!='PEN'):
            raise ErrorAPI(422,'PUBLICACION_INVALIDA','El catálogo recibido contiene productos inválidos.')
        try:
            precio=Decimal(p['precio'])
            if not precio.is_finite() or not Decimal('0')<precio<=Decimal('999999.99') or precio.as_tuple().exponent < -2:raise ValueError()
        except (KeyError,ValueError,TypeError,ArithmeticError):
            raise ErrorAPI(422,'PUBLICACION_INVALIDA','El catálogo contiene precios inválidos.') from None
        ids.add(p['id'])
    h=hashlib.sha256(json.dumps(datos,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    r=s.get(CatalogoPublicado,1)
    if r and r.origen!=str(entrada.origen):raise ErrorAPI(409,'CATALOGO_ORIGEN_DISTINTO','Esta tienda está vinculada a otra instalación.')
    if r and entrada.version==r.version and h!=r.huella:raise ErrorAPI(409,'VERSION_REUTILIZADA','La versión ya se recibió con otro contenido.')
    aplicada=not r or entrada.version>r.version
    if aplicada:
        if not r:r=CatalogoPublicado(id=1);s.add(r)
        r.origen=str(entrada.origen);r.version=entrada.version;r.huella=h;r.datos=datos;r.recibido_en=ahora()
        s.flush()
    return {'origen':str(entrada.origen),'version':entrada.version,'version_actual':r.version,'aplicada':aplicada}


@router.put('/integracion/catalogo')
def publicar(entrada:Publicacion,a=Depends(autorizar_publicacion),s:Session=Depends(obtener_sesion)):
    salida=recibir(s,entrada);s.commit();return {'datos':salida}


def catalogo_replica(s):
    r=s.get(CatalogoPublicado,1)
    if not r:raise ErrorAPI(503,'CATALOGO_NO_PUBLICADO','FoodSave todavía no ha publicado productos para esta tienda.')
    return json.loads(json.dumps(r.datos))


def catalogo_con_disponibilidad(s):
    datos=catalogo_replica(s);s.commit()  # No mantener la transacción SQLite durante HTTP.
    actualizado=True
    try:
        stock=foodsave('/stock')
        if stock.get('origen')!=datos['origen']:raise ErrorAPI(409,'CATALOGO_ORIGEN_DISTINTO','El origen del catálogo cambió.')
        por_id={p['producto_id']:p for p in stock['productos']}
        for p in datos['productos']:
            estado=por_id.get(p['id'])
            p['estado_stock']=estado['estado_stock'] if estado else 'AGOTADO'
            p['promocion']=estado.get('promocion') if estado else None
    except ErrorAPI:actualizado=False
    return {**datos,'modo':'api','disponibilidad_actualizada':actualizado}


def cotizar_comercio(s,datos):
    publicado=catalogo_replica(s)
    if datos.origen_catalogo!=publicado['origen']:
        raise ErrorAPI(409,'CATALOGO_CAMBIO','El catálogo cambió de origen. Vuelve a seleccionar los productos.')
    s.commit()
    return foodsave('/cotizar','POST',{'origen':publicado['origen'],'lineas':[l.model_dump() for l in datos.lineas]})


def preparar_vinculo(s,pago,cotizacion):
    v=PedidoComercial(pago_id=pago.id,origen=cotizacion['origen'],solicitud_reserva={
        'origen':cotizacion['origen'],'clave_idempotencia':pago.id,'cotizacion_hash':cotizacion['huella'],
        'lineas':[{'producto_id':l['producto_id'],'cantidad':l['cantidad']} for l in cotizacion['lineas']]},
        reserva=None,evento_venta=None,acuse=None,estado='PREPARANDO',intentos=0,proximo_intento=ahora())
    s.add(v);s.flush();return v


def asegurar_reserva(s,pago_id):
    v=s.get(PedidoComercial,pago_id)
    if not v:return True
    if v.reserva:
        vence=datetime.fromisoformat(v.reserva['vence_en'].replace('Z','+00:00'))
        if vence<=ahora() and v.estado not in ('REGISTRADA','PENDIENTE_VENTA'):
            p=s.get(PagoTiendaPrueba,pago_id);p.estado='EXPIRADO';v.estado='REVISION_REQUERIDA';v.ultimo_error='La reserva venció antes de completar el pago.';s.commit()
            return False
        return v.estado not in ('REVISION_REQUERIDA','LIBERADA','LIBERACION_PENDIENTE')
    cuerpo=json.loads(json.dumps(v.solicitud_reserva));s.commit()
    try:r=foodsave('/reservas','POST',cuerpo)
    except ErrorAPI as error:
        if error.status_code in (400,404,409,422):
            p=s.get(PagoTiendaPrueba,pago_id);v=s.get(PedidoComercial,pago_id)
            p.estado='INVALIDO';v.estado='REVISION_REQUERIDA';v.ultimo_error=error.detail[:160];s.commit()
            return False
        raise
    v=s.get(PedidoComercial,pago_id);p=s.get(PagoTiendaPrueba,pago_id)
    if (not isinstance(r.get('id'),str) or r.get('estado')!='ACTIVA'
        or Decimal(r.get('cotizacion',{}).get('total','-1')) != Decimal(p.monto_centimos)/100
        or r.get('cotizacion',{}).get('moneda')!='PEN'):
        v.estado='REVISION_REQUERIDA';v.ultimo_error='La reserva no coincide con el pago preparado.';p.estado='INVALIDO';s.commit();return False
    v.reserva=r;v.estado='RESERVADA';v.ultimo_error=None;s.commit();return True


def preparar_salida(s,pago):
    v=s.get(PedidoComercial,pago.id)
    if not v:return
    if pago.estado in APROBADOS:
        aprobadas=list(s.scalars(select(TransaccionPaymePrueba.transaction_id).where(
            TransaccionPaymePrueba.pago_id==pago.id,TransaccionPaymePrueba.estado.in_(APROBADOS))))
        if len(aprobadas)>1:
            v.estado='REVISION_REQUERIDA';v.ultimo_error='Hay más de una transacción aprobada para este pago. Revisar sin crear otra venta.';return
    if pago.estado in APROBADOS and v.estado!='REGISTRADA':
        if v.estado=='REVISION_REQUERIDA':return
        if not v.reserva:
            v.estado='REVISION_REQUERIDA';v.ultimo_error='Se verificó un pago sin reserva confirmada.';return
        if not v.evento_venta:
            t=s.scalar(select(TransaccionPaymePrueba).where(TransaccionPaymePrueba.pago_id==pago.id,
                TransaccionPaymePrueba.estado.in_(APROBADOS)).order_by(TransaccionPaymePrueba.transaction_id).limit(1))
            if not t:return
            v.evento_venta={'origen':v.origen,'reserva_id':v.reserva['id'],'evento_id':pago.id,'pedido_externo':pago.id,
                'pago':{'proveedor':'PAYME','ambiente':'PRUEBAS','verificado':True,'operacion':pago.operacion,
                        'transaccion':t.transaction_id,'metodo':pago.metodo,'monto':f'{Decimal(pago.monto_centimos)/100:.2f}','moneda':'PEN'}}
        v.estado='PENDIENTE_VENTA';v.proximo_intento=ahora()
    elif pago.estado in TERMINALES:
        if v.acuse:
            v.estado='REVISION_REQUERIDA';v.ultimo_error='El pago cambió después de registrar la venta. Revisar pedido y pago.'
        elif v.reserva:
            v.estado='LIBERACION_PENDIENTE';v.proximo_intento=ahora()


def sincronizar_pago(s,pago_id):
    v=s.get(PedidoComercial,pago_id)
    if not v or v.estado not in ('PENDIENTE_VENTA','LIBERACION_PENDIENTE'):return
    p=s.get(PagoTiendaPrueba,pago_id)
    estado=v.estado;evento=json.loads(json.dumps(v.evento_venta)) if v.evento_venta else None
    reserva_id=v.reserva['id'];motivo=p.estado;s.commit()
    try:
        if estado=='PENDIENTE_VENTA':
            r=foodsave('/ventas','POST',evento)
            if (r.get('pedido_externo')!=pago_id or r.get('origen')!=evento['origen'] or not isinstance(r.get('ticket_id'),int)
                or Decimal(r.get('total','-1'))!=Decimal(evento['pago']['monto']) or r.get('moneda')!='PEN'):
                raise ErrorAPI(502,'ACUSE_INVALIDO','La venta sigue pendiente de un acuse válido.')
        else:r=foodsave('/reservas/'+reserva_id+'/liberar','POST',{'motivo':motivo})
    except ErrorAPI as error:
        v=s.get(PedidoComercial,pago_id)
        if v.estado!=estado:return
        v.intentos+=1;v.ultimo_error=error.detail[:160]
        if error.status_code in (400,404,409,422):v.estado='REVISION_REQUERIDA'
        else:v.proximo_intento=ahora()+timedelta(seconds=min(300,5*2**min(v.intentos,6)))
        s.commit();return
    v=s.get(PedidoComercial,pago_id);p=s.get(PagoTiendaPrueba,pago_id)
    v.intentos+=1
    if estado=='PENDIENTE_VENTA':
        v.acuse=r
        if v.estado!='REVISION_REQUERIDA':
            v.estado='REGISTRADA' if p.estado in APROBADOS else 'REVISION_REQUERIDA'
            v.ultimo_error=None if v.estado=='REGISTRADA' else 'El pago cambió durante el registro; revisar la venta conservada.'
    elif v.estado==estado:v.estado='LIBERADA';v.ultimo_error=None
    s.commit()


def vista_comercial(s,pago):
    v=s.get(PedidoComercial,pago.id)
    if not v:return {'origen':'EJEMPLO','estado':'SIN_VENTA','ticket':None,'reserva_vence_en':None,'mensaje':'Este pago de ejemplo no genera una venta ni entrega.'}
    vence=v.reserva.get('vence_en') if v.reserva else None
    vencida=v.estado=='RESERVADA' and vence and datetime.fromisoformat(vence.replace('Z','+00:00'))<=ahora()
    return {'origen':'FOODSAVE','estado':'RESERVA_VENCIDA' if vencida else v.estado,'ticket':v.acuse,
            'reserva_vence_en':vence,'mensaje':'La reserva venció; consulta el pago antes de iniciar otra compra.' if vencida else v.ultimo_error}
