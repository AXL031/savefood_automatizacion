"""Caja real por HTTP y stock compartido. SQLite temporal o E03_POSTGRES_TEST=1 (esquemas aislados)."""
import os
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from decimal import Decimal
import pytest
from sqlalchemy import select, func
from sqlalchemy.orm import sessionmaker
from test_api_inicializacion_ventas import cliente, cabecera, token
from app.core.base_datos import obtener_sesion
from app.core.errores import ErrorAPI
from app.modules.productos.modelos import Producto
from app.modules.inventario.modelos import LoteProducto, MovimientoInventario
from app.modules.ventas.modelos import VentaDiaria
from app.modules.ventas.modelos_caja import TicketVenta, CotizacionVenta, PrecioVenta
from app.modules.ventas import caja

FECHA = datetime(2026,10,26,15,tzinfo=timezone.utc)


@pytest.fixture
def pos(cliente, monkeypatch):
    monkeypatch.setattr(caja, "ahora", lambda: FECHA)
    admin = cabecera(token(cliente,"admin@example.com","clave-segura-admin"))
    operador = cabecera(token(cliente,"operador@example.com","clave-segura-operador"))
    with contextmanager(cliente.app.dependency_overrides[obtener_sesion])() as s:
        sesiones = sessionmaker(bind=s.get_bind(), expire_on_commit=False)
    with sesiones.begin() as s:
        p = Producto(codigo="PAN", nombre="Pan de caja", activo=True)
        b = Producto(codigo="OTRO", nombre="Sin stock", activo=True)
        s.add_all([p,b]); s.flush()
        s.add_all([LoteProducto(producto_id=p.id,codigo_lote="TARDE",lote_informado=True,saldo_disponible=3,
            fecha_limite_venta=FECHA.date()+timedelta(days=1),fecha_caducidad=FECHA.date()+timedelta(days=3)),
            LoteProducto(producto_id=p.id,codigo_lote="PRIMERO",lote_informado=True,saldo_disponible=2,
            fecha_limite_venta=FECHA.date(),fecha_caducidad=FECHA.date()+timedelta(days=2))])
        id_, otro = p.id,b.id
    assert cliente.put(f"/api/v1/ventas/precios/{id_}",headers=admin,
        json={"clave_idempotencia":"precio-inicial","precio":"2.50","version_actual":0}).status_code==200
    return cliente,sesiones,admin,operador,id_,otro


def cot(pos, cantidad=3, clave="cotizacion-inicial", headers=None):
    c,_,_,op,id_,_ = pos
    return c.post("/api/v1/ventas/cotizaciones",headers=headers or op,
                  json={"clave_idempotencia":clave,"lineas":[{"producto_id":id_,"cantidad":cantidad}]})


def solicitud(cotizacion, clave="venta-inicial-001", medio="EFECTIVO", recibido="10.00"):
    return {"clave_idempotencia":clave,"cotizacion_id":cotizacion["id"],"total_revisado":cotizacion["total"],
            "cobro_presencial":{"medio":medio,"importe_recibido":recibido}}


def saldos(pos):
    with pos[1]() as s:
        return dict(s.execute(select(LoteProducto.codigo_lote,LoteProducto.saldo_disponible)).all())


def test_cotizar_registrar_repetir_recuperar_anular_y_preservar_historico(pos, monkeypatch):
    c,sesiones,admin,op,id_,_ = pos
    original = saldos(pos)
    q = cot(pos).json()["datos"]
    assert saldos(pos)==original and q["total"]=="7.50"
    assert cot(pos).status_code==200
    assert cot(pos,cantidad=1).status_code==409
    body=solicitud(q)
    r=c.post("/api/v1/ventas/tickets",headers=op,json=body)
    assert r.status_code==201,r.text
    t=r.json()["datos"]
    assert t["total"]=="7.50" and t["cobro"]["vuelto"]=="2.50"
    assert saldos(pos)=={"TARDE":2,"PRIMERO":0}
    assert len(t["lineas"][0]["salidas"])==2
    monkeypatch.setattr(caja,"ahora",lambda:FECHA+timedelta(minutes=10))
    assert c.post("/api/v1/ventas/tickets",headers=op,json=body).json()["datos"]==t
    assert c.get("/api/v1/ventas/tickets/por-clave/venta-inicial-001",headers=op).json()["datos"]==t
    assert c.get("/api/v1/ventas/tickets/por-clave/venta-inicial-001",headers=admin).status_code==404
    assert c.post("/api/v1/ventas/tickets",headers=op,json={**body,"total_revisado":"1.00"}).status_code==409
    anular={"clave_idempotencia":"anular-venta-001","motivo":"Cobro registrado por error","mercancia_no_entregada":True}
    ruta=f"/api/v1/ventas/tickets/{t['id']}/anular"
    assert c.post(ruta,headers=op,json=anular).status_code==403
    a=c.post(ruta,headers=admin,json=anular)
    assert a.status_code==200,a.text
    assert saldos(pos)==original
    assert c.post(ruta,headers=admin,json=anular).json()==a.json()
    assert c.post(ruta,headers=admin,json={**anular,"motivo":"Otro motivo"}).status_code==409
    with sesiones() as s:
        assert s.scalar(select(func.count()).select_from(TicketVenta))==1
        assert s.scalar(select(func.count()).select_from(MovimientoInventario))==4
        assert s.scalar(select(func.count()).select_from(VentaDiaria))==0
    lista=c.get("/api/v1/ventas/tickets?estado=ANULADA",headers=op).json()
    assert lista["metadatos"]["total"]==1 and lista["metadatos"]["importe_confirmado"]=="0.00"
    assert c.get("/api/v1/ventas",headers=op).status_code==200


def test_permisos_precios_cotizacion_ajena_y_versiones(pos):
    c,_,admin,op,id_,_ = pos
    ruta=f"/api/v1/ventas/precios/{id_}"
    p={"clave_idempotencia":"nuevo-precio-001","precio":"3.00","version_actual":1}
    assert c.get("/api/v1/ventas/catalogo").status_code==401
    assert c.put(ruta,headers=op,json=p).status_code==403
    q=cot(pos).json()["datos"]
    assert c.post("/api/v1/ventas/tickets",headers=admin,json=solicitud(q)).status_code==404
    assert c.put(ruta,headers=admin,json=p).json()["datos"]["version"]==2
    assert c.put(ruta,headers=admin,json=p).json()["datos"]["version"]==2
    assert c.post("/api/v1/ventas/tickets",headers=op,json=solicitud(q)).status_code==409
    assert saldos(pos)=={"TARDE":3,"PRIMERO":2}
    assert c.put(ruta,headers=admin,json={**p,"clave_idempotencia":"precio-atrasado"}).status_code==409


@pytest.mark.parametrize("cambio",[
    {"lineas":[{"producto_id":1,"cantidad":True}]},
    {"lineas":[{"producto_id":1,"cantidad":0}]},
    {"lineas":[{"producto_id":1,"cantidad":1},{"producto_id":1,"cantidad":2}]},
    {"canal":"TIENDA"}, {"fecha_local":"2022-08-24"}, {"lineas":[]},
])
def test_cotizacion_rechaza_payload_invalido(pos,cambio):
    c,_,_,op,id_,_=pos
    body={"clave_idempotencia":"cot-invalida-001","lineas":[{"producto_id":id_,"cantidad":1}],**cambio}
    assert c.post("/api/v1/ventas/cotizaciones",headers=op,json=body).status_code==422


@pytest.mark.parametrize("valor",["0.00","-1.00","NaN","1.001",1.25,True,"1000000.00"])
def test_dinero_invalido(pos,valor):
    c,_,admin,_,id_,_=pos
    assert c.put(f"/api/v1/ventas/precios/{id_}",headers=admin,json={"clave_idempotencia":"precio-invalido","precio":valor,"version_actual":1}).status_code==422


def test_cotizacion_vencida_doble_clave_y_cobro_exacto(pos,monkeypatch):
    c,_,_,op,_,_=pos
    q=cot(pos,cantidad=1).json()["datos"]
    assert c.post("/api/v1/ventas/tickets",headers=op,json=solicitud(q,medio="YAPE",recibido="10.00")).status_code==422
    body=solicitud(q,medio="YAPE",recibido="2.50")
    assert c.post("/api/v1/ventas/tickets",headers=op,json=body).status_code==201
    assert c.post("/api/v1/ventas/tickets",headers=op,json={**body,"clave_idempotencia":"otra-clave-venta"}).status_code==409
    q=cot(pos,cantidad=1,clave="cot-otra-venta").json()["datos"]
    monkeypatch.setattr(caja,"ahora",lambda:FECHA+timedelta(minutes=6))
    assert c.post("/api/v1/ventas/tickets",headers=op,json=solicitud(q,clave="venta-ya-vencida")).status_code==409


def test_stock_desconocido_vencido_y_caducidad_nula(pos):
    c,sesiones,admin,op,id_,otro=pos
    assert cot(pos,cantidad=6).status_code==409
    with sesiones.begin() as s:
        for l in s.scalars(select(LoteProducto)):
            l.fecha_limite_venta=FECHA.date()-timedelta(days=1)
    assert cot(pos).status_code==409
    with sesiones.begin() as s:
        for l in s.scalars(select(LoteProducto)):
            l.fecha_limite_venta=FECHA.date(); l.fecha_caducidad=None
    assert cot(pos).status_code==201
    catalogo=c.get("/api/v1/ventas/catalogo",headers=op).json()["datos"]["productos"]
    assert next(p for p in catalogo if p["id"]==id_)["aviso_caducidad"]
    assert next(p for p in catalogo if p["id"]==otro)["disponible"] is None


def test_fallo_despues_de_una_salida_revierte_ticket_y_todos_los_saldos(pos,monkeypatch):
    from app.modules.inventario import ventas
    c,sesiones,_,op,_,_=pos
    q=cot(pos).json()["datos"]
    original=ventas._aplicar
    veces=0
    def fallar(*args,**kwargs):
        nonlocal veces
        veces+=1
        if veces==2:raise ErrorAPI(503,"FALLO_CONTROLADO","Fixture de rollback.")
        return original(*args,**kwargs)
    monkeypatch.setattr(ventas,"_aplicar",fallar)
    assert c.post("/api/v1/ventas/tickets",headers=op,json=solicitud(q)).status_code==503
    assert saldos(pos)=={"TARDE":3,"PRIMERO":2}
    with sesiones() as s:
        assert s.scalar(select(func.count()).select_from(TicketVenta))==0
        assert s.scalar(select(func.count()).select_from(MovimientoInventario))==0


def test_confirmacion_revalida_stock_y_no_deja_venta_parcial(pos):
    c,sesiones,_,op,_,_=pos
    q=cot(pos).json()["datos"]
    with sesiones.begin() as s:
        for l in s.scalars(select(LoteProducto)):l.saldo_disponible=0
    assert c.post("/api/v1/ventas/tickets",headers=op,json=solicitud(q)).status_code==409
    with sesiones() as s: assert s.scalar(select(func.count()).select_from(TicketVenta))==0


def test_carrito_varios_productos_paginacion_y_anulacion_no_revende_lote_vencido(pos,monkeypatch):
    c,sesiones,admin,op,id_,otro=pos
    with sesiones.begin() as s:
        s.add(LoteProducto(producto_id=otro,codigo_lote="OTRO-HOY",lote_informado=True,saldo_disponible=4,
            fecha_limite_venta=FECHA.date(),fecha_caducidad=FECHA.date()))
    assert c.put(f"/api/v1/ventas/precios/{otro}",headers=admin,json={"clave_idempotencia":"precio-otro-001","precio":"1.15","version_actual":0}).status_code==200
    r=c.post("/api/v1/ventas/cotizaciones",headers=op,json={"clave_idempotencia":"carrito-varios-001","lineas":[{"producto_id":id_,"cantidad":1},{"producto_id":otro,"cantidad":3}]})
    assert r.status_code==201,r.text
    q=r.json()["datos"];assert q["total"]=="5.95"
    t=c.post("/api/v1/ventas/tickets",headers=op,json=solicitud(q)).json()["datos"]
    lista=c.get(f"/api/v1/ventas/tickets?producto_id={otro}&limite=1",headers=op).json()
    assert lista["metadatos"]["total"]==1 and lista["metadatos"]["importe_confirmado"]=="5.95"
    assert lista["datos"][0]["unidades"]==4
    assert c.get("/api/v1/ventas/tickets?desde=2026-10-27&hasta=2026-10-26",headers=op).status_code==422
    monkeypatch.setattr(caja,"ahora",lambda:FECHA+timedelta(days=5))
    assert c.post(f"/api/v1/ventas/tickets/{t['id']}/anular",headers=admin,json={"clave_idempotencia":"anular-varios-001","motivo":"Mercancía no entregada","mercancia_no_entregada":True}).status_code==200
    cat=c.get("/api/v1/ventas/catalogo",headers=op).json()["datos"]["productos"]
    assert all(p["disponible"]==0 for p in cat)


@pytest.mark.parametrize("misma_clave",[False,True])
def test_concurrencia_ultimo_stock_y_reentrega_pg(pos,misma_clave):
    if os.getenv("E03_POSTGRES_TEST")!="1":pytest.skip("Bloqueos requieren PostgreSQL aislado")
    c,sesiones,_,op,_,_=pos
    q=cot(pos,cantidad=5).json()["datos"]
    q2=q if misma_clave else cot(pos,cantidad=5,clave="cotizacion-segunda").json()["datos"]
    solicitudes=[solicitud(q,clave="venta-concurrente-0",recibido="20.00"),solicitud(q2,clave="venta-concurrente-0" if misma_clave else "venta-concurrente-1",recibido="20.00")]
    with ThreadPoolExecutor(max_workers=2) as pool:
        respuestas=list(pool.map(lambda body:c.post("/api/v1/ventas/tickets",headers=op,json=body),solicitudes))
    assert sorted(r.status_code for r in respuestas)==([200,201] if misma_clave else [201,409]),[r.text for r in respuestas]
    assert sum(saldos(pos).values())==0
    with sesiones() as s:assert s.scalar(select(func.count()).select_from(TicketVenta))==1
