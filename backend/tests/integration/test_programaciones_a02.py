"""Contrato A02: programación idempotente y trazas de intentos."""

import os
from datetime import datetime, timedelta, timezone

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite://")
os.environ.setdefault("JWT_SECRET", "clave-local-para-pruebas-de-acceso-a01")

import pytest
from fastapi.testclient import TestClient
from pwdlib import PasswordHash
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.base import Base
from app.core.base_datos import obtener_sesion
from app.core.errores import ErrorAPI
from app.modules.autenticacion.modelos import Usuario
from app.modules.automatizaciones.modelos import EjecucionAutomatizacion
from app.modules.automatizaciones.servicio import crear_o_recuperar_ejecucion, finalizar_intento, iniciar_intento
from app.modules.negocios.modelos import Negocio
from app.principal import app


@pytest.fixture
def entorno():
    motor = create_engine("sqlite+pysqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)

    @event.listens_for(motor, "connect")
    def registrar_char_length(conexion, _registro):
        conexion.isolation_level = None
        conexion.create_function("char_length", 1, len)

    @event.listens_for(motor, "begin")
    def iniciar_transaccion(conexion):
        conexion.exec_driver_sql("BEGIN")

    Base.metadata.create_all(motor)
    cifrador = PasswordHash.recommended()
    with Session(motor) as sesion:
        sesion.add(Negocio(id=1, nombre="Prueba", zona_horaria="America/Lima", moneda="PEN"))
        sesion.add_all([
            Usuario(correo="admin@example.com", nombre="Admin", rol="ADMINISTRADOR", activo=True,
                    hash_contrasena=cifrador.hash("clave-segura-admin")),
            Usuario(correo="operador@example.com", nombre="Operador", rol="OPERADOR", activo=True,
                    hash_contrasena=cifrador.hash("clave-segura-operador")),
        ])
        sesion.commit()

    def sesion_de_prueba():
        with Session(motor) as sesion:
            yield sesion

    app.dependency_overrides[obtener_sesion] = sesion_de_prueba
    with TestClient(app) as cliente:
        yield cliente, motor
    app.dependency_overrides.clear()
    motor.dispose()


def _token(cliente: TestClient, correo: str, contrasena: str) -> str:
    respuesta = cliente.post("/api/v1/autenticacion/iniciar-sesion", json={"correo": correo, "contrasena": contrasena})
    assert respuesta.status_code == 200
    return respuesta.json()["datos"]["token_acceso"]


def _cabecera(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _programacion() -> dict:
    return {
        "tipo": "GENERAR_PROPUESTA",
        "ejecutar_desde_utc": (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat(),
        "fecha_hora_simulada_local": "2022-08-24T10:00:00",
        "fecha_objetivo_demo": "2022-08-24",
        "producto_ids": [3, 1, 2],
        "clave_idempotencia": "demo-2022-08-24-v1",
    }


def test_programacion_api_idempotencia_y_consulta(entorno):
    cliente, _motor = entorno
    administrador = _token(cliente, "admin@example.com", "clave-segura-admin")
    ruta = "/api/v1/programaciones-demo"
    datos = _programacion()

    creada = cliente.post(ruta, headers=_cabecera(administrador), json=datos)
    assert creada.status_code == 200
    registro = creada.json()["datos"]
    assert registro["estado"] == "PROGRAMADA"
    assert registro["parametros"] == {"fecha_objetivo_demo": "2022-08-24", "producto_ids": [1, 2, 3]}
    assert registro["ejecucion_id"] is not None
    assert registro["despachada_en"] is None

    repetida = cliente.post(ruta, headers=_cabecera(administrador), json={**datos, "producto_ids": [2, 3, 1]})
    assert repetida.status_code == 200
    assert repetida.json()["datos"]["id"] == registro["id"]
    assert len(cliente.get(ruta, headers=_cabecera(administrador)).json()["datos"]) == 1

    detalle = cliente.get(f"{ruta}/{registro['id']}", headers=_cabecera(administrador))
    assert detalle.json()["datos"]["fecha_hora_simulada_local"] == "2022-08-24T10:00:00"
    ejecucion = cliente.get(f"/api/v1/ejecuciones-automatizacion/{registro['ejecucion_id']}", headers=_cabecera(administrador))
    assert ejecucion.status_code == 200
    assert ejecucion.json()["datos"]["estado"] == "PENDIENTE"
    assert ejecucion.json()["datos"]["intentos"] == []
    assert len(cliente.get("/api/v1/ejecuciones-automatizacion", headers=_cabecera(administrador)).json()["datos"]) == 1

    conflicto = cliente.post(ruta, headers=_cabecera(administrador), json={**datos, "producto_ids": [1, 4]})
    assert conflicto.status_code == 409
    assert conflicto.json()["error"]["codigo"] == "CLAVE_REUTILIZADA"
    assert len(cliente.get(ruta, headers=_cabecera(administrador)).json()["datos"]) == 1


def test_programacion_permisos_y_validacion(entorno):
    cliente, _motor = entorno
    ruta = "/api/v1/programaciones-demo"
    assert cliente.get(ruta).status_code == 401
    operador = _token(cliente, "operador@example.com", "clave-segura-operador")
    assert cliente.post(ruta, headers=_cabecera(operador), json=_programacion()).status_code == 403
    administrador = _token(cliente, "admin@example.com", "clave-segura-admin")

    datos = _programacion()
    casos_422 = [
        {**datos, "ejecutar_desde_utc": "2026-09-27T10:00:00"},
        {**datos, "fecha_hora_simulada_local": "2022-08-24T10:00:00Z"},
        {**datos, "fecha_objetivo_demo": "2022-08-25"},
        {**datos, "producto_ids": [1, 1]},
        {**datos, "producto_ids": []},
        {**datos, "clave_idempotencia": "clave con espacios"},
    ]
    for caso in casos_422:
        respuesta = cliente.post(ruta, headers=_cabecera(administrador), json=caso)
        assert respuesta.status_code == 422
        assert respuesta.json()["error"]["codigo"] == "DATOS_INVALIDOS"

    pasado = cliente.post(
        ruta, headers=_cabecera(administrador),
        json={**datos, "ejecutar_desde_utc": (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()},
    )
    assert pasado.status_code == 400
    assert pasado.json()["error"]["codigo"] == "HORA_NO_FUTURA"
    assert cliente.get(ruta, headers=_cabecera(administrador)).json()["datos"] == []
    assert cliente.get(f"{ruta}/999", headers=_cabecera(administrador)).status_code == 404


def test_frontera_de_eventos_no_confirma_y_guarda_intentos(entorno):
    _cliente, motor = entorno
    with Session(motor) as sesion:
        ejecucion = crear_o_recuperar_ejecucion(
            sesion, "PREPARAR_MODELO", "carga-huella-1", {"importacion_id": 7}
        )
        ejecucion_id = ejecucion.id
        sesion.rollback()
    with Session(motor) as sesion:
        assert sesion.get(EjecucionAutomatizacion, ejecucion_id) is None
        ejecucion = crear_o_recuperar_ejecucion(
            sesion, "PREPARAR_MODELO", "carga-huella-1", {"importacion_id": 7}
        )
        sesion.commit()
        assert crear_o_recuperar_ejecucion(
            sesion, "PREPARAR_MODELO", "carga-huella-1", {"importacion_id": 7}
        ).id == ejecucion.id
        with pytest.raises(ErrorAPI) as error:
            crear_o_recuperar_ejecucion(sesion, "PREPARAR_MODELO", "carga-huella-1", {"importacion_id": 8})
        assert error.value.status_code == 409

        intento = iniciar_intento(sesion, ejecucion.id)
        assert intento.numero_intento == 1
        assert iniciar_intento(sesion, ejecucion.id).id == intento.id
        finalizar_intento(sesion, intento.id, "REINTENTANDO", mensaje_error="Redis temporalmente caído",
                         proximo_intento_en=datetime.now(timezone.utc) + timedelta(minutes=1))
        sesion.commit()

        segundo = iniciar_intento(sesion, ejecucion.id)
        assert segundo.numero_intento == 2
        finalizar_intento(sesion, segundo.id, "COMPLETADA", datos_salida={"artefacto_id": 9})
        sesion.commit()
        with pytest.raises(ErrorAPI) as error:
            iniciar_intento(sesion, ejecucion.id)
        assert error.value.status_code == 409

    with Session(motor) as sesion:
        guardada = sesion.scalar(select(EjecucionAutomatizacion).where(EjecucionAutomatizacion.clave_idempotencia == "carga-huella-1"))
        assert guardada.estado == "COMPLETADA"
        assert guardada.datos_salida_json == {"artefacto_id": 9}
