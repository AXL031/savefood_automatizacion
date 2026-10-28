"""Tienda por HTTP, misma caja/stock; datos ficticios, nunca Payme o tienda externa."""
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from decimal import Decimal
from uuid import uuid4
import pytest
from sqlalchemy import select, func
from test_entradas_productos import inv, cliente, HOY
from app.modules.inventario.modelos import LoteProducto, MovimientoInventario
from app.modules.comercio.modelos import ReservaTienda, AsignacionReserva, EventoPublicacion
from app.modules.ventas.modelos_caja import TicketVenta, LineaTicketVenta
from app.modules.ventas.modelos import VentaDiaria
from app.modules.ventas import caja


@pytest.fixture
def comercio(inv,monkeypatch):
    monkeypatch.setenv('TIENDA_INTEGRACION_HABILITADA','1')
    monkeypatch.setenv('TIENDA_INTEGRACION_TOKEN','token-integracion-privado-falso-20261028')
    c,sesiones,admin,op,ids=inv
    with sesiones.begin() as s:
        lotes=[]
        for codigo,n,ingreso,limite in [('FRESCO-A',3,28,29),('FRESCO-B',4,28,30),('FUTURO',100,29,30)]:
            l=LoteProducto(producto_id=ids[0],codigo_lote=codigo,lote_informado=True,saldo_disponible=n,
                fecha_ingreso=date(2026,10,ingreso),fecha_limite_venta=date(2026,10,limite),fecha_caducidad=date(2026,10,30))
            s.add(l);s.flush();lotes.append(l.id)
    r=c.put(f'/api/v1/tienda-admin/productos/{ids[0]}',headers=admin,json={
        'version_actual':0,'publicado':True,'categoria':'panes','descripcion':'Pan QA','presentacion':'Unidad','imagen':''})
    assert r.status_code==200,r.text
    origen=c.get('/api/v1/tienda-admin/estado',headers=op).json()['datos']['origen']
    return inv,{'Authorization':'Bearer token-integracion-privado-falso-20261028'},origen,lotes


def consulta(esc,n=5):
    return {'origen':esc[2],'lineas':[{'producto_id':esc[0][4][0],'cantidad':n}]}


def reservar(esc,n=5,clave=None):
    c=esc[0][0];cab=esc[1]
    cot=c.post('/api/v1/integracion-tienda/cotizar',headers=cab,json=consulta(esc,n))
    assert cot.status_code==200,cot.text
    body={**consulta(esc,n),'cotizacion_hash':cot.json()['datos']['huella'],'clave_idempotencia':clave or str(uuid4())}
    r=c.post('/api/v1/integracion-tienda/reservas',headers=cab,json=body)
    return r,body


def venta(esc,reserva,body):
    return {'origen':esc[2],'reserva_id':reserva['id'],'evento_id':str(uuid4()),'pedido_externo':body['clave_idempotencia'],
        'pago':{'proveedor':'PAYME','ambiente':'PRUEBAS','verificado':True,'operacion':'123456789012',
                'transaccion':'transaccion-qa-001','metodo':'CARD','monto':reserva['cotizacion']['total'],'moneda':'PEN'}}


def test_reserva_venta_idempotente_mismo_stock_sin_historico(comercio):
    esc=comercio;(c,sesiones,admin,op,ids),cab,_,lotes=esc
    r,body=reservar(esc)
    assert r.status_code==201,r.text
    reserva=r.json()['datos']
    assert c.post('/api/v1/integracion-tienda/reservas',headers=cab,json=body).json()==r.json()
    cat=c.get('/api/v1/ventas/catalogo',headers=op).json()['datos']['productos']
    assert cat[0]['disponible']==2 and cat[0]['reservado']==5
    with sesiones() as s:
        assert s.get(LoteProducto,lotes[0]).saldo_disponible==3
        assert s.scalar(select(func.count()).select_from(MovimientoInventario).where(MovimientoInventario.tipo=='VENTA'))==0
    pedido=venta(esc,reserva,body)
    r=c.post('/api/v1/integracion-tienda/ventas',headers=cab,json=pedido)
    assert r.status_code==201,r.text
    assert c.post('/api/v1/integracion-tienda/ventas',headers=cab,json=pedido).json()==r.json()
    with sesiones() as s:
        t=s.scalar(select(TicketVenta));assert t.canal=='TIENDA' and t.usuario_id is None and t.total==Decimal('12.50')
        assert s.get(LoteProducto,lotes[0]).saldo_disponible==0 and s.get(LoteProducto,lotes[1]).saldo_disponible==2
        assert s.get(LoteProducto,lotes[2]).saldo_disponible==100
        assert s.scalar(select(ReservaTienda)).estado=='CONSUMIDA'
        assert s.scalar(select(func.count()).select_from(VentaDiaria))==0
    pedido['pago']['monto']='0.01'
    assert c.post('/api/v1/integracion-tienda/ventas',headers=cab,json=pedido).status_code==409
    assert c.get('/api/v1/ventas/tickets',headers=op).json()['metadatos']['total']==1


def test_presencial_y_ajuste_no_consumen_reserva(comercio):
    esc=comercio;(c,sesiones,admin,op,ids),cab,_,lotes=esc
    r,body=reservar(esc);assert r.status_code==201,r.text
    assert c.post('/api/v1/ventas/cotizaciones',headers=op,json={
        'clave_idempotencia':'presencial-no-disponible','lineas':[{'producto_id':ids[0],'cantidad':3}]}).status_code==409
    r=c.post('/api/v1/inventario/ajustes',headers=admin,json={'tipo':'producto','lote_id':lotes[0],'delta':'-1',
        'motivo':'Proteger reserva','clave_operacion':'ajuste-reservado-001','efectivo_en_demo':'2026-10-28T10:00:00'})
    assert r.status_code==409,r.text
    assert r.json()['error']['codigo']=='STOCK_RESERVADO'
    cot=c.post('/api/v1/ventas/cotizaciones',headers=op,json={
        'clave_idempotencia':'presencial-disponible','lineas':[{'producto_id':ids[0],'cantidad':2}]}).json()['datos']
    r=c.post('/api/v1/ventas/tickets',headers=op,json={'clave_idempotencia':'venta-presencial-junto-tienda','cotizacion_id':cot['id'],
        'total_revisado':cot['total'],'cobro_presencial':{'medio':'EFECTIVO','importe_recibido':'5.00'}})
    assert r.status_code==201,r.text
    reserva=c.get('/api/v1/integracion-tienda/reservas/'+c.post('/api/v1/integracion-tienda/reservas',headers=cab,json=body).json()['datos']['id'],headers=cab).json()['datos']
    assert c.post('/api/v1/integracion-tienda/ventas',headers=cab,json=venta(esc,reserva,body)).status_code==201
    assert c.get('/api/v1/ventas/catalogo',headers=op).json()['datos']['productos'][0]['disponible']==0


def test_caducidad_liberacion_y_pago_tardio(comercio,monkeypatch):
    esc=comercio;(c,sesiones,admin,op,ids),cab,_,_=esc
    r,body=reservar(esc);reserva=r.json()['datos']
    monkeypatch.setattr(caja,'ahora',lambda:HOY+timedelta(minutes=21))
    assert c.get('/api/v1/integracion-tienda/reservas/'+reserva['id'],headers=cab).json()['datos']['estado']=='EXPIRADA'
    assert c.get('/api/v1/ventas/catalogo',headers=op).json()['datos']['productos'][0]['disponible']==7
    r=c.post('/api/v1/integracion-tienda/ventas',headers=cab,json=venta(esc,reserva,body))
    assert r.status_code==409 and r.json()['error']['codigo']=='RESERVA_VENCIDA'
    r=c.post('/api/v1/integracion-tienda/reservas/'+reserva['id']+'/liberar',headers=cab,json={'motivo':'EXPIRADO'})
    assert r.status_code==200 and r.json()['datos']['estado']=='LIBERADA'
    with sesiones() as s:assert s.scalar(select(func.count()).select_from(TicketVenta))==0


def test_precio_cambiado_y_permisos_no_duplican(comercio):
    esc=comercio;(c,sesiones,admin,op,ids),cab,origen,_=esc
    cot=c.post('/api/v1/integracion-tienda/cotizar',headers=cab,json=consulta(esc)).json()['datos']
    assert c.get('/api/v1/integracion-tienda/stock',headers=admin).status_code==401
    assert c.get('/api/v1/tienda-admin/productos',headers=cab).status_code==401
    assert c.put(f'/api/v1/tienda-admin/productos/{ids[0]}',headers=op,json={'version_actual':1,'publicado':False}).status_code==403
    assert c.put(f'/api/v1/ventas/precios/{ids[0]}',headers=admin,json={
        'clave_idempotencia':'cambiar-precio-tienda','precio':'3.00','version_actual':1}).status_code==200
    r=c.post('/api/v1/integracion-tienda/reservas',headers=cab,json={**consulta(esc),
        'clave_idempotencia':str(uuid4()),'cotizacion_hash':cot['huella']})
    assert r.status_code==409 and r.json()['error']['codigo']=='COTIZACION_CAMBIO'
    with sesiones() as s:assert s.scalar(select(func.count()).select_from(ReservaTienda))==0


def test_promocion_solo_unidades_del_lote_y_precio_conservado(comercio):
    from app.modules.operaciones.modelos import PromocionOperacion
    from app.modules.promociones.modelos import ReglaPromocionDemo
    esc=comercio;(c,sesiones,admin,op,ids),cab,_,lotes=esc
    assert c.put('/api/v1/promociones/regla',headers=admin,json={'habilitada':True}).status_code==200
    with sesiones.begin() as s:
        regla=s.scalar(select(ReglaPromocionDemo))
        s.add(PromocionOperacion(clave='promo-publicada-qa',lote_id=lotes[0],regla_id=regla.id,estado='APROBADA',
                                descuento=20,motivo='Promoción de tres unidades',fecha=date(2026,10,28),decidido_por=1))
    r,body=reservar(esc);assert r.status_code==201,r.text
    reserva=r.json()['datos'];assert reserva['cotizacion']['total']=='11.00'
    assert reserva['cotizacion']['lineas'][0]['unidades_con_promocion']==3
    r=c.post('/api/v1/integracion-tienda/ventas',headers=cab,json=venta(esc,reserva,body));assert r.status_code==201,r.text
    with sesiones() as s:
        l=s.scalar(select(LineaTicketVenta));assert l.precio==Decimal('2.50') and l.subtotal==Decimal('11.00')
        assert [x['cantidad'] for x in l.segmentos]==[3,2]


def test_publicacion_durable_reintenta_misma_version(comercio,monkeypatch):
    from app.modules.comercio.publicaciones import despachar
    esc=comercio;(c,sesiones,admin,op,ids),_,_,_=esc
    llamadas=[]
    def error(datos):llamadas.append(datos);raise TimeoutError()
    despachar(sesiones,error)
    with sesiones() as s:assert s.scalar(select(EventoPublicacion)).estado=='PENDIENTE'
    monkeypatch.setattr(caja,'ahora',lambda:HOY+timedelta(minutes=1))
    despachar(sesiones,lambda datos:llamadas.append(datos))
    assert llamadas[0]==llamadas[1]
    with sesiones() as s:assert s.scalar(select(EventoPublicacion)).estado=='CONFIRMADO'
    assert despachar(sesiones,lambda _:pytest.fail('No reenviar confirmado'))==0


def test_reservas_concurrentes_y_ultima_unidad_postgresql(comercio):
    from threading import Barrier
    esc=comercio;(c,sesiones,admin,op,ids),cab,_,_=esc
    with sesiones() as s:
        if s.bind.dialect.name!='postgresql':pytest.skip('Requiere PostgreSQL para locks reales')
    cot=c.post('/api/v1/integracion-tienda/cotizar',headers=cab,json=consulta(esc)).json()['datos']
    barrera=Barrier(2)
    def intentar(_):
        barrera.wait(timeout=15)
        return c.post('/api/v1/integracion-tienda/reservas',headers=cab,json={**consulta(esc),
            'clave_idempotencia':str(uuid4()),'cotizacion_hash':cot['huella']}).status_code
    with ThreadPoolExecutor(2) as pool:res=list(pool.map(intentar,[1,2]))
    assert sorted(res)==[201,409]
    with sesiones() as s:assert s.scalar(select(func.count()).select_from(ReservaTienda))==1
