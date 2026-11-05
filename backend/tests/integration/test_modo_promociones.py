"""Configuración A01 y consumo real del monitor V03; sin transporte externo."""
from datetime import date
from sqlalchemy import select, func
from test_api_inicializacion_ventas import cliente  # noqa: F401
from test_planificacion_m02 import escenario  # noqa: F401
from test_operacion_integrada import configurar
from app.modules.inventario.modelos import LoteProducto
from app.modules.operaciones.modelos import PromocionOperacion, AvisoOperacion
from app.modules.operaciones.monitoreo import revisar


def test_configuracion_permisos_y_validacion(escenario):
    c,_,admin,op,_,_=escenario
    url='/api/v1/negocios/actual'
    assert c.get(url,headers=op).json()['datos']['modo_publicacion_promociones']=='REQUIERE_APROBACION'
    assert c.patch(url,headers=op,json={'modo_publicacion_promociones':'AUTOMATICO'}).status_code==403
    for valor in [None,'OTRO']:
        assert c.patch(url,headers=admin,json={'modo_publicacion_promociones':valor}).status_code==422
    r=c.patch(url,headers=admin,json={'modo_publicacion_promociones':'AUTOMATICO'})
    assert r.status_code==200,r.text
    assert r.json()['datos']['modo_envio_pedidos']=='REQUIERE_APROBACION'


def test_automatico_aprueba_solo_nuevas_validas_y_finaliza(escenario):
    c,sesiones,admin,_,_,ids=escenario;pid=ids['baguette']
    configurar(c,admin,pid)
    c.put('/api/v1/promociones/regla',headers=admin,json={'habilitada':True,'stock_umbral':2})
    with sesiones.begin() as s:
        lote=s.scalar(select(LoteProducto).where(LoteProducto.producto_id==pid))
        lote.fecha_limite_venta=lote.fecha_caducidad=date(2022,8,24)
        revisar(s,forzar=True)
        pendiente=s.scalar(select(PromocionOperacion));pendiente_id=pendiente.id
        assert pendiente.estado=='PENDIENTE'
    c.patch('/api/v1/negocios/actual',headers=admin,json={'modo_publicacion_promociones':'AUTOMATICO'})
    with sesiones.begin() as s:
        revisar(s,forzar=True)
        assert s.get(PromocionOperacion,pendiente_id).estado=='PENDIENTE'
        assert s.get(PromocionOperacion,pendiente_id).modo_publicacion=='REQUIERE_APROBACION'
        s.add_all([
            LoteProducto(producto_id=pid,codigo_lote='AUTO-VALIDO',lote_informado=True,saldo_disponible=10,fecha_ingreso=date(2022,8,24),fecha_limite_venta=date(2022,8,24),fecha_caducidad=date(2022,8,24)),
            LoteProducto(producto_id=pid,codigo_lote='AUTO-VENCIDO',lote_informado=True,saldo_disponible=10,fecha_limite_venta=date(2022,8,23),fecha_caducidad=date(2022,8,23)),
            LoteProducto(producto_id=pid,codigo_lote='AUTO-FUTURO',lote_informado=True,saldo_disponible=10,fecha_ingreso=date(2022,8,25),fecha_limite_venta=date(2022,8,25),fecha_caducidad=date(2022,8,25)),
        ]);s.flush()
        revisar(s,forzar=True)
        auto=s.scalar(select(PromocionOperacion).where(PromocionOperacion.estado=='APROBADA'))
        assert auto.modo_publicacion=='AUTOMATICO' and auto.decidido_por is None
        auto_id=auto.id;lote_id=auto.lote_id
        assert s.scalar(select(func.count()).select_from(PromocionOperacion).where(PromocionOperacion.estado=='APROBADA'))==1
        aviso=s.scalar(select(AvisoOperacion).where(AvisoOperacion.clave==f'promocion:{auto_id}'))
        assert aviso.datos['modo_publicacion']=='AUTOMATICO'
        revisar(s,forzar=True)
        assert s.scalar(select(func.count()).select_from(PromocionOperacion).where(PromocionOperacion.estado=='APROBADA'))==1
        # El mismo filtro comercial que consume la tienda reconoce la aprobación.
        from app.modules.comercio.catalogo import promociones_vigentes
        assert promociones_vigentes(s,[s.get(LoteProducto,lote_id)],date(2022,8,24))[lote_id].id==auto_id
        s.get(LoteProducto,lote_id).saldo_disponible=0;s.flush()
        revisar(s,forzar=True)
        assert s.get(PromocionOperacion,auto_id).estado=='FINALIZADA'
