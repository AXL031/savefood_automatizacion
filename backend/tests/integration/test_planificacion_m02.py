"""M02 consume APIs reales K02/M01/V02; fixtures de predicción, sin producción."""
import os
from contextlib import contextmanager
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from test_api_inicializacion_ventas import cliente, archivos, FECHAS, cabecera, token
from app.core.base_datos import obtener_sesion
from app.modules.automatizaciones.servicio import crear_o_recuperar_ejecucion
from app.modules.inventario.modelos import LoteProducto, MovimientoInventario
from app.modules.inventario.servicio import registrar_ajuste, SolicitudAjuste
from app.modules.planificacion.modelos import ElementoPlan, PlanProduccion, NecesidadIngrediente
from app.modules.compras.modelos import PropuestaCompra, PedidoCompra
from app.modules.planificacion.servicio import generar_plan, detalle_plan
from app.modules.pronosticos.modelos import ArtefactoModelo, CorridaPronostico, Pronostico
from app.modules.recetas.modelos import Receta
from app.modules.recetas.servicio import crear_version, LineaNueva
from app.modules.productos.modelos import Producto
from app.modules.pronosticos import servicio as inferencia
from app.modules.planificacion import manejadores
from app.workers import motor
from app.workers.retry.politica import ErrorDatos


@pytest.fixture
def escenario(cliente):
    admin = cabecera(token(cliente, "admin@example.com", "clave-segura-admin"))
    operador = cabecera(token(cliente, "operador@example.com", "clave-segura-operador"))
    carga = cliente.post("/api/v1/inicializacion/confirmar", headers=admin,
                         data={**FECHAS, "clave_importacion": "m02-carga"}, files=archivos())
    assert carga.status_code == 201, carga.text
    with contextmanager(cliente.app.dependency_overrides[obtener_sesion])() as sesion:
        sesiones = sessionmaker(bind=sesion.get_bind(), expire_on_commit=False)
    with sesiones.begin() as sesion:
        productos = {p.codigo: p.id for p in sesion.scalars(select(Producto))}
        tarea = crear_o_recuperar_ejecucion(sesion, "GENERAR_PROPUESTA", "m02-fixture", {})
        modelo = ArtefactoModelo(version_modelo="m02-fixture", ruta_local="fixture", sha256="a"*64,
                                huella_datos_entrenamiento="b"*64, fecha_corte_entrenamiento=date(2022,6,30),
                                particion_json={}, estado="LISTO_DEMO")
        sesion.add(modelo); sesion.flush()
        corrida = CorridaPronostico(ejecucion_id=tarea.id, modelo_id=modelo.id, tipo="DEMO_PROGRAMADA",
                                   clave_ejecucion="m02-fixture", huella_datos_entrada="c"*64,
                                   fecha_objetivo=date(2022,8,24), estado="COMPLETADA")
        sesion.add(corrida); sesion.flush()
        for codigo, cantidad in (("baguette",10), ("croissant",0), ("banette",1)):
            sesion.add(Pronostico(corrida_id=corrida.id, producto_id=productos[codigo],
                                 estado="DISPONIBLE", cantidad_pronosticada=cantidad))
        sesion.flush()
    return cliente, sesiones, admin, operador, corrida.id, productos


def solicitar(escenario, clave="m02-plan"):
    cliente, _, admin, _, corrida, _ = escenario
    return cliente.post("/api/v1/planes", headers=admin, json={"corrida_id":corrida, "clave_ejecucion":clave})


def saldos(sesiones):
    with sesiones() as sesion:
        return ([(l.id,l.saldo_disponible) for l in sesion.scalars(select(LoteProducto).order_by(LoteProducto.id))],
                sesion.scalar(select(func.count()).select_from(MovimientoInventario)))


def test_plan_calculo_snapshots_idempotencia_y_permisos(escenario):
    cliente, sesiones, admin, operador, corrida, productos = escenario
    ruta = "/api/v1/planes"
    assert cliente.get(ruta).status_code == 401
    assert cliente.post(ruta, headers=operador, json={"corrida_id":corrida,"clave_ejecucion":"negado"}).status_code == 403
    assert cliente.post(ruta, headers=admin, json={"corrida_id":corrida,"clave_ejecucion":" "}).status_code == 422
    assert cliente.post(ruta, headers=admin, json={"corrida_id":999,"clave_ejecucion":"ausente"}).status_code == 404
    antes = saldos(sesiones)
    respuesta = solicitar(escenario)
    assert respuesta.status_code == 201, respuesta.text
    plan = respuesta.json()["datos"]
    elementos = {e["producto_id"]:e for e in plan["elementos"]}
    assert elementos[productos["baguette"]]["cantidad_producir"] == 6
    assert elementos[productos["croissant"]]["cantidad_producir"] == 0
    assert elementos[productos["banette"]]["cantidad_producir"] == 0
    assert elementos[productos["baguette"]]["receta"]["lineas"][0]["cantidad_por_unidad"] == "250.500"
    assert "VIGENCIA_STOCK_DESCONOCIDA" in elementos[productos["banette"]]["avisos"]
    assert solicitar(escenario).json()["datos"] == plan
    assert saldos(sesiones) == antes
    assert cliente.get(f'{ruta}/{plan["id"]}', headers=operador).json()["datos"] == plan
    assert cliente.get(f'{ruta}?corrida_id={corrida}', headers=admin).json()["datos"][0]["id"] == plan["id"]
    assert cliente.get(f'{ruta}?corrida_id=999', headers=admin).json()["datos"] == []
    assert cliente.get(f'{ruta}/999', headers=admin).status_code == 404


@pytest.mark.parametrize("impedimento", ["HISTORIAL_INSUFICIENTE", "PRODUCTO_NO_CUBIERTO", "SIN_RECETA", "STOCK_DESCONOCIDO"])
def test_desconocidos_no_se_convierten_en_cero(escenario, impedimento):
    _, sesiones, _, _, corrida, productos = escenario
    producto_id = productos["croissant"]
    with sesiones.begin() as sesion:
        if impedimento in ("HISTORIAL_INSUFICIENTE", "PRODUCTO_NO_CUBIERTO"):
            p = sesion.scalar(select(Pronostico).where(Pronostico.corrida_id==corrida, Pronostico.producto_id==producto_id))
            p.estado = impedimento; p.cantidad_pronosticada = None
        elif impedimento == "SIN_RECETA":
            sesion.scalar(select(Receta).where(Receta.producto_id==producto_id)).activo = False
        else:
            sesion.delete(sesion.scalar(select(LoteProducto).where(LoteProducto.producto_id==producto_id)))
    respuesta = solicitar(escenario)
    assert respuesta.status_code == 201, respuesta.text
    elemento = next(e for e in respuesta.json()["datos"]["elementos"] if e["producto_id"]==producto_id)
    assert elemento["estado"] == impedimento
    assert elemento["cantidad_producir"] is None
    assert impedimento in elemento["avisos"]


def test_lotes_vencidos_y_limite_de_venta_no_cuentan(escenario):
    _, sesiones, _, _, _, productos = escenario
    with sesiones.begin() as sesion:
        lote = sesion.scalar(select(LoteProducto).where(LoteProducto.producto_id==productos["baguette"]))
        lote.fecha_limite_venta = date(2022,8,23)
    respuesta = solicitar(escenario)
    assert respuesta.status_code == 201, respuesta.text
    elemento = next(e for e in respuesta.json()["datos"]["elementos"] if e["producto_id"]==productos["baguette"])
    assert elemento["stock_disponible"] == 0 and elemento["cantidad_producir"] == 10
    assert elemento["stock"]["lotes"][0]["saldo"] == "4"
    assert elemento["stock"]["lotes"][0]["cuenta"] is False
    assert "LOTES_EXCLUIDOS" in elemento["avisos"]


def test_recalcular_preserva_receta_stock_y_plan_anterior(escenario):
    cliente, sesiones, admin, _, corrida, productos = escenario
    original = solicitar(escenario).json()["datos"]
    with sesiones.begin() as sesion:
        receta = sesion.scalar(select(Receta).where(Receta.producto_id==productos["baguette"], Receta.activo.is_(True)))
        crear_version(sesion, productos["baguette"], [LineaNueva(receta.lineas[0].ingrediente_id, "321.500")], "Receta modificada")
        lote = sesion.scalar(select(LoteProducto).where(LoteProducto.producto_id==productos["baguette"]))
        registrar_ajuste(sesion, SolicitudAjuste("producto", lote.id, 2, "Ajuste fixture", "m02-ajuste", datetime(2022,8,24,10)), None)
    assert solicitar(escenario).status_code == 409
    nueva = solicitar(escenario, "m02-recalculo")
    assert nueva.status_code == 201, nueva.text
    nuevo = nueva.json()["datos"]
    assert nuevo["id"] != original["id"] and nuevo["huella_stock_recetas"] != original["huella_stock_recetas"]
    actual = next(e for e in nuevo["elementos"] if e["producto_id"]==productos["baguette"])
    assert actual["cantidad_producir"] == 4 and actual["receta"]["version"] == 2
    assert cliente.get(f'/api/v1/planes/{original["id"]}', headers=admin).json()["datos"] == original
    with sesiones() as sesion:
        assert sesion.scalar(select(func.count()).select_from(PlanProduccion)) == 2


def test_transaccion_compartida_revierte_todo_y_sql_rechaza_calculo_invalido(escenario):
    _, sesiones, _, _, corrida, _ = escenario
    with pytest.raises(RuntimeError), sesiones.begin() as sesion:
        # Una escritura anterior reproduce la transacción del motor/importador
        # también en el driver SQLite, que difiere BEGIN hasta la primera escritura.
        sesion.execute(text("UPDATE configuracion_inicial SET mensaje_error='fixture' WHERE id=1"))
        generar_plan(sesion, corrida_id=corrida, clave_ejecucion="rollback-plan")
        raise RuntimeError("Fallo del consumidor después del plan")
    with sesiones() as sesion:
        assert sesion.scalar(select(func.count()).select_from(PlanProduccion)) == 0
        assert sesion.scalar(select(func.count()).select_from(ElementoPlan)) == 0
        assert sesion.scalar(select(func.count()).select_from(NecesidadIngrediente)) == 0
    plan = solicitar(escenario).json()["datos"]
    with pytest.raises(IntegrityError), sesiones.begin() as sesion:
        sesion.execute(text("UPDATE elemento_plan SET cantidad_producir=99 WHERE plan_id=:id"), {"id":plan["id"]})


def test_dos_solicitudes_concurrentes_guardan_un_plan(escenario):
    if os.getenv("E03_POSTGRES_TEST") != "1":
        pytest.skip("Concurrencia requiere PostgreSQL: E03_POSTGRES_TEST=1")
    _, sesiones, _, _, corrida, _ = escenario
    def generar(_):
        with sesiones.begin() as sesion:
            return generar_plan(sesion, corrida_id=corrida, clave_ejecucion="plan-concurrente").id
    with ThreadPoolExecutor(max_workers=2) as pool:
        ids = list(pool.map(generar, range(2)))
    assert ids[0] == ids[1]
    with sesiones() as sesion:
        assert sesion.scalar(select(func.count()).select_from(PlanProduccion)) == 1
        assert sesion.scalar(select(func.count()).select_from(ElementoPlan)) == 3
        assert sesion.scalar(select(func.count()).select_from(NecesidadIngrediente)) == 1


@pytest.mark.parametrize("fallar", [False, True])
def test_motor_reentrega_y_fallo_posterior_al_plan_son_atomicos(escenario, monkeypatch, fallar):
    _, sesiones, _, _, _, productos = escenario
    monkeypatch.setattr(motor, "SessionLocal", sesiones)
    class ModeloFixture:
        def predict(self, tabla): return [10]
    monkeypatch.setattr(inferencia, "_cargar_cbm", lambda _: (ModeloFixture(), {
        "productos_entrenados":["BAGUETTE","CROISSANT","BANETTE"], "min_observaciones_previas_28_dias":1}))
    with sesiones.begin() as sesion:
        modelo = sesion.scalar(select(ArtefactoModelo))
        modelo.particion_json = {"inicio_prueba":"2022-08-01", "fin_prueba":"2022-08-31"}
        ejecucion = crear_o_recuperar_ejecucion(sesion, "GENERAR_PROPUESTA", "m02-motor", {
            "parametros":{"fecha_objetivo_demo":"2022-08-24", "producto_ids":list(productos.values())}})
    if fallar:
        def error_posterior(*_): raise ErrorDatos("Consumidor interrumpido después del plan")
        monkeypatch.setattr(manejadores, "solicitar_evaluacion_corrida", error_posterior)
    antes = saldos(sesiones)
    mensajes = []
    motor.despachar_pendientes(lambda id_, token_: mensajes.append((id_,token_)))
    mensaje = next(m for m in mensajes if m[0]==ejecucion.id)
    assert motor.ejecutar(*mensaje)["resultado"] == ("FALLIDA" if fallar else "COMPLETADA")
    assert motor.ejecutar(*mensaje)["resultado"] == "IGNORADA"
    assert saldos(sesiones) == antes
    with sesiones() as sesion:
        assert sesion.scalar(select(func.count()).select_from(PlanProduccion)) == (0 if fallar else 1)
        assert sesion.scalar(select(func.count()).select_from(NecesidadIngrediente)) == (0 if fallar else 1)
        assert sesion.scalar(select(func.count()).select_from(PropuestaCompra)) == (0 if fallar else 1)
        assert sesion.scalar(select(func.count()).select_from(CorridaPronostico)) == (1 if fallar else 2)
