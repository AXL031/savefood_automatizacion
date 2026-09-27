"""A03 sobre PostgreSQL aislado; activar con A03_POSTGRES_TEST=1.

Cada prueba crea y elimina únicamente su esquema a03_test_<uuid>.
La prueba Celery usa una cola única y Redis DB 15, sin tocar colas de la demo.
"""

import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import sessionmaker

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite://")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")

from app.core.base import Base
from app.modules.automatizaciones.modelos import EjecucionAutomatizacion, IntentoAutomatizacion, ProgramacionDemo
from app.modules.automatizaciones.servicio import crear_o_recuperar_ejecucion, programar_ejecucion
from app.workers import motor
from app.workers.retry.politica import ErrorDatos, ErrorTransitorioInterno, es_transitorio, siguiente_intento
from app.workers.tasks.manejadores import MANEJADORES


def test_politica_interna_y_limite():
    ahora = datetime.now(timezone.utc)
    assert es_transitorio(ErrorTransitorioInterno())
    assert not es_transitorio(TimeoutError("envío externo incierto"))
    assert not es_transitorio(ErrorDatos("modelo ausente"))
    assert 60 <= (siguiente_intento(1, ahora) - ahora).total_seconds() <= 65
    assert 120 <= (siguiente_intento(2, ahora) - ahora).total_seconds() <= 125
    assert siguiente_intento(3, ahora) is None


@pytest.fixture
def entorno_pg(monkeypatch):
    if os.getenv("A03_POSTGRES_TEST") != "1":
        pytest.skip("A03_POSTGRES_TEST=1 requiere PostgreSQL para verificar bloqueos reales")
    url = os.environ["DATABASE_URL"]
    assert url.startswith("postgresql"), "Las pruebas de concurrencia requieren PostgreSQL"
    esquema = "a03_test_" + uuid4().hex
    admin = create_engine(url)
    with admin.begin() as conexion:
        conexion.execute(text(f'CREATE SCHEMA "{esquema}"'))
    engine = create_engine(url, connect_args={"options": f"-csearch_path={esquema}"})
    try:
        Base.metadata.create_all(engine)
        with engine.begin() as conexion:
            conexion.execute(text("CREATE TABLE prueba_efecto (ejecucion_id integer PRIMARY KEY, valor integer NOT NULL)"))
        sesiones = sessionmaker(bind=engine, expire_on_commit=False)
        monkeypatch.setattr(motor, "SessionLocal", sesiones)
        monkeypatch.setitem(MANEJADORES, "EVALUAR_MODELO", _efecto)
        yield sesiones
    finally:
        engine.dispose()
        with admin.begin() as conexion:
            conexion.execute(text(f'DROP SCHEMA "{esquema}" CASCADE'))
        admin.dispose()


def _efecto(sesion, contexto):
    sesion.execute(text("INSERT INTO prueba_efecto VALUES (:id, 1)"), {"id": contexto.id})
    return {"prueba_controlada": True, "ejecucion_id": contexto.id}


def _evento(sesiones):
    with sesiones.begin() as sesion:
        return crear_o_recuperar_ejecucion(sesion, "EVALUAR_MODELO", str(uuid4()), {"fixture": True}).id


def _reclamar():
    mensajes = []
    motor.despachar_pendientes(lambda id_, token: mensajes.append((id_, token)))
    return mensajes


def _vencer(sesiones, id_):
    with sesiones.begin() as sesion:
        ejecucion = sesion.get(EjecucionAutomatizacion, id_)
        ejecucion.lease_hasta = datetime.now(timezone.utc) - timedelta(seconds=1)
        if ejecucion.proximo_intento_en:
            ejecucion.proximo_intento_en = datetime.now(timezone.utc) - timedelta(seconds=1)


def test_commit_antes_de_publicar_y_recuperacion_de_redis(entorno_pg):
    sesiones = entorno_pg
    with sesiones() as sesion:
        rollback_id = crear_o_recuperar_ejecucion(sesion, "EVALUAR_MODELO", "no-confirmado", {}).id
        assert _reclamar() == []
        sesion.rollback()
    id_ = _evento(sesiones)
    primera = []

    def redis_caido(id_, token):
        # Otra conexión ya ve el reclamo: no se publica antes del commit.
        with sesiones() as sesion:
            assert sesion.get(EjecucionAutomatizacion, id_).token_despacho == token
        primera.append((id_, token))
        raise ConnectionError("Redis no disponible")

    assert motor.despachar_pendientes(redis_caido)["publicadas"] == 0
    assert _reclamar() == []
    _vencer(sesiones, id_)
    segunda = _reclamar()
    assert segunda[0][0] == id_
    assert segunda[0][1] != primera[0][1]
    assert motor.ejecutar(*primera[0])["resultado"] == "IGNORADA"
    assert motor.ejecutar(*segunda[0])["resultado"] == "COMPLETADA"
    assert motor.ejecutar(*segunda[0])["resultado"] == "IGNORADA"
    with sesiones() as sesion:
        assert sesion.get(EjecucionAutomatizacion, rollback_id) is None
        assert sesion.scalar(text("SELECT count(*) FROM prueba_efecto")) == 1
        assert len(sesion.scalars(select(IntentoAutomatizacion)).all()) == 1


def test_despachadores_y_workers_concurrentes_no_duplican(entorno_pg, monkeypatch):
    sesiones = entorno_pg
    id_ = _evento(sesiones)
    with ThreadPoolExecutor(max_workers=2) as pool:
        respuestas = list(pool.map(lambda _: _reclamar(), range(2)))
    mensajes = [mensaje for respuesta in respuestas for mensaje in respuesta]
    assert len(mensajes) == 1
    dentro = threading.Event()
    continuar = threading.Event()

    def efecto_lento(sesion, contexto):
        _efecto(sesion, contexto)
        dentro.set()
        assert continuar.wait(10)
        return {"prueba_controlada": True}

    monkeypatch.setitem(MANEJADORES, "EVALUAR_MODELO", efecto_lento)
    with ThreadPoolExecutor(max_workers=1) as pool:
        futuro = pool.submit(motor.ejecutar, *mensajes[0])
        try:
            assert dentro.wait(10)
            assert motor.ejecutar(*mensajes[0])["resultado"] == "IGNORADA"
            # Ni siquiera un lease vencido permite reclamar una transacción activa.
            assert motor.despachar_pendientes(lambda *_: pytest.fail("duplicado"),
                ahora=datetime.now(timezone.utc) + timedelta(hours=1))["reclamadas"] == 0
        finally:
            continuar.set()
        assert futuro.result(timeout=10)["resultado"] == "COMPLETADA"
    with sesiones() as sesion:
        assert sesion.scalar(text("SELECT count(*) FROM prueba_efecto")) == 1
        assert sesion.get(EjecucionAutomatizacion, id_).lease_hasta is None


def test_caida_worker_revierte_efecto_y_recupera_intento(entorno_pg, monkeypatch):
    sesiones = entorno_pg
    id_ = _evento(sesiones)
    mensaje = _reclamar()[0]

    def caer(sesion, contexto):
        _efecto(sesion, contexto)
        raise SystemExit("simula proceso interrumpido antes del commit")

    monkeypatch.setitem(MANEJADORES, "EVALUAR_MODELO", caer)
    with pytest.raises(SystemExit):
        motor.ejecutar(*mensaje)
    with sesiones() as sesion:
        assert sesion.scalar(text("SELECT count(*) FROM prueba_efecto")) == 0
        assert sesion.get(EjecucionAutomatizacion, id_).estado == "EN_EJECUCION"
    _vencer(sesiones, id_)
    assert motor.despachar_pendientes(lambda *_: pytest.fail("debe esperar backoff"))["recuperadas"] == 1
    assert _reclamar() == []
    assert motor.ejecutar(*mensaje)["resultado"] == "IGNORADA"
    _vencer(sesiones, id_)
    monkeypatch.setitem(MANEJADORES, "EVALUAR_MODELO", _efecto)
    assert motor.ejecutar(*_reclamar()[0])["resultado"] == "COMPLETADA"
    with sesiones() as sesion:
        intentos = sesion.scalars(select(IntentoAutomatizacion).order_by(IntentoAutomatizacion.numero_intento)).all()
        assert [i.estado for i in intentos] == ["FALLIDA", "COMPLETADA"]
        assert sesion.scalar(text("SELECT count(*) FROM prueba_efecto")) == 1


def test_reintentos_agotan_cupo_y_revierten_efectos(entorno_pg, monkeypatch):
    sesiones = entorno_pg
    id_ = _evento(sesiones)

    def fallar(sesion, contexto):
        _efecto(sesion, contexto)
        raise ErrorTransitorioInterno("detalle interno que no debe exponerse")

    monkeypatch.setitem(MANEJADORES, "EVALUAR_MODELO", fallar)
    for numero in range(1, 4):
        resultado = motor.ejecutar(*_reclamar()[0])
        assert resultado["resultado"] == ("REINTENTANDO" if numero < 3 else "FALLIDA")
        assert _reclamar() == []
        with sesiones() as sesion:
            ejecucion = sesion.get(EjecucionAutomatizacion, id_)
            assert "detalle interno" not in ejecucion.mensaje_error
            assert sesion.scalar(text("SELECT count(*) FROM prueba_efecto")) == 0
        _vencer(sesiones, id_)
    assert _reclamar() == []
    with sesiones() as sesion:
        assert len(sesion.scalars(select(IntentoAutomatizacion)).all()) == 3


@pytest.mark.parametrize("error", [ErrorDatos("Falta receta"), TimeoutError("Telegram incierto")])
def test_errores_definitivos_no_reintentan(entorno_pg, monkeypatch, error):
    sesiones = entorno_pg
    _evento(sesiones)

    def fallar(sesion, contexto):
        _efecto(sesion, contexto)
        raise error

    monkeypatch.setitem(MANEJADORES, "EVALUAR_MODELO", fallar)
    assert motor.ejecutar(*_reclamar()[0])["resultado"] == "FALLIDA"
    assert _reclamar() == []
    with sesiones() as sesion:
        assert sesion.scalar(text("SELECT count(*) FROM prueba_efecto")) == 0


def test_programaciones_respetan_hora_cancelacion_y_servicio_ausente(entorno_pg):
    sesiones = entorno_pg
    ahora = datetime.now(timezone.utc)
    with sesiones.begin() as sesion:
        futura = programar_ejecucion(sesion, tipo="EVALUAR_PROMOCION",
            ejecutar_desde_utc=ahora + timedelta(hours=1), fecha_hora_simulada_local=datetime(2022, 8, 24, 18),
            parametros={"lote_producto_id": 1}, clave_idempotencia="promocion-futura")
        cancelada = programar_ejecucion(sesion, tipo="GENERAR_PROPUESTA",
            ejecutar_desde_utc=ahora + timedelta(hours=1), fecha_hora_simulada_local=datetime(2022, 8, 24, 10),
            parametros={"fixture": True}, clave_idempotencia="propuesta-cancelada")
        cancelada.estado = "CANCELADA"
        cancelada.ejecutar_desde_utc = ahora - timedelta(seconds=1)
    assert _reclamar() == []
    with sesiones.begin() as sesion:
        sesion.get(ProgramacionDemo, futura.id).ejecutar_desde_utc = ahora - timedelta(seconds=1)
    mensajes = _reclamar()
    assert len(mensajes) == 1
    assert motor.ejecutar(*mensajes[0])["resultado"] == "FALLIDA"
    with sesiones() as sesion:
        ejecucion = sesion.get(EjecucionAutomatizacion, mensajes[0][0])
        assert "pendiente de integración" in ejecucion.mensaje_error
        assert ejecucion.datos_salida_json is None
        assert sesion.get(ProgramacionDemo, futura.id).estado == "DESPACHADA"


def test_beat_redis_worker_completa_evento_y_programacion_sin_despacho_manual(entorno_pg, monkeypatch):
    from celery.beat import Service
    from celery.contrib.testing.worker import start_worker
    from app.workers.celery_app import celery_app

    sesiones = entorno_pg
    cola = "a03_test_" + uuid4().hex
    broker = os.environ["REDIS_URL"].rsplit("/", 1)[0] + "/15"
    configuracion = {
        "broker_url": broker, "result_backend": broker, "task_default_queue": cola,
        "beat_schedule": {"prueba": {"task": "foodsave.despachar_pendientes", "schedule": 0.5}},
    }
    for clave, valor in configuracion.items():
        monkeypatch.setitem(celery_app.conf, clave, valor)
    id_ = _evento(sesiones)
    monkeypatch.setitem(MANEJADORES, "GENERAR_PROPUESTA", _efecto)
    with sesiones.begin() as sesion:
        programacion = programar_ejecucion(sesion, tipo="GENERAR_PROPUESTA",
            ejecutar_desde_utc=datetime.now(timezone.utc) + timedelta(seconds=2),
            fecha_hora_simulada_local=datetime(2022, 8, 24, 10),
            parametros={"fixture": True}, clave_idempotencia="beat-programacion")
        programada_id = sesion.scalar(select(EjecucionAutomatizacion.id).where(
            EjecucionAutomatizacion.programacion_id == programacion.id))
    beat = Service(app=celery_app, max_interval=0.5, scheduler_cls="celery.beat:Scheduler")
    with start_worker(celery_app, pool="solo", queues=[cola], perform_ping_check=False, shutdown_timeout=10):
        hilo = threading.Thread(target=beat.start, daemon=True)
        hilo.start()
        try:
            limite = time.monotonic() + 15
            while time.monotonic() < limite:
                with sesiones() as sesion:
                    if all(sesion.get(EjecucionAutomatizacion, eid).estado == "COMPLETADA"
                           for eid in (id_, programada_id)):
                        break
                time.sleep(0.1)
            else:
                pytest.fail("Beat + Redis + worker no completaron el evento en 15 segundos")
            with sesiones() as sesion:
                assert sesion.scalar(text("SELECT count(*) FROM prueba_efecto")) == 2
                assert sesion.get(ProgramacionDemo, programacion.id).estado == "DESPACHADA"
        finally:
            beat.stop(wait=False)
            hilo.join(timeout=5)
    with celery_app.connection_for_write() as conexion:
        conexion.default_channel.queue_delete(cola)
