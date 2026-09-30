"""La carga web del piloto protege datos y agenda ML en una sola transacción."""

import os

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite://")
os.environ.setdefault("JWT_SECRET", "clave-local-larga-para-pruebas-de-carga-csv")

import pytest
from fastapi.testclient import TestClient
from pwdlib import PasswordHash
from sqlalchemy import create_engine, event, select, func
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.base import Base
from app.core.base_datos import obtener_sesion
from app.modules.autenticacion.modelos import Usuario
from app.modules.automatizaciones.modelos import EjecucionAutomatizacion
from app.modules.inicializacion import piloto as rutas
from app.modules.negocios.modelos import Negocio
from app.modules.productos.modelos import Producto
from app.modules.ventas.modelos import ImportacionVenta, VentaDiaria
from app.principal import app


@pytest.fixture
def entorno(tmp_path, monkeypatch):
    motor = create_engine("sqlite+pysqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)

    @event.listens_for(motor, "connect")
    def registrar_char_length(conexion, _registro):
        conexion.create_function("char_length", 1, len)

    Base.metadata.create_all(motor)
    catalogo = tmp_path / "productos.md"
    catalogo.write_text("| Producto | Precio(s) válido(s) |\n|---|---:|\n| BAGUETTE | 0.90 |\n", encoding="utf-8")
    monkeypatch.setattr(rutas, "_catalogo_piloto", lambda: catalogo)
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


def _token(cliente, correo, clave):
    respuesta = cliente.post("/api/v1/autenticacion/iniciar-sesion", json={"correo": correo, "contrasena": clave})
    assert respuesta.status_code == 200
    return {"Authorization": f"Bearer {respuesta.json()['datos']['token_acceso']}"}


def _subir(cliente, cabecera, contenido):
    return cliente.post("/api/v1/inicializacion/piloto-bakery", headers=cabecera,
                        files={"archivo": ("ventas.csv", contenido, "text/csv")})


def test_carga_web_idempotente_y_entrenamiento_reservado(entorno, monkeypatch):
    cliente, motor = entorno
    contenido = b"date,article,Quantity\n2022-08-21,BAGUETTE,2.0\n2022-08-21,BAGUETTE,3.0\n"
    assert _subir(cliente, {}, contenido).status_code == 401
    operador = _token(cliente, "operador@example.com", "clave-segura-operador")
    assert _subir(cliente, operador, contenido).status_code == 403
    admin = _token(cliente, "admin@example.com", "clave-segura-admin")
    primera = _subir(cliente, admin, contenido)
    assert primera.status_code == 202, primera.text
    datos = primera.json()["datos"]
    assert (datos["productos"], datos["filas_aceptadas"], datos["ventas_diarias_creadas"]) == (1, 2, 1)
    assert datos["repetida"] is False
    assert datos["version_modelo"].startswith("piloto-q65v2-")
    segunda = _subir(cliente, admin, contenido)
    assert segunda.status_code == 202
    assert segunda.json()["datos"]["repetida"] is True
    assert segunda.json()["datos"]["ejecucion_id"] == datos["ejecucion_id"]
    monkeypatch.setattr(rutas, "VERSION_POLITICA_MODELO", "q65v3")
    nueva_politica = _subir(cliente, admin, contenido)
    assert nueva_politica.status_code == 202
    assert nueva_politica.json()["datos"]["repetida"] is True
    assert nueva_politica.json()["datos"]["importacion_id"] == datos["importacion_id"]
    assert nueva_politica.json()["datos"]["ejecucion_id"] != datos["ejecucion_id"]
    with Session(motor) as sesion:
        assert sesion.scalar(select(func.count()).select_from(Producto)) == 1
        assert sesion.scalar(select(func.count()).select_from(VentaDiaria)) == 1
        assert sesion.scalar(select(func.count()).select_from(EjecucionAutomatizacion)) == 2


def test_error_csv_no_confirma_catalogo_ni_ventas(entorno):
    cliente, motor = entorno
    admin = _token(cliente, "admin@example.com", "clave-segura-admin")
    respuesta = _subir(cliente, admin, b"date,article,Quantity\n2022-08-21,DESCONOCIDO,1.0\n")
    assert respuesta.status_code == 422
    assert respuesta.json()["error"]["codigo"] == "SKU_DESCONOCIDO"
    with Session(motor) as sesion:
        assert sesion.scalar(select(func.count()).select_from(Producto)) == 0
        assert sesion.scalar(select(func.count()).select_from(ImportacionVenta)) == 0
        assert sesion.scalar(select(func.count()).select_from(EjecucionAutomatizacion)) == 0
