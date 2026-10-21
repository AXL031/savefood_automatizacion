"""Recepción física explícita; PostgreSQL aislado y transporte Telegram falso."""
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta
from decimal import Decimal
import pytest
from sqlalchemy import func, select
from test_api_inicializacion_ventas import cliente
from test_planificacion_m02 import escenario, solicitar
from test_compras_l02 import compra, generar
from test_aprobacion_envio_l03 import borrador, aprobar, publicar, TelegramEnvio
from app.modules.compras.envios import ejecutar_envio
from app.modules.compras.modelos import PedidoCompra, PropuestaCompra, RecepcionPedido, LineaRecepcionPedido, EnvioPedido
from app.modules.compras.recepciones import RecepcionCrear, registrar_recepcion
from app.modules.inventario.modelos import LoteIngrediente, MovimientoInventario
from app.modules.inventario.servicio import consultar_disponibilidad
from app.modules.proveedores.servicio import ServicioProveedores
from app.modules.proveedores.esquemas import OfertaCrear
from app.modules.planificacion.modelos import PlanProduccion
from app.core.errores import ErrorAPI


def enviado(compra):
    entorno = compra[0]
    _, sesiones, _, _, _, _ = entorno
    propuesta, pedido = borrador(compra)
    assert aprobar(entorno, pedido).status_code == 202
    tareas, _ = publicar(sesiones)
    fake = TelegramEnvio(sesiones)
    assert ejecutar_envio(*tareas[0], sesiones=sesiones, cliente=fake)["estado"] == "ENVIADO"
    assert len(fake.llamadas) == 1
    return propuesta, pedido


def entrada(pedido, cantidad="2", clave="recepcion-prueba-0001", **linea):
    return {"clave_idempotencia": clave, "fecha_recepcion": "2022-08-24", "motivo": "Entrega comprobada en almacén",
        "lineas": [{"linea_pedido_id": pedido["lineas"][0]["id"], "cantidad_compra": cantidad, **linea}]}


def recibir(compra, pedido, datos, actor=None):
    http, _, admin, _, _, _ = compra[0]
    return http.post(f'/api/v1/pedidos/{pedido["id"]}/recepciones', headers=actor or admin, json=datos)


def cuenta(sesiones, modelo):
    with sesiones() as s:
        return s.scalar(select(func.count()).select_from(modelo))


def test_parcial_total_idempotencia_conversion_conservada_y_auditoria(compra):
    propuesta, pedido = enviado(compra)
    http, sesiones, admin, operador, _, _ = compra[0]
    with sesiones.begin() as s:
        # La recepción usa el factor del pedido, aunque se sustituya la oferta actual.
        servicio = ServicioProveedores(s)
        servicio.desactivar_oferta(compra[2])
        servicio.crear_oferta(compra[1], OfertaCrear(ingrediente_id=compra[3], descripcion="Otra presentación",
            unidad_compra="saco", factor_conversion=Decimal("5000"), preferida=True))
    antes = cuenta(sesiones, MovimientoInventario)
    datos = entrada(pedido, codigo_lote="ENTREGA-A", fecha_caducidad="2022-09-30")
    assert recibir(compra, pedido, datos, operador).status_code == 403
    r = recibir(compra, pedido, datos)
    assert r.status_code == 200, r.text
    parcial = r.json()["datos"]
    assert parcial["estado"] == "ENVIADO" and parcial["recepcion_estado"] == "PARCIAL"
    assert Decimal(parcial["lineas"][0]["cantidad_recibida"]) == 2
    assert Decimal(parcial["lineas"][0]["cantidad_pendiente"]) == 2
    assert Decimal(parcial["recepciones"][0]["lineas"][0]["cantidad_base"]) == 2000
    assert recibir(compra, pedido, datos).json()["datos"] == parcial
    assert recibir(compra, pedido, {**datos, "motivo": "Otro contenido"}).status_code == 409
    assert cuenta(sesiones, MovimientoInventario) == antes + 1
    with sesiones() as s:
        lote = s.scalar(select(LoteIngrediente).where(LoteIngrediente.codigo_lote == "ENTREGA-A"))
        assert lote.saldo_disponible == 2000 and lote.fecha_ingreso == date(2022,8,24)
        m = s.scalar(select(MovimientoInventario).where(MovimientoInventario.tipo == "RECEPCION"))
        assert m.usuario_id and m.lote_ingrediente_id == lote.id
        pasado = consultar_disponibilidad(s, date(2022,8,23))
        assert all(l.lote_id != lote.id for l in pasado.de("ingrediente", compra[3]).lotes)
    completa = recibir(compra, pedido, entrada(pedido, clave="recepcion-prueba-0002"))
    assert completa.status_code == 200, completa.text
    assert completa.json()["datos"]["recepcion_estado"] == "RECIBIDO"
    assert recibir(compra, pedido, entrada(pedido, "0.1", "recepcion-prueba-0003")).status_code == 409
    assert cuenta(sesiones, RecepcionPedido) == 2
    assert cuenta(sesiones, MovimientoInventario) == antes + 2
    assert http.get(f'/api/v1/compras/propuestas/{propuesta["id"]}', headers=admin).json()["datos"]["activa"]


@pytest.mark.parametrize("cambio,estado", [
    ({"cantidad_compra": "5"},409), ({"cantidad_compra":"0"},422),
    ({"cantidad_compra":"0.00001"},422), ({"linea_pedido_id":99999},422),
    ({"fecha_caducidad":"2022-08-23"},422),
])
def test_entrada_invalida_no_deja_recepcion_lote_ni_movimiento(compra,cambio,estado):
    _, pedido = enviado(compra)
    sesiones = compra[0][1]
    antes = [cuenta(sesiones, m) for m in (RecepcionPedido,LoteIngrediente,MovimientoInventario)]
    datos = entrada(pedido)
    datos["lineas"][0].update(cambio)
    r = recibir(compra,pedido,datos)
    assert r.status_code == estado, r.text
    assert [cuenta(sesiones,m) for m in (RecepcionPedido,LoteIngrediente,MovimientoInventario)] == antes


@pytest.mark.parametrize("fecha", ["2022-08-23", (date.today()+timedelta(days=2)).isoformat()])
def test_fecha_invalida_y_lineas_repetidas(compra, fecha):
    _,pedido = enviado(compra)
    datos=entrada(pedido); datos["fecha_recepcion"]=fecha
    assert recibir(compra,pedido,datos).status_code == 422
    datos=entrada(pedido); datos["lineas"] *= 2
    assert recibir(compra,pedido,datos).status_code == 422
    assert cuenta(compra[0][1], RecepcionPedido) == 0


def test_no_recibe_pedido_sin_envio_y_lote_duplicado_no_se_suma(compra):
    _,pedido = borrador(compra)
    assert recibir(compra,pedido,entrada(pedido)).status_code == 409
    entorno=compra[0]; sesiones=entorno[1]
    assert aprobar(entorno,pedido).status_code == 202
    tareas,_=publicar(sesiones)
    ejecutar_envio(*tareas[0],sesiones=sesiones,cliente=TelegramEnvio(sesiones))
    assert recibir(compra,pedido,entrada(pedido,codigo_lote="LOTE-X")).status_code == 200
    r=recibir(compra,pedido,entrada(pedido,clave="segunda-recepcion",codigo_lote="LOTE-X"))
    assert r.status_code == 409
    assert cuenta(sesiones,RecepcionPedido) == 1


@pytest.mark.parametrize("caso", ["unidad_fraccionaria", "conversion_inexacta", "rollback_consumidor"])
def test_frontera_inventario_y_rollback_del_consumidor(compra,caso):
    _,pedido=enviado(compra)
    sesiones=compra[0][1]
    from app.modules.compras.modelos import LineaPedido
    from app.modules.ingredientes.modelos import Ingrediente
    from app.modules.autenticacion.modelos import Usuario
    with sesiones.begin() as s:
        if caso=="unidad_fraccionaria": s.get(Ingrediente,compra[3]).unidad_base="unidad"
        if caso=="conversion_inexacta":
            linea=s.get(LineaPedido,pedido["lineas"][0]["id"])
            linea.oferta_json={**linea.oferta_json,"factor_conversion":"0.001"}
        actor=s.scalar(select(Usuario).where(Usuario.correo=="admin@example.com"))
        uid,nombre=actor.id,actor.nombre
    antes=[cuenta(sesiones,m) for m in (RecepcionPedido,LoteIngrediente,MovimientoInventario)]
    if caso=="rollback_consumidor":
        with pytest.raises(RuntimeError), sesiones.begin() as s:
            registrar_recepcion(s,pedido["id"],RecepcionCrear(**entrada(pedido)),uid,nombre)
            raise RuntimeError("Consumidor aborta después de aplicar inventario")
    else:
        r=recibir(compra,pedido,entrada(pedido,"0.0001"))
        assert r.status_code==422,r.text
    assert [cuenta(sesiones,m) for m in (RecepcionPedido,LoteIngrediente,MovimientoInventario)]==antes


def test_migracion_0018_ddl_reversible_y_metadatos_completos(cliente):
    from contextlib import contextmanager
    from app.core.base_datos import obtener_sesion
    from app.core.base import Base
    from alembic.autogenerate import compare_metadata
    from alembic.migration import MigrationContext
    from alembic.operations import Operations
    from sqlalchemy import inspect
    from test_migraciones_entregas import cargar_revision
    with contextmanager(cliente.app.dependency_overrides[obtener_sesion])() as s:
        motor=s.get_bind()
    revision=cargar_revision("0018_recepcion_compras")
    with motor.begin() as c, Operations.context(MigrationContext.configure(c)):
        revision.downgrade()
        assert "recepcion_pedido" not in inspect(c).get_table_names()
        assert "fecha_ingreso" not in {x["name"] for x in inspect(c).get_columns("lote_ingrediente")}
        revision.upgrade()
        assert compare_metadata(MigrationContext.configure(c),Base.metadata)==[]
        assert "ck_movimiento_recepcion_ingrediente" in {x["name"] for x in inspect(c).get_check_constraints("movimiento_inventario")}


def test_migracion_0018_protege_evidencia(compra):
    from alembic.operations import Operations
    from alembic.migration import MigrationContext
    from test_migraciones_entregas import cargar_revision
    _,pedido=enviado(compra)
    assert recibir(compra,pedido,entrada(pedido)).status_code==200
    with compra[0][1].begin() as s:
        with Operations.context(MigrationContext.configure(s.connection())):
            with pytest.raises(RuntimeError,match="evidencia"):
                cargar_revision("0018_recepcion_compras").downgrade()
    assert cuenta(compra[0][1],RecepcionPedido)==1


@pytest.mark.skipif(os.getenv("E03_POSTGRES_TEST")!="1",reason="Bloqueos requieren PostgreSQL")
@pytest.mark.parametrize("misma_clave", [True,False])
def test_recepciones_concurrentes_no_duplican_stock(compra,misma_clave):
    _,pedido=enviado(compra)
    http,sesiones,admin,_,_,_=compra[0]
    # La identidad proviene del administrador de la fixture; sin transporte real.
    from app.modules.autenticacion.modelos import Usuario
    with sesiones() as s:
        actor=s.scalar(select(Usuario).where(Usuario.correo=="admin@example.com"))
        uid,nombre=actor.id,actor.nombre
    def operar(n):
        try:
            with sesiones.begin() as s:
                datos=RecepcionCrear(**entrada(pedido,"4",f"concurrente-{0 if misma_clave else n}"))
                return registrar_recepcion(s,pedido["id"],datos,uid,nombre).id
        except ErrorAPI as e: return e.codigo
    with ThreadPoolExecutor(max_workers=2) as pool:
        resultado=list(pool.map(operar,[1,2]))
    assert cuenta(sesiones,RecepcionPedido)==cuenta(sesiones,LineaRecepcionPedido)==1
    if misma_clave: assert resultado[0]==resultado[1]
    else: assert "EXCEDE_PENDIENTE" in resultado


def test_corregir_faltantes_conserva_original_sin_outbox_y_rollback_si_persisten(compra):
    entorno, proveedor, oferta, ingrediente=compra
    http,sesiones,admin,operador,_,_=entorno
    with sesiones.begin() as s: ServicioProveedores(s).desactivar_oferta(oferta)
    original=generar(entorno,solicitar(entorno).json()["datos"]["id"]).json()["datos"]
    ruta=f'/api/v1/compras/propuestas/{original["id"]}/corregir'
    assert original["estado"]=="BLOQUEADA"
    antes=cuenta(sesiones,PlanProduccion)
    assert http.post(ruta,headers=operador,json={"motivo":"Corregir"}).status_code==403
    assert http.post(ruta,headers=admin,json={"motivo":"Corregir"}).status_code==409
    assert cuenta(sesiones,PlanProduccion)==antes
    assert http.get(f'/api/v1/compras/propuestas/{original["id"]}',headers=admin).json()["datos"]["activa"]
    with sesiones.begin() as s:
        ServicioProveedores(s).crear_oferta(proveedor,OfertaCrear(ingrediente_id=ingrediente,
            descripcion="Bolsa corregida",unidad_compra="kg",factor_conversion=Decimal(1000),preferida=True))
    assert http.patch('/api/v1/negocios/actual',headers=admin,json={"modo_envio_pedidos":"AUTOMATICO"}).status_code==200
    r=http.post(ruta,headers=admin,json={"motivo":"Corregir con ofertas actuales"})
    assert r.status_code==200,r.text
    nueva=r.json()["datos"]
    assert nueva["id"]!=original["id"] and nueva["plan_id"]!=original["plan_id"]
    assert nueva["estado"]=="GENERADA" and nueva["modo_envio"]=="REQUIERE_APROBACION"
    assert all(p["estado"]=="PENDIENTE_APROBACION" for p in nueva["pedidos"])
    vieja=http.get(f'/api/v1/compras/propuestas/{original["id"]}',headers=admin).json()["datos"]
    assert vieja["estado"]=="CANCELADA" and vieja["reemplazo_id"]==nueva["id"]
    assert vieja["incidencias"]==original["incidencias"] and cuenta(sesiones,EnvioPedido)==0
    assert http.post(ruta,headers=admin,json={"motivo":"Corregir con ofertas actuales"}).json()["datos"]==nueva
    assert cuenta(sesiones,PlanProduccion)==antes+1
    assert http.post(f'/api/v1/compras/propuestas/{nueva["id"]}/corregir',headers=admin,json={"motivo":"Corregir"}).status_code==409
