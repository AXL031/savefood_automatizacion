"""Frontera E03→ML: API, transacciones, fallos y flujo real con PostgreSQL/Redis."""
import os
import threading
import time
from contextlib import contextmanager
from datetime import date, datetime, timedelta, timezone
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

import pytest
from sqlalchemy import func, select, text
from sqlalchemy.orm import sessionmaker

from test_api_inicializacion_ventas import cliente, archivos, FECHAS, cabecera, token
from app.core.base_datos import obtener_sesion
from app.modules.inicializacion.modelos import ConfiguracionInicial
from app.modules.automatizaciones.modelos import EjecucionAutomatizacion
from app.modules.productos.modelos import Producto
from app.modules.ventas.modelos import VentaDiaria, ImportacionVenta
from app.modules.inventario.modelos import MovimientoInventario
from app.modules.pronosticos.modelos import ArtefactoModelo
from app.modules.pronosticos import manejadores
from app.workers import motor
from app.workers.retry.politica import ErrorDatos


@pytest.fixture
def entorno(cliente, monkeypatch):
    proveedor = cliente.app.dependency_overrides[obtener_sesion]
    with contextmanager(proveedor)() as sesion:
        sesiones = sessionmaker(bind=sesion.get_bind(), expire_on_commit=False)
    monkeypatch.setattr(motor, "SessionLocal", sesiones)
    admin = cabecera(token(cliente, "admin@example.com", "clave-segura-admin"))
    return cliente, sesiones, admin


def cargar(cliente, admin, entrega=None, fechas=FECHAS):
    respuesta = cliente.post("/api/v1/inicializacion/confirmar", data={**fechas, "clave_importacion": "inicial-ml"},
                             files=entrega or archivos(), headers=admin)
    assert respuesta.status_code == 201, respuesta.text
    return cliente.get("/api/v1/inicializacion/estado", headers=admin).json()["datos"]


def estado(cliente, admin):
    respuesta = cliente.get("/api/v1/inicializacion/estado", headers=admin)
    assert respuesta.status_code == 200, respuesta.text
    return respuesta.json()["datos"]


def conteos(sesiones):
    with sesiones() as sesion:
        return tuple(sesion.scalar(select(func.count()).select_from(modelo))
                     for modelo in (Producto, VentaDiaria, ImportacionVenta, MovimientoInventario))


def ejecutar(id_):
    mensajes = []
    motor.despachar_pendientes(lambda id_, token_: mensajes.append((id_, token_)))
    mensaje = next(m for m in mensajes if m[0] == id_)
    return motor.ejecutar(*mensaje), mensaje


def test_carga_reserva_una_preparacion_y_repeticion_no_duplica(entorno):
    cliente, sesiones, admin = entorno
    inicial = cargar(cliente, admin)
    assert inicial["estado"] == "DATOS_CARGADOS"
    assert inicial["preparacion"]["estado"] == "PENDIENTE"
    antes = conteos(sesiones)
    assert cargar(cliente, admin)["preparacion"] == inicial["preparacion"]
    assert conteos(sesiones) == antes
    with sesiones() as sesion:
        assert sesion.scalar(select(func.count()).select_from(EjecucionAutomatizacion)) == 1
    for _ in range(2):
        respuesta = cliente.post("/api/v1/inicializacion/reintentar-preparacion", headers=admin)
        assert respuesta.status_code == 202
        assert respuesta.json()["datos"]["preparacion"]["id"] == inicial["preparacion"]["id"]


def test_reintento_exige_datos_y_administrador(entorno):
    cliente, _, admin = entorno
    assert cliente.post("/api/v1/inicializacion/reintentar-preparacion").status_code == 401
    operador = cabecera(token(cliente, "operador@example.com", "clave-segura-operador"))
    assert cliente.post("/api/v1/inicializacion/reintentar-preparacion", headers=operador).status_code == 403
    assert cliente.post("/api/v1/inicializacion/reintentar-preparacion", headers=admin).status_code == 409


def test_fallo_durable_y_reintento_sin_importar(entorno, monkeypatch):
    cliente, sesiones, admin = entorno
    inicial = cargar(cliente, admin)
    antes = conteos(sesiones)
    def fallar(*_, **__):
        # Otra conexión puede ver ENTRENANDO antes de terminar el handler.
        assert estado(cliente, admin)["estado"] == "ENTRENANDO"
        raise ErrorDatos("Historial insuficiente para entrenar el modelo.")
    monkeypatch.setattr(manejadores, "preparar_modelo", fallar)
    resultado, mensaje = ejecutar(inicial["preparacion"]["id"])
    assert resultado["resultado"] == "FALLIDA"
    actual = estado(cliente, admin)
    assert actual["estado"] == "DATOS_CARGADOS"
    assert "Historial insuficiente" in actual["mensaje_error"]
    assert actual["preparacion"]["estado"] == "FALLIDA"
    assert conteos(sesiones) == antes
    assert motor.ejecutar(*mensaje)["resultado"] == "IGNORADA"
    def reintentar():
        respuesta = cliente.post("/api/v1/inicializacion/reintentar-preparacion", headers=admin)
        assert respuesta.status_code == 202, respuesta.text
        return respuesta.json()["datos"]["preparacion"]["id"]
    if os.getenv("E03_POSTGRES_TEST") == "1":
        with ThreadPoolExecutor(max_workers=2) as pool:
            ids = list(pool.map(lambda _: reintentar(), range(2)))
    else:
        ids = [reintentar(), reintentar()]
    assert ids[0] == ids[1] != inicial["preparacion"]["id"]
    assert estado(cliente, admin)["mensaje_error"] is None
    assert conteos(sesiones) == antes
    with sesiones() as sesion:
        assert sesion.scalar(select(func.count()).select_from(EjecucionAutomatizacion)) == 2


def test_recuperacion_de_worker_actualiza_estado_sin_perder_datos(entorno, monkeypatch):
    cliente, sesiones, admin = entorno
    inicial = cargar(cliente, admin)
    def interrumpir(*_, **__):
        raise SystemExit("caída de proceso")
    monkeypatch.setattr(manejadores, "preparar_modelo", interrumpir)
    with pytest.raises(SystemExit):
        ejecutar(inicial["preparacion"]["id"])
    assert estado(cliente, admin)["estado"] == "ENTRENANDO"
    with sesiones.begin() as sesion:
        sesion.execute(text("UPDATE ejecucion_automatizacion SET lease_hasta=:antes WHERE id=:id"),
                       {"antes": datetime.now(timezone.utc)-timedelta(seconds=1),
                        "id": inicial["preparacion"]["id"]})
    assert motor.despachar_pendientes(lambda *_: None)["recuperadas"] == 1
    actual = estado(cliente, admin)
    assert actual["estado"] == "DATOS_CARGADOS"
    assert actual["preparacion"]["estado"] == "REINTENTANDO"
    respuesta = cliente.post("/api/v1/inicializacion/reintentar-preparacion", headers=admin)
    assert respuesta.json()["datos"]["preparacion"]["id"] == inicial["preparacion"]["id"]


def entrega_historial():
    fecha = date(2022, 1, 1)
    filas = ["fecha_local,sku_externo,unidades_vendidas"]
    while fecha <= date(2022, 6, 30):
        for i, sku in enumerate(("BAGUETTE", "CROISSANT", "BANETTE")):
            filas.append(f"{fecha},{sku},{10+i+fecha.day%7}")
        fecha += timedelta(days=1)
    entrega = archivos(("\n".join(filas)+"\n").encode())
    return [(campo, (nombre, crudo.replace(b"2022-08-25", b"2022-06-21").replace(b"2022-08-24", b"2022-06-20")
                      if nombre == "stock_inicial.csv" else crudo, tipo)) for campo,(nombre,crudo,tipo) in entrega]


def test_beat_entrena_evalua_y_dashboard_real(entorno, monkeypatch, tmp_path):
    if os.getenv("E03_POSTGRES_TEST") != "1":
        pytest.skip("E03_POSTGRES_TEST=1 verifica ML real y Beat con PostgreSQL/Redis")
    from celery.beat import Service
    from celery.contrib.testing.worker import start_worker
    from app.workers.celery_app import celery_app
    cliente, sesiones, admin = entorno
    monkeypatch.setenv("MODEL_ARTIFACT_DIR", str(tmp_path / "modelos"))
    evaluar_real = manejadores.evaluar_modelo
    evaluaciones = 0
    def fallar_primera_evaluacion(*args, **kwargs):
        nonlocal evaluaciones
        evaluaciones += 1
        if evaluaciones == 1:
            raise ErrorDatos("Evaluación interrumpida para verificar recuperación.")
        return evaluar_real(*args, **kwargs)
    monkeypatch.setattr(manejadores, "evaluar_modelo", fallar_primera_evaluacion)
    cola = "e03_ml_" + uuid4().hex
    broker = os.environ["REDIS_URL"].rsplit("/",1)[0]+"/15"
    for clave, valor in {"broker_url":broker, "result_backend":broker, "task_default_queue":cola,
                         "beat_schedule":{"e03":{"task":"foodsave.despachar_pendientes","schedule":0.5}}}.items():
        monkeypatch.setitem(celery_app.conf, clave, valor)
    inicial = cargar(cliente, admin, entrega_historial(), {"fecha_objetivo_demo":"2022-06-20", "fecha_referencia_stock":"2022-06-19"})
    antes = conteos(sesiones)
    beat = Service(app=celery_app, max_interval=0.5, scheduler_cls="celery.beat:Scheduler")
    observado = set()
    reintentada = False
    with start_worker(celery_app, pool="solo", queues=[cola], perform_ping_check=False, shutdown_timeout=30):
        hilo = threading.Thread(target=beat.start, daemon=True); hilo.start()
        try:
            limite = time.monotonic()+180
            while time.monotonic() < limite:
                actual = estado(cliente, admin); observado.add(actual["estado"])
                assert actual["preparacion"]["estado"] != "FALLIDA", actual
                if actual["evaluacion"]:
                    if actual["evaluacion"]["estado"] == "FALLIDA":
                        assert not reintentada and actual["estado"] == "MODELO_LISTO"
                        assert conteos(sesiones) == antes
                        with sesiones() as sesion:
                            assert sesion.scalar(select(func.count()).select_from(ArtefactoModelo)) == 1
                        respuesta = cliente.post("/api/v1/inicializacion/reintentar-preparacion", headers=admin)
                        assert respuesta.status_code == 202, respuesta.text
                        assert respuesta.json()["datos"]["preparacion"]["id"] != inicial["preparacion"]["id"]
                        reintentada = True
                    elif actual["evaluacion"]["estado"] == "COMPLETADA": break
                time.sleep(0.1)
            else: pytest.fail(f"ML automático no terminó: {actual}")
        finally:
            beat.stop(wait=False); hilo.join(timeout=5)
    assert reintentada and evaluaciones == 2
    assert "ENTRENANDO" in observado
    assert actual["estado"] == "MODELO_LISTO" and actual["modelo_id"]
    reporte = cliente.get(f'/api/v1/pronosticos/evaluacion?modelo_id={actual["modelo_id"]}', headers=admin)
    assert reporte.status_code == 200, reporte.text
    assert reporte.json()["datos"]["total_pares_evaluables"] > 0
    assert conteos(sesiones) == antes
    assert cargar(cliente, admin, entrega_historial(), {"fecha_objetivo_demo":"2022-06-20", "fecha_referencia_stock":"2022-06-19"})["modelo_id"] == actual["modelo_id"]
    assert cliente.post("/api/v1/inicializacion/reintentar-preparacion", headers=admin).json()["datos"]["preparacion"]["id"] == actual["preparacion"]["id"]
    with sesiones() as sesion:
        assert sesion.scalar(select(func.count()).select_from(ArtefactoModelo)) == 1
        assert sesion.scalar(select(func.count()).select_from(EjecucionAutomatizacion)) == 4
    with celery_app.connection_for_write() as conexion:
        conexion.default_channel.queue_delete(cola)
