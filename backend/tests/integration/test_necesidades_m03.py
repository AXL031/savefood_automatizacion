"""Integración M03 con recetas, stock, API y snapshots reales."""
from decimal import Decimal
from sqlalchemy import select
from test_api_inicializacion_ventas import cliente
from test_planificacion_m02 import escenario, solicitar, saldos
from app.modules.inventario.modelos import LoteIngrediente
from app.modules.planificacion.modelos import PlanProduccion, NecesidadIngrediente
from app.modules.pronosticos.modelos import Pronostico
from app.modules.ingredientes.servicio import crear_ingrediente
from app.modules.recetas.servicio import crear_version, LineaNueva


def test_suma_compartida_exacta_y_sin_movimientos(escenario):
    _, sesiones, _, _, corrida, productos = escenario
    with sesiones.begin() as sesion:
        p = sesion.scalar(select(Pronostico).where(Pronostico.corrida_id == corrida, Pronostico.producto_id == productos["croissant"]))
        p.cantidad_pronosticada = 2
    antes = saldos(sesiones)
    respuesta = solicitar(escenario)
    assert respuesta.status_code == 201, respuesta.text
    plan = respuesta.json()["datos"]
    assert plan["necesidades_estado"] == "CALCULADAS"
    n, = plan["necesidades"]
    assert Decimal(n["cantidad_necesaria"]) == Decimal("1743.000")
    assert Decimal(n["faltante"]) == 0
    assert len(n["aportes"]) == 3
    assert saldos(sesiones) == antes


def test_stock_desconocido_preservado_y_cero_explicito(escenario):
    cliente, sesiones, admin, _, _, _ = escenario
    with sesiones.begin() as sesion:
        lote = sesion.scalar(select(LoteIngrediente))
        lote_id = lote.id
        # Conservar el lote pero excluirlo por caducidad equivale a cero conocido.
        from datetime import date
        lote.fecha_caducidad = date(2022, 8, 23)
    plan = solicitar(escenario).json()["datos"]
    assert Decimal(plan["necesidades"][0]["faltante"]) == Decimal("1503")
    with sesiones.begin() as sesion:
        lote = sesion.get(LoteIngrediente, lote_id)
        lote.fecha_caducidad = None
        lote.saldo_disponible = Decimal("10")
    assert cliente.get(f'/api/v1/planes/{plan["id"]}', headers=admin).json()["datos"] == plan
    assert solicitar(escenario).status_code == 409
    nuevo = solicitar(escenario, "otro").json()["datos"]
    assert Decimal(nuevo["necesidades"][0]["faltante"]) == Decimal("1493")


def test_plan_anterior_se_completa_una_vez_y_permisos(escenario):
    cliente, sesiones, admin, operador, _, _ = escenario
    plan = solicitar(escenario).json()["datos"]
    with sesiones.begin() as sesion:
        for n in sesion.scalars(select(NecesidadIngrediente)):
            sesion.delete(n)
        p = sesion.get(PlanProduccion, plan["id"])
        p.necesidades_estado = "PENDIENTE_M03"; p.necesidades_meta_json = None
    ruta = f'/api/v1/planes/{plan["id"]}/necesidades'
    assert cliente.post(ruta, headers=operador).status_code == 403
    resultado = cliente.post(ruta, headers=admin)
    assert resultado.status_code == 200
    assert cliente.post(ruta, headers=admin).json() == resultado.json()


def test_produccion_incompleta_no_inventa_aporte(escenario):
    _, sesiones, _, _, corrida, productos = escenario
    with sesiones.begin() as sesion:
        p = sesion.scalar(select(Pronostico).where(Pronostico.corrida_id == corrida, Pronostico.producto_id == productos["baguette"]))
        p.estado = "HISTORIAL_INSUFICIENTE"; p.cantidad_pronosticada = None
    plan = solicitar(escenario).json()["datos"]
    assert plan["necesidades_estado"] == "INCOMPLETAS"
    assert plan["necesidades_meta"]["productos_excluidos"][0]["producto_id"] == productos["baguette"]
    assert Decimal(plan["necesidades"][0]["cantidad_necesaria"]) == 0


def test_ingrediente_sin_lotes_no_es_cero_y_desbordamiento_es_atomico(escenario):
    _, sesiones, _, _, _, productos = escenario
    with sesiones.begin() as sesion:
        ingrediente = crear_ingrediente(sesion, "sal", "Sal", "g")
        crear_version(sesion, productos["baguette"], [LineaNueva(ingrediente.id, Decimal("0.101"))], "fixture sin stock")
    respuesta = solicitar(escenario)
    assert respuesta.status_code == 201, respuesta.text
    plan = respuesta.json()["datos"]
    assert plan["necesidades_estado"] == "INCOMPLETAS"
    sal = next(n for n in plan["necesidades"] if n["ingrediente_id"] == ingrediente.id)
    assert Decimal(sal["cantidad_necesaria"]) == Decimal("0.606")
    assert sal["stock_disponible"] is None and sal["faltante"] is None
    with sesiones.begin() as sesion:
        crear_version(sesion, productos["baguette"], [LineaNueva(ingrediente.id, Decimal("99999999999.999"))], "fixture desbordamiento")
    respuesta = solicitar(escenario, "desbordamiento")
    assert respuesta.status_code == 422, respuesta.text
    with sesiones() as sesion:
        assert len(list(sesion.scalars(select(PlanProduccion)))) == 1


def test_migracion_preserva_plan_previo(escenario):
    import importlib.util
    from pathlib import Path
    from alembic.migration import MigrationContext
    from alembic.operations import Operations
    cliente, sesiones, admin, _, _, _ = escenario
    original = solicitar(escenario).json()["datos"]
    ruta = Path(__file__).resolve().parents[2] / "migrations/versions/0010_m03_necesidades.py"
    spec = importlib.util.spec_from_file_location("m03_delta", ruta)
    migracion = importlib.util.module_from_spec(spec); spec.loader.exec_module(migracion)
    ruta_l02 = ruta.parent / "0011_l02_compras.py"
    spec_l02 = importlib.util.spec_from_file_location("l02_delta", ruta_l02)
    l02 = importlib.util.module_from_spec(spec_l02); spec_l02.loader.exec_module(l02)
    with sesiones.begin() as sesion:
        with Operations.context(MigrationContext.configure(sesion.connection())):
            l02.downgrade()
            migracion.downgrade()
            migracion.upgrade()
            l02.upgrade()
    previo = cliente.get(f'/api/v1/planes/{original["id"]}', headers=admin).json()["datos"]
    assert previo["elementos"] == original["elementos"]
    assert previo["necesidades_estado"] == "PENDIENTE_M03"
    assert previo["necesidades"] == []
    completado = cliente.post(f'/api/v1/planes/{original["id"]}/necesidades', headers=admin)
    assert completado.status_code == 200, completado.text
    assert completado.json()["datos"]["necesidades"] == original["necesidades"]
