"""Entrada HTTP completa, stock compartido con caja y concurrencia PostgreSQL aislada."""
import os
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, date, timezone
import pytest
from sqlalchemy import select, func
from sqlalchemy.orm import sessionmaker
from test_api_inicializacion_ventas import cliente, cabecera, token
from app.core.base_datos import obtener_sesion
from app.core.errores import ErrorAPI
from app.modules.inventario import entradas
from app.modules.ventas import caja
from app.modules.inventario.modelos import EntradaProductos, LineaEntradaProductos, LoteProducto, MovimientoInventario
from app.modules.productos.modelos import Producto
from app.modules.ventas.modelos import VentaDiaria

HOY = datetime(2026, 10, 28, 15, tzinfo=timezone.utc)
RUTA = "/api/v1/inventario/entradas-productos"


@pytest.fixture
def inv(cliente, monkeypatch):
    monkeypatch.setattr(entradas, "ahora", lambda: HOY)
    monkeypatch.setattr(caja, "ahora", lambda: HOY)
    admin = cabecera(token(cliente, "admin@example.com", "clave-segura-admin"))
    operador = cabecera(token(cliente, "operador@example.com", "clave-segura-operador"))
    with contextmanager(cliente.app.dependency_overrides[obtener_sesion])() as s:
        sesiones = sessionmaker(bind=s.get_bind(), expire_on_commit=False)
    with sesiones.begin() as s:
        p = Producto(codigo="PAN", nombre="Pan de prueba", activo=True)
        q = Producto(codigo="CRO", nombre="Croissant de prueba", activo=True)
        s.add_all([p,q]); s.flush()
        ids = (p.id,q.id)
        s.add(LoteProducto(producto_id=p.id, codigo_lote="HISTORICO", lote_informado=True, saldo_disponible=4,
                          fecha_limite_venta=date(2026,10,2), fecha_caducidad=date(2026,10,3)))
    cliente.put(f"/api/v1/ventas/precios/{p.id}", headers=admin,
                json={"clave_idempotencia":"precio-entrada-001", "precio":"2.50", "version_actual":0})
    return cliente, sesiones, admin, operador, ids


def cuerpo(inv, clave="entrada-multiple-001"):
    return {"clave_operacion":clave, "fecha_entrada":"2026-10-28", "motivo":"Ingreso de productos terminados",
            "lineas":[{"producto_id":id_, "codigo_lote":lote, "cantidad":n, "fecha_elaboracion":"2026-10-28",
                       "fecha_caducidad":"2026-10-30", "fecha_limite_venta":"2026-10-29"}
                      for id_,lote,n in [(inv[4][0],"PAN-A",30),(inv[4][1],"CRO-A",20),(inv[4][0],"PAN-B",5)]]}


def contar(inv, modelo):
    with inv[1]() as s:
        return s.scalar(select(func.count()).select_from(modelo))


def test_varios_productos_lotes_historial_recuperacion_y_venta_real(inv):
    c, sesiones, admin, op, ids = inv
    assert c.get(RUTA+"/contexto", headers=op).json()["datos"]["fecha_actual"]=="2026-10-28"
    datos=cuerpo(inv)
    r=c.post(RUTA, headers=admin, json=datos)
    assert r.status_code==201,r.text
    entrada=r.json()["datos"]
    assert len(entrada["lineas"])==3
    assert len({l["movimiento_id"] for l in entrada["lineas"]})==3
    assert c.post(RUTA, headers=admin, json={**datos,"lineas":list(reversed(datos["lineas"]))}).json()==r.json()
    assert c.post(RUTA, headers=admin, json={**datos,"motivo":"Otro contenido"}).status_code==409
    assert c.get(RUTA+"/por-clave/"+datos["clave_operacion"],headers=admin).json()==r.json()
    assert c.get(RUTA+"/por-clave/"+datos["clave_operacion"],headers=op).status_code==404
    assert c.get(RUTA+f"/{entrada['id']}",headers=op).json()==r.json()
    historial=c.get(RUTA+"?limite=1",headers=op).json()
    assert historial["metadatos"]["total"]==1
    assert historial["datos"][0]["lotes"]==3 and historial["datos"][0]["unidades"]==55
    antes=c.get("/api/v1/inventario/disponibilidad?fecha=2026-10-27&tipo=producto",headers=op).json()["datos"]
    assert all(l["codigo_lote"]=="HISTORICO" for p in antes for l in p["lotes"])
    hoy=c.get("/api/v1/inventario/disponibilidad?fecha=2026-10-28&tipo=producto",headers=op).json()["datos"]
    assert {p["item_id"]:p["cantidad_disponible"] for p in hoy}=={ids[0]:"35",ids[1]:"20"}
    cot=c.post("/api/v1/ventas/cotizaciones",headers=op,json={"clave_idempotencia":"cotizar-entrada-001",
        "lineas":[{"producto_id":ids[0],"cantidad":3}]}).json()["datos"]
    venta=c.post("/api/v1/ventas/tickets",headers=op,json={"clave_idempotencia":"venta-entrada-001",
        "cotizacion_id":cot["id"],"total_revisado":"7.50","cobro_presencial":{"medio":"EFECTIVO","importe_recibido":"10.00"}})
    assert venta.status_code==201,venta.text
    assert venta.json()["datos"]["lineas"][0]["salidas"][0]["lote_id"] in {l["lote_id"] for l in entrada["lineas"]}
    with sesiones() as s:
        assert s.scalar(select(LoteProducto.saldo_disponible).where(LoteProducto.codigo_lote=="HISTORICO"))==4
        assert s.scalar(select(func.sum(LoteProducto.saldo_disponible)).where(LoteProducto.producto_id==ids[0]))==36
        assert s.scalar(select(func.count()).select_from(VentaDiaria))==0
    assert contar(inv,EntradaProductos)==1 and contar(inv,LineaEntradaProductos)==3
    assert c.post("/api/v1/inventario/ajustes",headers=admin,json={"tipo":"producto", "lote_id":entrada["lineas"][0]["lote_id"],
        "delta":"1","motivo":"Fecha anterior inválida","clave_operacion":"ajuste-anterior-001","efectivo_en_demo":"2026-10-27T12:00:00"}).status_code==422


@pytest.mark.parametrize("caso", ["cero","fraccion","booleano","duplicado","caducidad","limite","antes","vida","extra","futuro"])
def test_entradas_invalidas_no_crean_efectos(inv, caso):
    c,_,admin,_,_ = inv
    b=cuerpo(inv); l=b["lineas"][0]
    if caso=="cero": l["cantidad"]=0
    if caso=="fraccion": l["cantidad"]=1.5
    if caso=="booleano": l["cantidad"]=True
    if caso=="duplicado": b["lineas"].append(dict(l))
    if caso=="caducidad": l["fecha_caducidad"]="2026-10-27"
    if caso=="limite": l["fecha_limite_venta"]="2026-10-31"
    if caso=="antes": l["fecha_elaboracion"]="2026-10-29"
    if caso=="vida": l["fecha_caducidad"]="2026-11-05"
    if caso=="extra": b["usuario_id"]=999
    if caso=="futuro":
        b["fecha_entrada"]="2026-10-29"
        for l in b["lineas"]: l["fecha_elaboracion"]="2026-10-29"
    assert c.post(RUTA,headers=admin,json=b).status_code==422
    assert contar(inv,EntradaProductos)==0 and contar(inv,LoteProducto)==1 and contar(inv,MovimientoInventario)==0


def test_permisos_duplicado_producto_inactivo_y_rollback_completo(inv, monkeypatch):
    c,sesiones,admin,op,ids=inv
    b=cuerpo(inv)
    assert c.post(RUTA,json=b).status_code==401
    assert c.post(RUTA,headers=op,json=b).status_code==403
    with sesiones.begin() as s: s.get(Producto,ids[1]).activo=False
    assert c.post(RUTA,headers=admin,json=b).status_code==409
    assert contar(inv,LoteProducto)==1
    with sesiones.begin() as s: s.get(Producto,ids[1]).activo=True
    duplicado=cuerpo(inv);duplicado["lineas"][-1]["codigo_lote"]="HISTORICO"
    assert c.post(RUTA,headers=admin,json=duplicado).status_code==409
    original=entradas._aplicar
    def fallar(s,**kw):
        if kw["clave"].endswith("-2"): raise ErrorAPI(409,"FALLO_QA","Fallo controlado de segunda línea")
        return original(s,**kw)
    monkeypatch.setattr(entradas,"_aplicar",fallar)
    assert c.post(RUTA,headers=admin,json=b).status_code==409
    assert contar(inv,EntradaProductos)==0 and contar(inv,LoteProducto)==1 and contar(inv,MovimientoInventario)==0


@pytest.mark.parametrize("misma_clave",[True,False])
def test_registro_concurrente_no_duplica_lotes(inv, misma_clave):
    if os.getenv("E03_POSTGRES_TEST")!="1": pytest.skip("Requiere PostgreSQL aislado")
    c,_,admin,_,_=inv
    b=cuerpo(inv);b["lineas"]=b["lineas"][:1]
    otro={**b,"clave_operacion":b["clave_operacion"] if misma_clave else "otra-entrada-concurrente"}
    with ThreadPoolExecutor(max_workers=2) as pool:
        respuestas=list(pool.map(lambda v:c.post(RUTA,headers=admin,json=v),[b,otro]))
    assert sorted(r.status_code for r in respuestas)==([200,201] if misma_clave else [201,409])
    assert contar(inv,EntradaProductos)==1 and contar(inv,MovimientoInventario)==1 and contar(inv,LoteProducto)==2
