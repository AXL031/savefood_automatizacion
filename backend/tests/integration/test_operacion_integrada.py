"""Recorrido operativo real por HTTP, inventario y auditoría; sin red externa."""
from datetime import datetime, timedelta, timezone, date
from decimal import Decimal
import pytest
from sqlalchemy import select, func
from test_api_inicializacion_ventas import cliente  # noqa: F401
from test_planificacion_m02 import escenario, solicitar
from test_compras_l02 import compra, generar
from app.modules.inventario.modelos import LoteIngrediente, LoteProducto, MovimientoInventario
from app.modules.operaciones.modelos import RegistroOperacion, SolicitudProveedor, AvisoOperacion


def configurar(c,admin,producto_id):
    r=c.put('/api/v1/operaciones/configuracion',headers=admin,json={'reloj':'ESCENARIO','fecha_escenario':'2022-08-24','hora_escenario':'17:15','habilitada':True,'producto_ids':[producto_id]})
    assert r.status_code==200,r.text


def test_tandas_venta_y_rollback_completo(escenario):
    c,sesiones,admin,operador,_,ids=escenario
    pid=ids['baguette'];configurar(c,admin,pid)
    plan=solicitar(escenario).json()['datos']['id']
    entrada={'clave_idempotencia':'produccion-primera','plan_id':plan,'fecha':'2022-08-24','lineas':[{'producto_id':pid,'cantidad':2,'fecha_caducidad':'2022-08-24'}]}
    r=c.post('/api/v1/operaciones/producciones',headers=operador,json=entrada)
    assert r.status_code==200,r.text
    id_=r.json()['datos']['id']
    assert c.post('/api/v1/operaciones/producciones',headers=operador,json=entrada).json()['datos']['id']==id_
    with sesiones() as s:
        assert s.scalar(select(LoteIngrediente.saldo_disponible))==Decimal('11499.500')
        assert s.scalar(select(func.count()).select_from(RegistroOperacion).where(RegistroOperacion.tipo=='PRODUCCION'))==1
    entrada['lineas'][0]['cantidad']=3
    assert c.post('/api/v1/operaciones/producciones',headers=operador,json=entrada).status_code==409
    entrada['clave_idempotencia']='segunda-tanda';entrada['lineas'][0]['cantidad']=4
    assert c.post('/api/v1/operaciones/producciones',headers=operador,json=entrada).status_code==200
    entrada['clave_idempotencia']='excede-tanda';entrada['lineas'][0]['cantidad']=1
    assert c.post('/api/v1/operaciones/producciones',headers=operador,json=entrada).status_code==409
    venta={'clave_idempotencia':'venta-operativa-1','fecha':'2022-08-24','lineas':[{'producto_id':pid,'cantidad':3}]}
    assert c.post('/api/v1/operaciones/ventas',headers=operador,json=venta).status_code==200
    assert c.post('/api/v1/operaciones/ventas',headers=operador,json=venta).status_code==200
    with sesiones() as s:
        antes=s.scalar(select(func.sum(LoteProducto.saldo_disponible)).where(LoteProducto.producto_id==pid))
        harina=s.scalar(select(LoteIngrediente.saldo_disponible))
        assert antes==7 and harina==Decimal('10497.500')
    venta['clave_idempotencia']='venta-no-alcanza';venta['lineas'][0]['cantidad']=100
    assert c.post('/api/v1/operaciones/ventas',headers=operador,json=venta).status_code==409
    with sesiones() as s:
        assert s.scalar(select(func.sum(LoteProducto.saldo_disponible)).where(LoteProducto.producto_id==pid))==antes
        assert s.scalar(select(RegistroOperacion).where(RegistroOperacion.clave=='venta-no-alcanza')) is None


def test_tienda_real_precio_stock_y_separacion_ml(escenario,monkeypatch):
    from pwdlib import PasswordHash
    from app.modules.tienda.modelos import ClienteTienda
    from app.modules.operaciones.modelos import CuentaClienteLocal
    from app.modules.ventas.modelos import VentaDiaria
    c,sesiones,admin,operador,_,ids=escenario;pid=ids['baguette'];configurar(c,admin,pid)
    with sesiones.begin() as s:
        cliente=ClienteTienda(google_sub='local:prueba',correo='cliente@example.com',nombre='Cliente')
        s.add(cliente);s.flush();s.add(CuentaClienteLocal(cliente_id=cliente.id,correo=cliente.correo,hash_contrasena=PasswordHash.recommended().hash('cliente-seguro-123')))
    monkeypatch.setenv('HABILITAR_CLIENTE_LOCAL','1')
    token=c.post('/api/v1/tienda/sesion/local',json={'correo':'cliente@example.com','contrasena':'cliente-seguro-123'}).json()['datos']['token']
    cab={'Authorization':'Bearer '+token}
    assert c.get('/api/v1/operaciones/resumen',headers=cab).status_code==401
    assert c.put(f'/api/v1/operaciones/productos/{pid}/ficha',headers=operador,json={'precio':'2.00'}).status_code==403
    assert c.put(f'/api/v1/operaciones/productos/{pid}/ficha',headers=admin,json={'precio':'2.00'}).status_code==200
    catalogo=c.get('/api/v1/tienda/catalogo').json()['datos']['productos']
    assert catalogo[0]['estado_stock']=='ULTIMAS_UNIDADES' and 'cantidad' not in catalogo[0]
    cot=c.post('/api/v1/tienda/carrito/cotizar',json={'lineas':[{'producto_id':pid,'cantidad':2}]}).json()['datos']
    assert cot['total']=='4.00'
    compra={'clave_idempotencia':'compra-tienda-1','lineas':[{'producto_id':pid,'cantidad':2,'subtotal_esperado':'4.00'}],
        'entrega':{'nombre_receptor':'Persona Prueba','celular':'999111222','direccion':'Calle de prueba 123','distrito':'Lima','referencia':''},'metodo_pago_simulado':'TARJETA_SIMULADA'}
    with sesiones() as s: ventas=s.scalar(select(func.sum(VentaDiaria.unidades_vendidas)))
    r=c.post('/api/v1/tienda/pedidos',headers=cab,json=compra);assert r.status_code==201,r.text
    assert c.post('/api/v1/tienda/pedidos',headers=cab,json=compra).json()['datos']['id']==r.json()['datos']['id']
    with sesiones() as s:
        assert s.scalar(select(func.sum(VentaDiaria.unidades_vendidas)))==ventas
        assert s.scalar(select(LoteProducto.saldo_disponible).where(LoteProducto.producto_id==pid))==2
    compra['tarjeta']='NO-DEBE-ACEPTARSE'
    assert c.post('/api/v1/tienda/pedidos',headers=cab,json=compra).status_code==422


def test_enlace_aceptacion_recepcion_parcial_y_aviso(compra):
    escenario,_,_,_=compra;c,sesiones,admin,operador,_,_=escenario
    plan=solicitar(escenario).json()['datos']['id'];pedido=generar(escenario,plan).json()['datos']['pedidos'][0]
    pid=pedido['id']
    with sesiones.begin() as s:
        from app.modules.compras.modelos import PedidoCompra
        s.get(PedidoCompra,pid).estado='ENVIADO'
    r=c.post(f'/api/v1/operaciones/pedidos/{pid}/enlace',headers=admin);assert r.status_code==200,r.text
    token=r.json()['datos']['url'].rsplit('/',1)[1];url=f'/api/v1/proveedor/pedidos/{token}'
    assert c.get(url).json()['datos']['estado']=='PENDIENTE'
    respuesta={'accion':'ACEPTAR','nombre':'Proveedor prueba','descripcion':'','entrega_comprometida':(datetime.now(timezone.utc)+timedelta(days=1)).isoformat()}
    assert c.post(url,json=respuesta).json()['datos']['estado']=='ACEPTADO'
    assert c.post(url,json=respuesta).status_code==200
    respuesta['accion']='RECHAZAR'
    assert c.post(url,json=respuesta).status_code==409
    entrada={'clave_idempotencia':'recepcion-con-diferencia','fecha_recepcion':'2022-08-24','motivo':'Una bolsa se encontraba rota','lineas':[{'linea_pedido_id':pedido['lineas'][0]['id'],'cantidad_compra':'3','fecha_caducidad':'2022-12-31'}]}
    r=c.post(f'/api/v1/operaciones/recepciones/{pid}',headers=operador,json=entrada);assert r.status_code==200,r.text
    assert c.post(f'/api/v1/operaciones/recepciones/{pid}',headers=operador,json=entrada).status_code==200
    avisos=c.get('/api/v1/operaciones/avisos',headers=admin).json()['datos'];incidencia=next(a for a in avisos if 'diferencias' in a['titulo'])
    assert incidencia['datos']['diferencias'][0]['aceptada']=='3'
    assert c.patch(f'/api/v1/operaciones/avisos/{incidencia["id"]}',headers=admin,json={'leido':True}).status_code==200
    avisos=c.get('/api/v1/operaciones/avisos',headers=admin).json()['datos']
    assert next(a for a in avisos if a['id']==incidencia['id'])['resolucion'] is None


def test_caducidad_del_enlace_y_alerta_idempotente(compra):
    from app.modules.operaciones.monitoreo import revisar
    from app.modules.compras.modelos import PedidoCompra
    escenario,_,_,_=compra;c,sesiones,admin,_,_,_=escenario
    pid=generar(escenario,solicitar(escenario).json()['datos']['id']).json()['datos']['pedidos'][0]['id']
    with sesiones.begin() as s:s.get(PedidoCompra,pid).estado='ENVIADO'
    r=c.post(f'/api/v1/operaciones/pedidos/{pid}/enlace',headers=admin)
    token=r.json()['datos']['url'].rsplit('/',1)[1]
    with sesiones.begin() as s:
        enlace=s.scalar(select(SolicitudProveedor));enlace.expira_en=datetime.now(timezone.utc)-timedelta(seconds=1)
        revisar(s);revisar(s)
    assert c.get(f'/api/v1/proveedor/pedidos/{token}').status_code==410
    with sesiones() as s:assert s.scalar(select(func.count()).select_from(AvisoOperacion).where(AvisoOperacion.clave.like('sin-respuesta:%')))==1


def test_monitor_diez_minutos_y_aprobacion(escenario):
    from app.modules.operaciones.monitoreo import revisar
    from app.modules.operaciones.modelos import PromocionOperacion
    c,sesiones,admin,operador,_,ids=escenario;pid=ids['baguette'];configurar(c,admin,pid)
    assert c.put('/api/v1/promociones/regla',headers=admin,json={'habilitada':True,'stock_umbral':2}).status_code==200
    with sesiones.begin() as s:
        l=s.scalar(select(LoteProducto).where(LoteProducto.producto_id==pid));l.fecha_limite_venta=l.fecha_caducidad=date(2022,8,24)
        ahora=datetime.now(timezone.utc)
        assert revisar(s,ahora)['evaluadas']==1
        assert revisar(s,ahora+timedelta(minutes=9))['revisada'] is False
        assert revisar(s,ahora+timedelta(minutes=10))['evaluadas']==0
        p=s.scalar(select(PromocionOperacion));promo=p.id
    assert c.post(f'/api/v1/operaciones/promociones/{promo}/decision',headers=operador,json={'aprobar':True}).status_code==403
    assert c.post(f'/api/v1/operaciones/promociones/{promo}/decision',headers=admin,json={'aprobar':True}).status_code==200
    assert c.put(f'/api/v1/operaciones/productos/{pid}/ficha',headers=admin,json={'precio':'2.00'}).status_code==200
    assert c.get('/api/v1/tienda/catalogo').json()['datos']['productos'][0]['promocion']['precio_promocional']=='1.60'


def test_ventas_concurrentes_no_sobrevenden_postgresql(escenario):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    from app.modules.operaciones.servicio import vender
    from app.modules.autenticacion.modelos import Usuario
    from app.core.errores import ErrorAPI
    c,sesiones,admin,_,_,ids=escenario;pid=ids['baguette']
    with sesiones() as s:
        if s.bind.dialect.name!='postgresql':pytest.skip('Concurrencia requiere PostgreSQL: E03_POSTGRES_TEST=1')
        uid=s.scalar(select(Usuario.id).where(Usuario.rol=='OPERADOR'))
    configurar(c,admin,pid);barrera=Barrier(2)
    def intentar(n):
        barrera.wait(timeout=10)
        try:
            with sesiones.begin() as s:vender(s,{'clave_idempotencia':f'concurrente-venta-{n}','fecha':'2022-08-24','lineas':[{'producto_id':pid,'cantidad':3}]},uid)
            return 'OK'
        except ErrorAPI as e:return e.codigo
    with ThreadPoolExecutor(max_workers=2) as pool:resultados=list(pool.map(intentar,[1,2]))
    assert sorted(resultados)==['OK','STOCK_INSUFICIENTE']
    with sesiones() as s:
        assert s.scalar(select(LoteProducto.saldo_disponible).where(LoteProducto.producto_id==pid))==1
        assert s.scalar(select(func.count()).select_from(RegistroOperacion).where(RegistroOperacion.tipo=='VENTA_INTERNA'))==1


def test_tandas_concurrentes_respetan_pendiente_postgresql(escenario):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    from app.modules.operaciones.servicio import producir
    from app.modules.autenticacion.modelos import Usuario
    from app.core.errores import ErrorAPI
    c,sesiones,admin,_,_,ids=escenario;pid=ids['baguette']
    with sesiones() as s:
        if s.bind.dialect.name!='postgresql':pytest.skip('Concurrencia requiere PostgreSQL: E03_POSTGRES_TEST=1')
        uid=s.scalar(select(Usuario.id).where(Usuario.rol=='OPERADOR'))
    configurar(c,admin,pid);plan=solicitar(escenario).json()['datos']['id'];barrera=Barrier(2)
    def intentar(n):
        barrera.wait(timeout=10)
        try:
            with sesiones.begin() as s:producir(s,{'clave_idempotencia':f'concurrente-tanda-{n}','plan_id':plan,'fecha':'2022-08-24','lineas':[{'producto_id':pid,'cantidad':4,'fecha_caducidad':'2022-08-24'}]},uid)
            return 'OK'
        except ErrorAPI as e:return e.codigo
    with ThreadPoolExecutor(max_workers=2) as pool:resultados=list(pool.map(intentar,[1,2]))
    assert sorted(resultados)==['EXCEDE_PLAN','OK']
    with sesiones() as s:
        assert s.scalar(select(func.sum(LoteProducto.saldo_disponible)).where(LoteProducto.producto_id==pid))==8
