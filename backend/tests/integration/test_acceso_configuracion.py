"""Contrato A01: identidad, permisos, validación y persistencia."""

import os
import time

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite://")
os.environ.setdefault("JWT_SECRET", "clave-local-para-pruebas-de-acceso-a01")

import pytest
import jwt
from fastapi.testclient import TestClient
from pwdlib import PasswordHash
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.base import Base
from app.core.base_datos import obtener_sesion
from app.modules.autenticacion.modelos import Usuario
from app.modules.negocios.modelos import Negocio
from app.principal import app


@pytest.fixture
def cliente():
    motor = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(motor, "connect")
    def registrar_char_length(conexion, _registro):
        conexion.create_function("char_length", 1, len)

    Base.metadata.create_all(motor)
    cifrador = PasswordHash.recommended()
    with Session(motor) as sesion:
        sesion.add(Negocio(id=1, nombre="Prueba", zona_horaria="America/Lima", moneda="PEN"))
        sesion.add_all(
            [
                Usuario(correo="admin@example.com", nombre="Admin", rol="ADMINISTRADOR", activo=True,
                        hash_contrasena=cifrador.hash("clave-segura-admin")),
                Usuario(correo="operador@example.com", nombre="Operador", rol="OPERADOR", activo=True,
                        hash_contrasena=cifrador.hash("clave-segura-operador")),
                Usuario(correo="inactivo@example.com", nombre="Inactivo", rol="OPERADOR", activo=False,
                        hash_contrasena=cifrador.hash("clave-segura-inactivo")),
            ]
        )
        sesion.commit()

    def sesion_de_prueba():
        with Session(motor) as sesion:
            yield sesion

    app.dependency_overrides[obtener_sesion] = sesion_de_prueba
    with TestClient(app) as prueba:
        yield prueba
    app.dependency_overrides.clear()
    motor.dispose()


def token(cliente: TestClient, correo: str, contrasena: str) -> str:
    respuesta = cliente.post("/api/v1/autenticacion/iniciar-sesion", json={"correo": correo, "contrasena": contrasena})
    assert respuesta.status_code == 200
    return respuesta.json()["datos"]["token_acceso"]


def cabecera(token_acceso: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token_acceso}"}


def test_identidad_y_permisos(cliente: TestClient):
    ruta = "/api/v1/negocios/actual"
    sin_sesion = cliente.get(ruta)
    assert sin_sesion.status_code == 401
    assert sin_sesion.json()["error"]["codigo"] == "AUTENTICACION_REQUERIDA"

    invalida = cliente.get(ruta, headers=cabecera("token-invalido"))
    assert invalida.status_code == 401
    assert invalida.json()["error"]["codigo"] == "CREDENCIAL_INVALIDA"

    administrador = token(cliente, "admin@example.com", "clave-segura-admin")
    payload = jwt.decode(administrador, os.environ["JWT_SECRET"], algorithms=["HS256"])
    payload["exp"] = int(time.time()) - 1
    expirada = cliente.get(ruta, headers=cabecera(jwt.encode(payload, os.environ["JWT_SECRET"], algorithm="HS256")))
    assert expirada.status_code == 401
    assert expirada.json()["error"]["codigo"] == "CREDENCIAL_INVALIDA"

    operador = token(cliente, "operador@example.com", "clave-segura-operador")
    assert cliente.get(ruta, headers=cabecera(operador)).status_code == 200
    prohibido = cliente.patch(ruta, headers=cabecera(operador), json={"moneda": "USD"})
    assert prohibido.status_code == 403
    assert prohibido.json() == {"error": {"codigo": "PERMISO_DENEGADO", "mensaje": "Se requiere administrador"}}

    inactivo = cliente.post(
        "/api/v1/autenticacion/iniciar-sesion",
        json={"correo": "inactivo@example.com", "contrasena": "clave-segura-inactivo"},
    )
    assert inactivo.status_code == 401
    assert inactivo.json()["error"]["codigo"] == "CREDENCIALES_INVALIDAS"


@pytest.mark.parametrize("cambio", [
    {"zona_horaria": "America/NoExiste"},
    {"moneda": "P1N"},
    {"moneda": "pen"},
    {"nombre": "   "},
    {"modo_envio_pedidos": "NO_VALIDO"},
    {"zona_horaria": None},
    {},
])
def test_configuracion_invalida_no_persiste(cliente: TestClient, cambio: dict):
    administrador = token(cliente, "admin@example.com", "clave-segura-admin")
    ruta = "/api/v1/negocios/actual"
    anterior = cliente.get(ruta, headers=cabecera(administrador)).json()["datos"]
    respuesta = cliente.patch(ruta, headers=cabecera(administrador), json=cambio)
    assert respuesta.status_code == 422
    assert respuesta.json()["error"]["codigo"] == "DATOS_INVALIDOS"
    assert respuesta.json()["error"]["detalles"]
    assert cliente.get(ruta, headers=cabecera(administrador)).json()["datos"] == anterior


def test_administrador_actualiza_modo_y_perfil(cliente: TestClient):
    administrador = token(cliente, "admin@example.com", "clave-segura-admin")
    perfil = cliente.get("/api/v1/autenticacion/mi-perfil", headers=cabecera(administrador))
    assert perfil.json()["datos"]["rol"] == "ADMINISTRADOR"

    ruta = "/api/v1/negocios/actual"
    respuesta = cliente.patch(
        ruta, headers=cabecera(administrador),
        json={"zona_horaria": "America/Bogota", "moneda": "USD", "modo_envio_pedidos": "AUTOMATICO"},
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["datos"]["modo_envio_pedidos"] == "AUTOMATICO"
    assert cliente.get(ruta, headers=cabecera(administrador)).json()["datos"]["moneda"] == "USD"


def test_cambio_mixto_invalido_no_guarda_campos_validos(cliente: TestClient):
    administrador = token(cliente, "admin@example.com", "clave-segura-admin")
    ruta = "/api/v1/negocios/actual"
    respuesta = cliente.patch(
        ruta, headers=cabecera(administrador),
        json={"nombre": "Otro comercio", "zona_horaria": "America/NoExiste"},
    )
    assert respuesta.status_code == 422
    assert cliente.get(ruta, headers=cabecera(administrador)).json()["datos"]["nombre"] == "Prueba"


def test_ruta_ausente_usa_sobre_de_error(cliente: TestClient):
    respuesta = cliente.get("/api/v1/no-existe")
    assert respuesta.status_code == 404
    assert respuesta.json()["error"]["codigo"] == "NO_ENCONTRADO"
