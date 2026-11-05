"""Programación puntual, retirada comercial, revalidación y motor; sin red externa."""
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from types import SimpleNamespace
import pytest
from sqlalchemy import select, func
from test_api_inicializacion_ventas import cliente  # noqa: F401
from test_planificacion_m02 import escenario  # noqa: F401
from app.modules.operaciones import promociones_programadas as servicio
from app.modules.operaciones.modelos import PromocionOperacion, AvisoOperacion
from app.modules.operaciones.monitoreo import revisar
from app.modules.inventario.modelos import LoteProducto
from app.modules.automatizaciones.modelos import EjecucionAutomatizacion,ProgramacionDemo
from app.modules.promociones.servicio import evaluar_programada
from app.modules.ventas import caja


@pytest.fixture
def preparada(escenario,monkeypatch):
    c,sesiones,admin,op,_,ids=escenario;pid=ids['baguette']
    base=(datetime.now(ZoneInfo('America/Lima'))+timedelta(days=1)).replace(hour=12,minute=0,second=0,microsecond=0).astimezone(timezone.utc)
    reloj={'ahora':base}
    monkeypatch.setattr(servicio,'ahora',lambda:reloj['ahora'])
    monkeypatch.setattr(caja,'ahora',lambda:reloj['ahora'])
    assert c.put('/api/v1/operaciones/configuracion',headers=admin,json={'reloj':'ACTUAL','producto_ids':[pid],'habilitada':True}).status_code==200
    assert c.put('/api/v1/promociones/regla',headers=admin,json={'habilitada':True,'hora_revision':'00:00','hora_cierre':'23:59','stock_umbral':2}).status_code==200
    assert c.put(f'/api/v1/ventas/precios/{pid}',headers=admin,json={'clave_idempotencia':'precio-programacion-fixture','precio':'10.00','version_actual':0}).status_code==200
    assert c.put(f'/api/v1/tienda-admin/productos/{pid}',headers=admin,json={'version_actual':0,'publicado':True,'categoria':'panes','descripcion':'QA','presentacion':'Unidad','imagen':''}).status_code==200
    with sesiones.begin() as s:
        lote=s.scalar(select(LoteProducto).where(LoteProducto.producto_id==pid))
        lote.fecha_ingreso=lote.fecha_limite_venta=lote.fecha_caducidad=base.astimezone(ZoneInfo('America/Lima')).date()
        s.flush();revisar(s,base,forzar=True)
        p=s.scalar(select(PromocionOperacion).where(PromocionOperacion.lote_id==lote.id));p.estado='APROBADA'
        promo,lote_id=p.id,lote.id
    entrada={'clave_idempotencia':'programacion-fixture-001','fecha_hora_local':(base+timedelta(minutes=2)).astimezone(ZoneInfo('America/Lima')).replace(tzinfo=None).isoformat(),'modo_publicacion':'AUTOMATICO'}
    return c,sesiones,admin,op,promo,lote_id,reloj,entrada,pid


def programar(e):
    c,_,admin,_,p,_,_,entrada,_=e
    r=c.post(f'/api/v1/operaciones/promociones/{p}/programar',headers=admin,json=entrada)
    assert r.status_code==200,r.text
    return r.json()['datos']['programacion_id']


def ejecutar(e,programacion):
    _,sesiones,_,_,_,_,reloj,_,_=e
    reloj['ahora']+=timedelta(minutes=3)
    with sesiones.begin() as s:
        tarea=s.scalar(select(EjecucionAutomatizacion).where(EjecucionAutomatizacion.programacion_id==programacion))
        return evaluar_programada(s,SimpleNamespace(id=tarea.id,datos_entrada=tarea.datos_entrada_json))


def publicado(e):
    from app.modules.comercio.catalogo import catalogo_publicado
    with e[1]() as s:return next(p for p in catalogo_publicado(s)['productos'] if p['id']==e[8])['promocion']


def test_retiro_espera_publicacion_snapshot_y_reentrega(preparada):
    e=preparada;c,sesiones,admin,_,p,_,reloj,entrada,_=e
    assert publicado(e)
    prog=programar(e);assert publicado(e) is None
    assert programar(e)==prog
    r=c.post(f'/api/v1/operaciones/promociones/{p}/programar',headers=admin,json={**entrada,'modo_publicacion':'REQUIERE_APROBACION'})
    assert r.status_code==409
    # El monitor no debe adelantar la promoción puntual ni crear otra para el lote.
    with sesiones.begin() as s:
        revisar(s,reloj['ahora'],forzar=True)
        assert s.get(PromocionOperacion,p).estado=='PROGRAMADA'
        assert s.scalar(select(func.count()).select_from(PromocionOperacion).where(PromocionOperacion.lote_id==e[5]))==1
    c.patch('/api/v1/negocios/actual',headers=admin,json={'modo_publicacion_promociones':'REQUIERE_APROBACION'})
    salida=ejecutar(e,prog);assert salida['estado']=='APROBADA'
    assert publicado(e)['id']==p
    assert ejecutar(e,prog)==salida
    with sesiones() as s:
        assert s.get(PromocionOperacion,p).modo_publicacion=='AUTOMATICO'
        assert s.scalar(select(func.count()).select_from(AvisoOperacion).where(AvisoOperacion.clave==f'promocion-programada:{prog}'))==1


def test_permisos_fecha_y_cancelacion_sin_reactivar(preparada):
    e=preparada;c,sesiones,admin,op,p,_,_,entrada,_=e
    url=f'/api/v1/operaciones/promociones/{p}'
    assert c.post(url+'/programar',headers=op,json=entrada).status_code==403
    assert c.post(url+'/programar',headers=admin,json={**entrada,'fecha_hora_local':(e[6]['ahora']-timedelta(minutes=1)).astimezone(ZoneInfo('America/Lima')).replace(tzinfo=None).isoformat()}).status_code==422
    prog=programar(e)
    assert c.post(url+'/cancelar-programacion',headers=admin,json={'programacion_id':prog+100}).status_code==409
    for _ in range(2):
        r=c.post(url+'/cancelar-programacion',headers=admin,json={'programacion_id':prog});assert r.status_code==200,r.text
    assert publicado(e) is None
    with sesiones() as s:
        assert s.get(PromocionOperacion,p).estado=='PENDIENTE'
        assert s.get(ProgramacionDemo,prog).estado=='CANCELADA'


@pytest.mark.parametrize('cambio',['agotado','vencido','manual'])
def test_revalida_stock_vigencia_y_modo(preparada,cambio):
    e=preparada
    if cambio=='manual':e[7]['modo_publicacion']='REQUIERE_APROBACION'
    prog=programar(e)
    with e[1].begin() as s:
        lote=s.get(LoteProducto,e[5])
        if cambio=='agotado':lote.saldo_disponible=0
        if cambio=='vencido':lote.fecha_ingreso=lote.fecha_limite_venta=lote.fecha_caducidad=lote.fecha_caducidad-timedelta(days=1)
    assert ejecutar(e,prog)['estado']==('PENDIENTE' if cambio=='manual' else 'NO_APLICA')
    assert publicado(e) is None


def test_motor_existente_completa_la_tarea(preparada,monkeypatch):
    from app.workers import motor
    e=preparada;prog=programar(e);e[6]['ahora']+=timedelta(minutes=3)
    monkeypatch.setattr(motor,'SessionLocal',e[1]);monkeypatch.setattr(motor,'_ahora',lambda:e[6]['ahora'])
    with e[1]() as s:tid=s.scalar(select(EjecucionAutomatizacion.id).where(EjecucionAutomatizacion.programacion_id==prog))
    mensajes=[];motor.despachar_pendientes(lambda id_,token:mensajes.append((id_,token)),ahora=e[6]['ahora'])
    id_,token=next(m for m in mensajes if m[0]==tid)
    assert motor.ejecutar(id_,token)['resultado']=='COMPLETADA'
    assert motor.ejecutar(id_,token)['resultado']=='IGNORADA'
    assert publicado(e)
