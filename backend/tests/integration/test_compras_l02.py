"""M03→L02 real: decimales, snapshots, recompra y transacciones."""
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from decimal import Decimal
import pytest
from sqlalchemy import func, select, text
from test_api_inicializacion_ventas import cliente
from test_planificacion_m02 import escenario, solicitar, saldos
from test_proveedores_l01 import TelegramFalso
from app.core.errores import ErrorAPI
from app.modules.compras.modelos import LineaPedido, PedidoCompra, PropuestaCompra
from app.modules.compras.servicio import generar_pedidos
from app.modules.ingredientes.servicio import crear_ingrediente
from app.modules.inventario.modelos import LoteIngrediente
from app.modules.inventario.servicio import registrar_ajuste, SolicitudAjuste
from app.modules.planificacion.servicio import generar_plan
from app.modules.proveedores.esquemas import OfertaCrear, ProveedorCrear
from app.modules.proveedores.servicio import ServicioProveedores
from app.modules.recetas.servicio import crear_version, LineaNueva


@pytest.fixture
def compra(escenario):
    _, sesiones, _, _, _, _ = escenario
    with sesiones.begin() as sesion:
        lote = sesion.scalar(select(LoteIngrediente))
        ingrediente_id = lote.ingrediente_id
        registrar_ajuste(sesion, SolicitudAjuste("ingrediente", lote.id, -lote.saldo_disponible,
                         "fixture faltante", "l02-ajuste", datetime(2022,8,24,10)), None)
        servicio = ServicioProveedores(sesion, TelegramFalso())
        proveedor = servicio.crear_proveedor(ProveedorCrear(codigo="P1", nombre="Proveedor uno", chat_id_pruebas="123"))
        assert servicio.verificar_destino(proveedor.id).verificado
        oferta = servicio.crear_oferta(proveedor.id, OfertaCrear(ingrediente_id=ingrediente_id,
            descripcion="Bolsa", unidad_compra="bolsa", factor_conversion=Decimal("1000"),
            minimo=Decimal("3"), multiplo=Decimal("2"), preferida=True))
    return escenario, proveedor.id, oferta.id, ingrediente_id


def generar(escenario, plan_id):
    cliente, _, admin, _, _, _ = escenario
    return cliente.post("/api/v1/pedidos/generar", headers=admin, json={"plan_id": plan_id})


def test_pedidos_conversion_exacta_snapshots_permisos_y_stock(compra):
    escenario, proveedor_id, oferta_id, _ = compra
    cliente, sesiones, admin, operador, _, _ = escenario
    antes = saldos(sesiones)
    plan = solicitar(escenario).json()["datos"]
    assert cliente.post("/api/v1/pedidos/generar", json={"plan_id":plan["id"]}).status_code == 401
    assert cliente.post("/api/v1/pedidos/generar", headers=operador, json={"plan_id":plan["id"]}).status_code == 403
    assert generar(escenario, 999).status_code == 404
    respuesta = generar(escenario, plan["id"])
    assert respuesta.status_code == 201, respuesta.text
    propuesta = respuesta.json()["datos"]
    assert propuesta["estado"] == "GENERADA"
    pedido, = propuesta["pedidos"]
    assert pedido["estado"] == "PENDIENTE_APROBACION" and pedido["envio_estado"] == "SIN_ENVIO"
    linea, = pedido["lineas"]
    assert Decimal(linea["faltante_base"]) == Decimal("1503")
    assert Decimal(linea["cantidad_compra"]) == 4 and Decimal(linea["cantidad_base_pedida"]) == 4000
    assert linea["oferta"]["oferta_id"] == oferta_id
    assert saldos(sesiones) == antes
    assert cliente.get(f'/api/v1/pedidos/{pedido["id"]}', headers=operador).json()["datos"] == pedido
    assert cliente.get(f'/api/v1/compras/propuestas?plan_id={plan["id"]}', headers=operador).json()["datos"] == [propuesta]
    assert cliente.get(f'/api/v1/pedidos?plan_id={plan["id"]}', headers=admin).json()["datos"] == [pedido]
    assert cliente.get("/api/v1/pedidos/999", headers=admin).status_code == 404
    with sesiones.begin() as sesion:
        ServicioProveedores(sesion).desactivar_oferta(oferta_id)
        ServicioProveedores(sesion).cambiar_estado(proveedor_id, False)
    assert cliente.patch("/api/v1/negocios/actual", headers=admin, json={"modo_envio_pedidos":"AUTOMATICO"}).status_code == 200
    repetida = generar(escenario, plan["id"]).json()["datos"]
    assert not repetida["pedidos"][0]["destino_actual"]["activo"]
    # Solo el destino actual es una consulta viva; los snapshots no se recalculan.
    repetida["pedidos"][0]["destino_actual"] = propuesta["pedidos"][0]["destino_actual"]
    assert repetida == propuesta


@pytest.mark.parametrize("causa", ["SIN_PROVEEDOR", "DESTINO_NO_VERIFICADO", "AUTOMATICO", "INCOMPLETAS"])
def test_bloqueos_reales_no_simulan_envio(compra, causa):
    escenario, proveedor_id, oferta_id, _ = compra
    cliente, sesiones, admin, _, corrida, productos = escenario
    with sesiones.begin() as sesion:
        s = ServicioProveedores(sesion)
        if causa == "SIN_PROVEEDOR": s.cambiar_estado(proveedor_id, False)
        if causa == "DESTINO_NO_VERIFICADO": s.vincular_chat(proveedor_id, "456")
        if causa == "INCOMPLETAS":
            from app.modules.pronosticos.modelos import Pronostico
            p = sesion.scalar(select(Pronostico).where(Pronostico.corrida_id==corrida, Pronostico.producto_id==productos["baguette"]))
            p.estado="HISTORIAL_INSUFICIENTE"; p.cantidad_pronosticada=None
    if causa == "AUTOMATICO":
        cliente.patch("/api/v1/negocios/actual", headers=admin, json={"modo_envio_pedidos":"AUTOMATICO"})
    plan = solicitar(escenario).json()["datos"]
    respuesta = generar(escenario, plan["id"])
    assert respuesta.status_code == 201, respuesta.text
    propuesta = respuesta.json()["datos"]
    assert propuesta["estado"] == "BLOQUEADA"
    assert all(p["estado"] == "BLOQUEADO" for p in propuesta["pedidos"])
    if causa in {"SIN_PROVEEDOR", "INCOMPLETAS"}:
        assert propuesta["pedidos"] == [] and propuesta["incidencias"]
    else:
        assert ("CANAL_PENDIENTE_L03" if causa == "AUTOMATICO" else causa) in propuesta["pedidos"][0]["bloqueos"]


def test_recompra_requiere_cancelacion_explicita_y_conserva_historial(compra):
    escenario, _, _, _ = compra
    cliente, _, admin, operador, _, _ = escenario
    original = solicitar(escenario).json()["datos"]
    anterior = generar(escenario, original["id"]).json()["datos"]
    nuevo = solicitar(escenario, "plan-nuevo").json()["datos"]
    assert generar(escenario, nuevo["id"]).status_code == 409
    ruta = f'/api/v1/compras/propuestas/{anterior["id"]}/cancelar'
    assert cliente.post(ruta, headers=operador, json={"motivo":"corrección"}).status_code == 403
    assert cliente.post(ruta, headers=admin, json={"motivo":" "}).status_code == 422
    respuesta = cliente.post(ruta, headers=admin, json={"motivo":"Usar plan corregido"})
    assert respuesta.status_code == 200
    cancelada = respuesta.json()["datos"]
    assert cancelada["estado"] == "CANCELADA" and not cancelada["activa"]
    assert cancelada["pedidos"][0]["estado"] == "CANCELADO"
    assert cliente.post(ruta, headers=admin, json={"motivo":"Usar plan corregido"}).json()["datos"] == cancelada
    assert cliente.post(ruta, headers=admin, json={"motivo":"Otro motivo"}).status_code == 409
    assert generar(escenario, original["id"]).json()["datos"] == cancelada
    assert generar(escenario, nuevo["id"]).status_code == 201
    assert cliente.get(f'/api/v1/planes/{original["id"]}', headers=admin).json()["datos"]["pedidos_estado"] == "CANCELADA"


def test_rollback_consumidor_y_concurrencia_por_fecha(compra):
    escenario, _, _, _ = compra
    _, sesiones, _, _, corrida, _ = escenario
    with pytest.raises(RuntimeError), sesiones.begin() as sesion:
        sesion.execute(text("UPDATE configuracion_inicial SET mensaje_error='fixture' WHERE id=1"))
        plan = generar_plan(sesion, corrida_id=corrida, clave_ejecucion="rollback-l02")
        generar_pedidos(sesion, plan.id)
        raise RuntimeError("Consumidor falló")
    with sesiones() as sesion:
        for modelo in (PropuestaCompra, PedidoCompra, LineaPedido):
            assert sesion.scalar(select(func.count()).select_from(modelo)) == 0
    if os.getenv("E03_POSTGRES_TEST") != "1":
        return
    ids = [solicitar(escenario, clave).json()["datos"]["id"] for clave in ("primero", "segundo")]
    def producir(plan_id):
        try:
            with sesiones.begin() as sesion:
                return generar_pedidos(sesion, plan_id).estado
        except ErrorAPI as error:
            return error.codigo
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(producir, ids)) == ["GENERADA", "RECOMPRA_FECHA"]
    with sesiones() as sesion:
        assert sesion.scalar(select(func.count()).select_from(PropuestaCompra)) == 1
        assert sesion.scalar(select(func.count()).select_from(PedidoCompra)) == 1


def test_agrupacion_por_proveedor_y_bloqueo_global(compra):
    escenario, _, _, harina_id = compra
    _, sesiones, _, _, _, productos = escenario
    with sesiones.begin() as sesion:
        sal = crear_ingrediente(sesion, "sal", "Sal", "g")
        sesion.add(LoteIngrediente(ingrediente_id=sal.id, codigo_lote="SAL-0", lote_informado=True, saldo_disponible=0))
        crear_version(sesion, productos["baguette"], [LineaNueva(harina_id, Decimal("250.5")), LineaNueva(sal.id, Decimal("0.2"))], "fixture dos proveedores")
        s = ServicioProveedores(sesion)
        p2 = s.crear_proveedor(ProveedorCrear(codigo="P2", nombre="Proveedor dos"))
        s.crear_oferta(p2.id, OfertaCrear(ingrediente_id=sal.id, descripcion="Sal", unidad_compra="g", factor_conversion=1, minimo=0, multiplo=Decimal("0.5"), preferida=True))
    plan = solicitar(escenario).json()["datos"]
    propuesta = generar(escenario, plan["id"]).json()["datos"]
    assert len(propuesta["pedidos"]) == 2 and propuesta["estado"] == "BLOQUEADA"
    assert all(p["estado"] == "BLOQUEADO" for p in propuesta["pedidos"])
    sal = next(l for p in propuesta["pedidos"] for l in p["lineas"] if l["nombre"] == "Sal")
    assert Decimal(sal["cantidad_compra"]) == Decimal("1.5")


def test_sin_faltantes_no_crea_pedidos_ni_reserva_fecha(escenario):
    _, sesiones, _, _, _, _ = escenario
    for clave in ("sin-faltantes-1", "sin-faltantes-2"):
        plan = solicitar(escenario, clave).json()["datos"]
        respuesta = generar(escenario, plan["id"])
        assert respuesta.status_code == 201, respuesta.text
        propuesta = respuesta.json()["datos"]
        assert propuesta["estado"] == "SIN_FALTANTES" and not propuesta["activa"]
        assert propuesta["pedidos"] == [] and propuesta["incidencias"] == []
    with sesiones() as sesion:
        assert sesion.scalar(select(func.count()).select_from(PedidoCompra)) == 0


def test_repeticion_concurrente_de_un_plan_no_duplica_pedidos(compra):
    if os.getenv("E03_POSTGRES_TEST") != "1":
        pytest.skip("Requiere PostgreSQL: E03_POSTGRES_TEST=1")
    escenario, _, _, _ = compra
    _, sesiones, _, _, _, _ = escenario
    plan_id = solicitar(escenario).json()["datos"]["id"]
    def generar_uno(_):
        with sesiones.begin() as sesion:
            return generar_pedidos(sesion, plan_id).id
    with ThreadPoolExecutor(max_workers=2) as pool:
        ids = list(pool.map(generar_uno, range(2)))
    assert ids[0] == ids[1]
    with sesiones() as sesion:
        assert sesion.scalar(select(func.count()).select_from(PropuestaCompra)) == 1
        assert sesion.scalar(select(func.count()).select_from(PedidoCompra)) == 1
        assert sesion.scalar(select(func.count()).select_from(LineaPedido)) == 1


def test_motor_recompra_conserva_nuevo_plan_y_evaluacion(compra, monkeypatch):
    from datetime import date
    from app.modules.automatizaciones.servicio import crear_o_recuperar_ejecucion
    from app.modules.pronosticos.modelos import ArtefactoModelo
    from app.modules.pronosticos import servicio as inferencia
    from app.modules.planificacion.modelos import PlanProduccion
    from app.workers import motor
    escenario, _, _, _ = compra
    _, sesiones, _, _, _, productos = escenario
    monkeypatch.setattr(motor, "SessionLocal", sesiones)
    class ModeloFixture:
        def predict(self, tabla): return [10]
    monkeypatch.setattr(inferencia, "_cargar_cbm", lambda _: (ModeloFixture(), {
        "productos_entrenados":["BAGUETTE","CROISSANT","BANETTE"], "min_observaciones_previas_28_dias":1}))
    with sesiones.begin() as sesion:
        modelo = sesion.scalar(select(ArtefactoModelo))
        modelo.particion_json = {"inicio_prueba":"2022-08-01", "fin_prueba":"2022-08-31"}
    for clave in ("propuesta-original", "propuesta-recalculada"):
        with sesiones.begin() as sesion:
            ejecucion = crear_o_recuperar_ejecucion(sesion, "GENERAR_PROPUESTA", clave, {
                "parametros":{"fecha_objetivo_demo":"2022-08-24", "producto_ids":list(productos.values())}})
        mensajes = []
        motor.despachar_pendientes(lambda id_, token_: mensajes.append((id_,token_)))
        assert motor.ejecutar(*next(m for m in mensajes if m[0]==ejecucion.id))["resultado"] == "COMPLETADA"
    from app.modules.automatizaciones.modelos import EjecucionAutomatizacion
    with sesiones() as sesion:
        segunda = sesion.get(EjecucionAutomatizacion, ejecucion.id)
        assert segunda.datos_salida_json["pedidos_estado"] == "RECOMPRA_FECHA"
        assert segunda.datos_salida_json["evaluacion_ejecucion_id"]
        assert sesion.scalar(select(func.count()).select_from(PlanProduccion)) == 2
        assert sesion.scalar(select(func.count()).select_from(PropuestaCompra)) == 1
