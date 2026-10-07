"""Primera carga HTTP → motor real → CatBoost → backtest; esquema aislado.

Por defecto SQLite; E03_POSTGRES_TEST=1 ejecuta la cadena Alembic completa en
un esquema e03_test_<uuid> de PostgreSQL sin tocar datos de la instalación.
"""

import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import Barrier
from uuid import uuid4

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite://")
os.environ.setdefault("JWT_SECRET", "clave-local-de-pruebas-e03-con-mas-de-32-caracteres")

import pytest
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.operations import Operations
from alembic.script import ScriptDirectory
from fastapi.testclient import TestClient
from pwdlib import PasswordHash
from sqlalchemy import create_engine, event, func, select, text
from sqlalchemy.orm import sessionmaker

from app.core.base import Base
from app.core.base_datos import obtener_sesion
from app.modules.autenticacion.modelos import Usuario
from app.modules.automatizaciones.modelos import EjecucionAutomatizacion, IntentoAutomatizacion
from app.modules.inicializacion.modelos import ConfiguracionInicial
from app.modules.inicializacion.preparacion import solicitar_preparacion_modelo
from app.modules.inventario.modelos import MovimientoInventario
from app.modules.negocios.modelos import Negocio
from app.modules.pronosticos import manejadores as ml
from app.modules.pronosticos.modelos import ArtefactoModelo, EvaluacionPronostico
from app.modules.ventas.modelos import VentaDiaria
from app.principal import app
from app.workers import motor
from app.workers.retry.politica import ErrorDatos, ErrorTransitorioInterno

MUESTRAS = Path(__file__).resolve().parents[1] / "fixtures" / "primera_carga"
FECHAS = {"fecha_objetivo_demo": "2022-09-24", "fecha_referencia_stock": "2022-09-23",
          "clave_importacion": "demo-completa-1"}


def archivos():
    return [("archivos", (p.name, p.read_bytes(), "text/csv")) for p in sorted(MUESTRAS.glob("*.csv"))]


@pytest.fixture
def entorno(tmp_path, monkeypatch):
    admin = None
    if os.getenv("E03_POSTGRES_TEST") == "1":
        assert os.environ["DATABASE_URL"].startswith("postgresql")
        esquema = "e03_test_" + uuid4().hex
        admin = create_engine(os.environ["DATABASE_URL"])
        with admin.begin() as c:
            c.execute(text(f'CREATE SCHEMA "{esquema}"'))
        engine = create_engine(os.environ["DATABASE_URL"], connect_args={"options": f"-csearch_path={esquema}"})
        config = Config()
        config.set_main_option("script_location", str(Path(__file__).resolve().parents[2] / "migrations"))
        with engine.begin() as c, Operations.context(MigrationContext.configure(c)):
            for revision in reversed(list(ScriptDirectory.from_config(config).walk_revisions())):
                revision.module.upgrade()
    else:
        engine = create_engine(f"sqlite:///{tmp_path / 'e03.db'}", connect_args={"check_same_thread": False})

        @event.listens_for(engine, "connect")
        def configurar(c, _):
            c.isolation_level = None
            c.create_function("char_length", 1, len)
            c.execute("PRAGMA foreign_keys=ON")

        @event.listens_for(engine, "begin")
        def iniciar_transaccion(conexion):
            conexion.exec_driver_sql("BEGIN")

        Base.metadata.create_all(engine)
    sesiones = sessionmaker(bind=engine, expire_on_commit=False)
    with sesiones.begin() as s:
        if s.get(Negocio, 1) is None:
            s.add(Negocio(id=1, nombre="Demo sintética", zona_horaria="America/Lima", moneda="PEN"))
        if s.get(ConfiguracionInicial, 1) is None:
            s.add(ConfiguracionInicial(id=1, estado="PENDIENTE"))
        for rol in ("ADMINISTRADOR", "OPERADOR"):
            s.add(Usuario(correo=f"{rol.lower()}@example.com", nombre=rol, rol=rol, activo=True,
                          hash_contrasena=PasswordHash.recommended().hash("clave-de-prueba")))
    monkeypatch.setattr(motor, "SessionLocal", sesiones)
    monkeypatch.setenv("MODEL_ARTIFACT_DIR", str(tmp_path / "modelos"))

    def sesion_api():
        with sesiones() as s:
            yield s

    app.dependency_overrides[obtener_sesion] = sesion_api
    try:
        with TestClient(app) as cliente:
            cabeceras = {}
            for rol in ("ADMINISTRADOR", "OPERADOR"):
                respuesta = cliente.post("/api/v1/autenticacion/iniciar-sesion", json={
                    "correo": f"{rol.lower()}@example.com", "contrasena": "clave-de-prueba"})
                cabeceras[rol] = {"Authorization": f'Bearer {respuesta.json()["datos"]["token_acceso"]}'}
            yield cliente, sesiones, cabeceras
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
        if admin is not None:
            with admin.begin() as c:
                c.execute(text(f'DROP SCHEMA "{esquema}" CASCADE'))
            admin.dispose()


def cargar(entorno):
    cliente, _, cabeceras = entorno
    respuesta = cliente.post("/api/v1/inicializacion/confirmar", data=FECHAS,
                             files=archivos(), headers=cabeceras["ADMINISTRADOR"])
    assert respuesta.status_code == 201, respuesta.text
    return cliente.get("/api/v1/inicializacion/estado", headers=cabeceras["ADMINISTRADOR"]).json()["datos"]["preparacion"]["id"]


def reclamar():
    mensajes = []
    motor.despachar_pendientes(lambda id_, token: mensajes.append((id_, token)))
    return mensajes


def contar(sesiones):
    with sesiones() as s:
        return tuple(s.scalar(select(func.count()).select_from(t))
                     for t in (VentaDiaria, MovimientoInventario, EjecucionAutomatizacion))


def test_carga_reserva_una_sola_tarea_y_rechaza_reintento_sin_permisos(entorno):
    cliente, sesiones, cabeceras = entorno
    assert cliente.post("/api/v1/inicializacion/reintentar-preparacion", json={"clave_idempotencia": "r1"},
                        headers=cabeceras["ADMINISTRADOR"]).status_code == 409
    id_ = cargar(entorno)
    antes = contar(sesiones)
    assert cargar(entorno) == id_
    assert contar(sesiones) == antes
    respuesta = cliente.post("/api/v1/inicializacion/reintentar-preparacion", json={"clave_idempotencia": "r1"},
                             headers=cabeceras["ADMINISTRADOR"])
    assert respuesta.json()["datos"]["preparacion"]["id"] == id_
    assert cliente.post("/api/v1/inicializacion/reintentar-preparacion", json={"clave_idempotencia": "r1"},
                        headers=cabeceras["OPERADOR"]).status_code == 403
    estado = cliente.get("/api/v1/inicializacion/estado", headers=cabeceras["OPERADOR"]).json()["datos"]
    assert estado["estado"] == "DATOS_CARGADOS"
    assert estado["preparacion"]["estado"] == "PENDIENTE"


def test_catboost_real_y_evaluacion_sin_reimportar(entorno, monkeypatch):
    cliente, sesiones, cabeceras = entorno
    id_ = cargar(entorno)
    real = ml.preparar_modelo

    def observar(sesion, **kwargs):
        # Otra conexión ve ENTRENANDO antes del cálculo largo.
        with sesiones() as lectura:
            assert lectura.get(ConfiguracionInicial, 1).estado == "ENTRENANDO"
        return real(sesion, **kwargs)

    monkeypatch.setattr(ml, "preparar_modelo", observar)
    mensaje = reclamar()[0]
    assert mensaje[0] == id_
    assert motor.ejecutar(*mensaje)["resultado"] == "COMPLETADA"
    assert motor.ejecutar(*mensaje)["resultado"] == "IGNORADA"
    estado = cliente.get("/api/v1/inicializacion/estado", headers=cabeceras["ADMINISTRADOR"]).json()["datos"]
    assert estado["estado"] == "MODELO_LISTO"
    assert estado["modelo_id"] is not None
    assert cargar(entorno) == id_
    evaluacion = reclamar()[0]
    assert motor.ejecutar(*evaluacion)["resultado"] == "COMPLETADA"
    assert motor.ejecutar(*evaluacion)["resultado"] == "IGNORADA"
    with sesiones() as s:
        assert s.scalar(select(func.count()).select_from(ArtefactoModelo)) == 1
        assert s.scalar(select(func.count()).select_from(EvaluacionPronostico)) > 0


def test_fallo_definitivo_reintenta_con_nueva_clave_sin_cargar(entorno, monkeypatch):
    cliente, sesiones, cabeceras = entorno
    cargar(entorno)
    antes = contar(sesiones)

    def fallar(*args, **kwargs):
        raise ErrorDatos("Historial de prueba insuficiente.")

    monkeypatch.setattr(ml, "preparar_modelo", fallar)
    assert motor.ejecutar(*reclamar()[0])["resultado"] == "FALLIDA"
    with sesiones() as s:
        estado = s.get(ConfiguracionInicial, 1)
        assert estado.estado == "DATOS_CARGADOS"
        assert "insuficiente" in estado.mensaje_error
    datos = {"clave_idempotencia": "corregido-1"}
    nuevo = cliente.post("/api/v1/inicializacion/reintentar-preparacion", json=datos,
                         headers=cabeceras["ADMINISTRADOR"]).json()["datos"]["preparacion"]["id"]
    assert cliente.post("/api/v1/inicializacion/reintentar-preparacion", json=datos,
                        headers=cabeceras["ADMINISTRADOR"]).json()["datos"]["preparacion"]["id"] == nuevo
    assert contar(sesiones) == (antes[0], antes[1], antes[2] + 1)
    assert motor.ejecutar(*reclamar()[0])["resultado"] == "FALLIDA"
    # El contrato conciliado reserva un intento nuevo tras cada fallo;
    # mientras siga activo, repetir lo recupera sin duplicar.
    tercero = cliente.post("/api/v1/inicializacion/reintentar-preparacion", headers=cabeceras["ADMINISTRADOR"]).json()["datos"]["preparacion"]["id"]
    assert tercero != nuevo
    assert contar(sesiones) == (antes[0], antes[1], antes[2] + 2)


def test_fallo_transitorio_y_recuperacion_de_worker_conservan_datos(entorno, monkeypatch):
    _, sesiones, _ = entorno
    id_ = cargar(entorno)
    antes = contar(sesiones)

    def fallar(*args, **kwargs):
        raise ErrorTransitorioInterno()

    monkeypatch.setattr(ml, "preparar_modelo", fallar)
    assert motor.ejecutar(*reclamar()[0])["resultado"] == "REINTENTANDO"
    with sesiones.begin() as s:
        assert s.get(ConfiguracionInicial, 1).estado == "DATOS_CARGADOS"
        e = s.get(EjecucionAutomatizacion, id_)
        e.proximo_intento_en = datetime.now(timezone.utc) - timedelta(seconds=1)
    mensaje = reclamar()[0]
    # Simular interrupción justo después del inicio durable del segundo intento.
    from app.modules.automatizaciones.servicio import iniciar_intento
    from app.workers.tasks.manejadores import notificar_inicio
    with sesiones.begin() as s:
        e = s.get(EjecucionAutomatizacion, id_)
        iniciar_intento(s, id_)
        from app.workers.tasks.manejadores import ContextoEjecucion
        notificar_inicio(s, ContextoEjecucion(e.id, e.tipo, e.clave_idempotencia, e.datos_entrada_json))
        e.lease_hasta = datetime.now(timezone.utc) - timedelta(seconds=1)
    assert motor.despachar_pendientes(lambda *_: None)["recuperadas"] == 1
    with sesiones() as s:
        assert s.get(ConfiguracionInicial, 1).estado == "DATOS_CARGADOS"
        assert "interrumpió" in s.get(ConfiguracionInicial, 1).mensaje_error
        assert s.scalar(select(func.count()).select_from(IntentoAutomatizacion)) == 2
    assert motor.ejecutar(*mensaje)["resultado"] == "IGNORADA"
    assert contar(sesiones) == antes


def test_rollback_de_reserva_no_deja_carga_ni_tarea(entorno, monkeypatch):
    cliente, sesiones, cabeceras = entorno
    from app.modules.inicializacion import servicio as preparacion

    def fallar(*args, **kwargs):
        raise ErrorAPI(503, "RESERVA_NO_DISPONIBLE", "Fallo inducido antes de confirmar.")

    from app.core.errores import ErrorAPI
    monkeypatch.setattr(preparacion, "crear_o_recuperar_ejecucion", fallar)
    respuesta = cliente.post("/api/v1/inicializacion/confirmar", data=FECHAS,
                             files=archivos(), headers=cabeceras["ADMINISTRADOR"])
    assert respuesta.status_code == 503
    assert contar(sesiones) == (0, 0, 0)


def test_reservas_concurrentes_son_una_sola_preparacion(entorno, monkeypatch):
    if os.getenv("E03_POSTGRES_TEST") != "1":
        pytest.skip("La serialización concurrente requiere PostgreSQL")
    _, sesiones, _ = entorno
    id_ = cargar(entorno)

    def fallar(*args, **kwargs):
        raise ErrorDatos("Fallo definitivo inducido.")

    monkeypatch.setattr(ml, "preparar_modelo", fallar)
    assert motor.ejecutar(*reclamar()[0])["resultado"] == "FALLIDA"
    barrera = Barrier(2)

    def reservar(_):
        with sesiones.begin() as s:
            barrera.wait(timeout=10)
            return solicitar_preparacion_modelo(s, str(uuid4())).id

    with ThreadPoolExecutor(max_workers=2) as pool:
        resultados = list(pool.map(reservar, range(2)))
        assert resultados[0] == resultados[1] != id_
    assert contar(sesiones)[2] == 2


def test_confirmaciones_concurrentes_no_duplican_apertura(entorno):
    if os.getenv("E03_POSTGRES_TEST") != "1":
        pytest.skip("La carga concurrente requiere PostgreSQL")
    _, sesiones, _ = entorno
    barrera = Barrier(2)

    def confirmar(_):
        barrera.wait(timeout=10)
        return cargar(entorno)

    with ThreadPoolExecutor(max_workers=2) as pool:
        resultados = list(pool.map(confirmar, range(2)))
    assert resultados[0] == resultados[1]
    assert contar(sesiones)[1:] == (3, 1)


def test_carga_dispara_worker_y_beat_reales(entorno):
    if os.getenv("E03_POSTGRES_TEST") != "1":
        pytest.skip("Beat y worker requieren PostgreSQL y Redis")
    from celery.beat import Service
    from celery.contrib.testing.worker import start_worker
    from app.workers.celery_app import celery_app

    cliente, sesiones, cabeceras = entorno
    cola = "e03_test_" + uuid4().hex
    configuracion_previa = {k: celery_app.conf[k] for k in (
        "broker_url", "result_backend", "task_default_queue", "beat_schedule")}
    redis_pruebas = os.environ["REDIS_URL"].rsplit("/", 1)[0] + "/15"
    celery_app.conf.update(broker_url=redis_pruebas, result_backend=redis_pruebas,
                          task_default_queue=cola, beat_schedule={"e03": {
                              "task": "foodsave.despachar_pendientes", "schedule": 0.5,
                              "options": {"queue": cola}}})
    beat = Service(app=celery_app, max_interval=0.5, scheduler_cls="celery.beat:Scheduler")
    try:
        with start_worker(celery_app, pool="solo", queues=[cola], perform_ping_check=False, shutdown_timeout=20):
            cargar(entorno)
            hilo = threading.Thread(target=beat.start, daemon=True)
            hilo.start()
            try:
                limite = time.monotonic() + 90
                while time.monotonic() < limite:
                    with sesiones() as s:
                        tareas = s.scalars(select(EjecucionAutomatizacion)).all()
                        if len(tareas) == 2 and all(e.estado == "COMPLETADA" for e in tareas):
                            break
                    time.sleep(0.2)
                else:
                    pytest.fail("Beat y worker no completaron preparación y backtest en 90 segundos")
                estado = cliente.get("/api/v1/inicializacion/estado", headers=cabeceras["ADMINISTRADOR"]).json()["datos"]
                assert estado["estado"] == "MODELO_LISTO"
                assert estado["preparacion"]["estado"] == "COMPLETADA"
                with sesiones() as s:
                    assert s.scalar(select(func.count()).select_from(EvaluacionPronostico)) > 0
                # Siguiente frontera real: HTTP → Beat → inferencia → plan → evaluación.
                from app.modules.productos.modelos import Producto
                from app.modules.planificacion.modelos import PlanProduccion
                with sesiones() as s:
                    ids = list(s.scalars(select(Producto.id).order_by(Producto.id)))
                    movimientos = s.scalar(select(func.count()).select_from(MovimientoInventario))
                programada = cliente.post("/api/v1/programaciones-demo", headers=cabeceras["ADMINISTRADOR"], json={
                    "tipo": "GENERAR_PROPUESTA", "ejecutar_desde_utc": (datetime.now(timezone.utc) + timedelta(seconds=1)).isoformat(),
                    "fecha_hora_simulada_local": "2022-09-24T10:00:00", "fecha_objetivo_demo": "2022-09-24",
                    "producto_ids": ids, "clave_idempotencia": "propuesta-beat-real"})
                assert programada.status_code == 200, programada.text
                ejecucion_id = programada.json()["datos"]["ejecucion_id"]
                limite = time.monotonic() + 30
                while time.monotonic() < limite:
                    with sesiones() as s:
                        ejecucion = s.get(EjecucionAutomatizacion, ejecucion_id)
                        if ejecucion.estado == "COMPLETADA":
                            salida = ejecucion.datos_salida_json
                            evaluacion = s.get(EjecucionAutomatizacion, salida["evaluacion_ejecucion_id"])
                            if evaluacion.estado == "COMPLETADA":
                                break
                        assert ejecucion.estado != "FALLIDA", ejecucion.mensaje_error
                    time.sleep(0.2)
                else:
                    pytest.fail("La propuesta programada no completó plan y evaluación")
                detalle = cliente.get(f'/api/v1/planes/{salida["plan_id"]}', headers=cabeceras["OPERADOR"])
                assert detalle.status_code == 200
                assert len(detalle.json()["datos"]["elementos"]) == 3
                assert salida["pedidos_estado"] == "BLOQUEADA"
                with sesiones() as s:
                    assert s.scalar(select(func.count()).select_from(PlanProduccion)) == 1
                    assert s.scalar(select(func.count()).select_from(MovimientoInventario)) == movimientos
            finally:
                beat.stop(wait=False)
                hilo.join(timeout=5)
        with celery_app.connection_for_write() as conexion:
            conexion.default_channel.queue_delete(cola)
    finally:
        celery_app.conf.update(**configuracion_previa)
