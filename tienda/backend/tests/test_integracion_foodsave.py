"""Frontera HTTP y estados comerciales; sin importar FoodSave ni usar pagos reales."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from uuid import uuid4
from decimal import Decimal
import pytest
from sqlalchemy import select, func
from test_payme import db, api, entrada, resultado  # noqa
from checkout import integracion
from checkout.integracion import router
from checkout.rutas_catalogo import router as catalogo_router
from checkout.modelos import PedidoComercial, CatalogoPublicado, PagoTiendaPrueba


@pytest.fixture
def conexion(api,db,monkeypatch):
    c,proveedor=api
    c.app.include_router(router,prefix='/api/v1');c.app.include_router(catalogo_router,prefix='/api/v1')
    monkeypatch.setenv('TIENDA_MODO','api');monkeypatch.setenv('FOODSAVE_PUBLICACION_TOKEN','token-publicacion-pruebas-20261028-largo')
    origen=str(uuid4());calls=[];reservas={};fallar={'venta':False,'reserva':False}
    producto={'id':101,'codigo':'PAN-REAL','nombre':'Producto de FoodSave','precio':'3.00','moneda':'PEN','estado_stock':'DISPONIBLE',
        'categoria':'panes','descripcion':'Producto de prueba','presentacion':'Unidad','imagen':'','promocion':None}
    publicado={'origen':origen,'version':1,'fecha_generacion':datetime.now(timezone.utc).isoformat(),'fecha_local':'2026-10-28',
               'moneda':'PEN','categorias':[],'productos':[producto]}
    def remoto(ruta,metodo='GET',cuerpo=None):
        calls.append((ruta,metodo,deepcopy(cuerpo)))
        if ruta=='/stock':return {'origen':origen,'productos':[{'producto_id':101,'estado_stock':'ULTIMAS_UNIDADES','promocion':None}]}
        if ruta=='/cotizar':
            n=cuerpo['lineas'][0]['cantidad']
            return {'origen':origen,'huella':'c'*64,'moneda':'PEN','total':f'{n*3:.2f}',
                'lineas':[{'producto_id':101,'nombre':'Producto de FoodSave','cantidad':n,'subtotal':f'{n*3:.2f}',
                          'disponible':True,'unidades_con_promocion':0,'precio_unitario_base':'3.00','precio_promocional':None,'estado_stock':'DISPONIBLE'}]}
        if ruta=='/reservas':
            n=cuerpo['lineas'][0]['cantidad']
            r=reservas.setdefault(cuerpo['clave_idempotencia'],{'id':str(uuid4()),'estado':'ACTIVA',
                'vence_en':(datetime.now(timezone.utc)+timedelta(minutes=20)).isoformat(),'cotizacion':{'total':f'{n*3:.2f}','moneda':'PEN'}})
            if fallar['reserva']:
                fallar['reserva']=False
                raise integracion.ErrorAPI(503,'FOODSAVE_NO_DISPONIBLE','Respuesta perdida al reservar')
            return r
        if ruta=='/ventas':
            if fallar['venta']:raise integracion.ErrorAPI(503,'FOODSAVE_NO_DISPONIBLE','Respuesta perdida al confirmar')
            return {'ticket_id':10,'numero':'V-00000010','total':cuerpo['pago']['monto'],'moneda':'PEN','pedido_externo':cuerpo['pedido_externo'],'origen':origen,'fecha_local':'2026-10-28'}
        if ruta.endswith('/liberar'):return {'id':ruta.split('/')[2],'estado':'LIBERADA'}
        raise AssertionError('Ruta HTTP inesperada '+ruta)
    monkeypatch.setattr(integracion,'foodsave',remoto)
    cab={'Authorization':'Bearer token-publicacion-pruebas-20261028-largo'}
    assert c.put('/api/v1/integracion/catalogo',headers=cab,json=publicado).status_code==200
    body=entrada();body['lineas']=[{'producto_id':101,'cantidad':2}];body['origen_catalogo']=origen
    body['cotizacion_hash']='c'*64;body['total_revisado']='6.00'
    return c,proveedor,body,calls,fallar,publicado,cab


def test_catalogo_idempotente_fuera_de_orden_y_origen(conexion,db):
    c,_,_,_,_,p,cab=conexion
    assert c.get('/api/v1/catalogo').json()['datos']['productos'][0]['nombre']=='Producto de FoodSave'
    assert c.get('/api/v1/catalogo').json()['datos']['productos'][0]['estado_stock']=='ULTIMAS_UNIDADES'
    assert c.put('/api/v1/integracion/catalogo',headers=cab,json=p).json()['datos']['aplicada'] is False
    cambiado=deepcopy(p);cambiado['productos'][0]['precio']='4.00'
    assert c.put('/api/v1/integracion/catalogo',headers=cab,json=cambiado).status_code==409
    cambiado['version']=2;assert c.put('/api/v1/integracion/catalogo',headers=cab,json=cambiado).status_code==200
    assert c.put('/api/v1/integracion/catalogo',headers=cab,json=p).json()['datos']['version_actual']==2
    p['origen']=str(uuid4());assert c.put('/api/v1/integracion/catalogo',headers=cab,json=p).status_code==409
    assert c.put('/api/v1/integracion/catalogo',json=p).status_code==401
    assert db.scalar(select(func.count()).select_from(CatalogoPublicado))==1


def test_pago_canonico_invitado_y_evento_de_venta_durable(conexion,db):
    c,proveedor,body,calls,fallar,_,_=conexion
    cot=c.post('/api/v1/pagos/cotizar',json={'origen_catalogo':body['origen_catalogo'],'lineas':body['lineas']})
    assert cot.status_code==200 and cot.json()['datos']['total']=='6.00'
    r=c.post('/api/v1/pagos',json=body);assert r.status_code==200,r.text
    datos=r.json()['datos'];id_=datos['pago']['id']
    assert datos['flex']['payload']['payment_details']['amount']=='600'
    assert datos['pago']['comercial']['estado']=='RESERVADA'
    assert c.post('/api/v1/pagos',json=body).json()['datos']['pago']['id']==id_
    assert len([x for x in calls if x[0]=='/reservas'])==1
    cab={'Authorization':'Bearer '+body['clave_checkout']}
    assert c.get('/api/v1/pagos/recuperar',headers=cab).json()['datos']['id']==id_
    assert c.get('/api/v1/pagos/'+id_).status_code==404
    fallar['venta']=True
    r=c.post('/api/v1/pagos/'+id_+'/verificar',headers=cab,json={'transaction_id':'payme-http-001'})
    assert r.status_code==200,r.text
    assert r.json()['datos']['pagado'] and r.json()['datos']['comercial']['estado']=='PENDIENTE_VENTA'
    evento=db.get(PedidoComercial,id_).evento_venta
    fallar['venta']=False
    r=c.post('/api/v1/pagos/'+id_+'/sincronizar',headers=cab)
    assert r.json()['datos']['comercial']['estado']=='REGISTRADA'
    assert r.json()['datos']['comercial']['ticket']['numero']=='V-00000010'
    ventas=[x[2] for x in calls if x[0]=='/ventas']
    assert ventas[0]==ventas[1]==evento
    assert c.post('/api/v1/pagos/'+id_+'/sincronizar',headers=cab).status_code==200
    assert len([x for x in calls if x[0]=='/ventas'])==2
    assert db.scalar(select(func.count()).select_from(PagoTiendaPrueba))==1


def test_reserva_respuesta_perdida_reusa_clave_sin_otro_pago(conexion,db):
    c,_,body,calls,fallar,_,_=conexion;fallar['reserva']=True
    assert c.post('/api/v1/pagos',json=body).status_code==503
    cab={'Authorization':'Bearer '+body['clave_checkout']}
    p=c.get('/api/v1/pagos/recuperar',headers=cab).json()['datos']
    assert p['comercial']['estado']=='PREPARANDO'
    r=c.post('/api/v1/pagos',json=body);assert r.status_code==200,r.text
    assert r.json()['datos']['pago']['id']==p['id']
    cuerpos=[x[2] for x in calls if x[0]=='/reservas'];assert cuerpos[0]==cuerpos[1]
    assert db.scalar(select(func.count()).select_from(PagoTiendaPrueba))==1


def test_precio_manipulado_y_catalogo_ejemplo_no_se_mezclan(conexion,db):
    c,_,body,calls,_,_,_=conexion
    mal=deepcopy(body);mal['total_revisado']='0.01'
    assert c.post('/api/v1/pagos',json=mal).status_code==409
    mal=deepcopy(body);mal['origen_catalogo']='ejemplo:tienda-ejemplo-20261021'
    assert c.post('/api/v1/pagos',json=mal).status_code==409
    assert db.scalar(select(func.count()).select_from(PagoTiendaPrueba))==0
    assert not any(x[0]=='/reservas' for x in calls)


def test_pago_denegado_libera_y_pago_tardio_queda_en_revision(conexion,db,monkeypatch):
    c,proveedor,body,calls,_,_,_=conexion
    r=c.post('/api/v1/pagos',json=body);id_=r.json()['datos']['pago']['id']
    cab={'Authorization':'Bearer '+body['clave_checkout']};proveedor.estado='DENEGADO'
    r=c.post(f'/api/v1/pagos/{id_}/verificar',headers=cab,json={'transaction_id':'payme-denegado'})
    assert r.json()['datos']['comercial']['estado']=='LIBERADA'
    assert any(x[0].endswith('/liberar') for x in calls)
    def vencida(ruta,metodo='GET',cuerpo=None):raise integracion.ErrorAPI(409,'RESERVA_VENCIDA','Pago tardío, revisar')
    monkeypatch.setattr(integracion,'foodsave',vencida);proveedor.estado='AUTORIZADO'
    r=c.post(f'/api/v1/pagos/{id_}/verificar',headers=cab,json={'transaction_id':'payme-tardio'})
    assert r.status_code==200 and r.json()['datos']['pagado']
    assert r.json()['datos']['comercial']['estado']=='REVISION_REQUERIDA'


@pytest.mark.parametrize('venta_pendiente',[False,True])
def test_dos_transacciones_aprobadas_requieren_revision_sin_segunda_venta(conexion,db,venta_pendiente):
    c,_,body,calls,fallar,_,_=conexion
    id_=c.post('/api/v1/pagos',json=body).json()['datos']['pago']['id']
    cab={'Authorization':'Bearer '+body['clave_checkout']}
    fallar['venta']=venta_pendiente
    primero=c.post(f'/api/v1/pagos/{id_}/verificar',headers=cab,json={'transaction_id':'aprobada-uno'})
    assert primero.status_code==200 and primero.json()['datos']['pagado']
    entregas=len([x for x in calls if x[0]=='/ventas'])
    fallar['venta']=False
    segundo=c.post(f'/api/v1/pagos/{id_}/verificar',headers=cab,json={'transaction_id':'aprobada-dos'})
    assert segundo.status_code==200 and segundo.json()['datos']['pagado']
    assert segundo.json()['datos']['comercial']['estado']=='REVISION_REQUERIDA'
    c.post(f'/api/v1/pagos/{id_}/sincronizar',headers=cab)
    assert len([x for x in calls if x[0]=='/ventas'])==entregas
    assert bool(db.get(PedidoComercial,id_).acuse) is (not venta_pendiente)


def test_reserva_vencida_no_se_presenta_como_stock_apartado(conexion,monkeypatch):
    c,_,body,_,_,_,_=conexion
    id_=c.post('/api/v1/pagos',json=body).json()['datos']['pago']['id']
    futuro=datetime.now(timezone.utc)+timedelta(minutes=30)
    monkeypatch.setattr(integracion,'ahora',lambda:futuro)
    r=c.get(f'/api/v1/pagos/{id_}',headers={'Authorization':'Bearer '+body['clave_checkout']})
    assert r.status_code==200 and not r.json()['datos']['pagado']
    assert r.json()['datos']['comercial']['estado']=='RESERVA_VENCIDA'


def test_acuse_no_borra_revision_detectada_durante_la_entrega(conexion,db,monkeypatch):
    from checkout.pagos import aplicar_resultado
    c,_,body,_,_,_,_=conexion
    id_=c.post('/api/v1/pagos',json=body).json()['datos']['pago']['id']
    original=integracion.foodsave
    def respuesta_con_otro_pago(ruta,metodo='GET',cuerpo=None):
        if ruta=='/ventas':
            p=db.get(PagoTiendaPrueba,id_)
            aplicar_resultado(db,p,resultado(p,tid='segunda-aprobacion-durante-entrega'))
            integracion.preparar_salida(db,p)
            db.commit()
        return original(ruta,metodo,cuerpo)
    monkeypatch.setattr(integracion,'foodsave',respuesta_con_otro_pago)
    r=c.post(f'/api/v1/pagos/{id_}/verificar',headers={'Authorization':'Bearer '+body['clave_checkout']},json={'transaction_id':'primera-aprobacion'})
    assert r.status_code==200,r.text
    comercial=r.json()['datos']['comercial']
    assert comercial['estado']=='REVISION_REQUERIDA' and comercial['ticket']['numero']=='V-00000010'
    assert 'más de una' in comercial['mensaje']
