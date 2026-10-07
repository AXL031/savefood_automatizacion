"""Permisos, credenciales y protección concurrente del último administrador."""
import os
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
import pytest
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from test_api_inicializacion_ventas import cliente, cabecera, token
from app.core.base_datos import obtener_sesion
from app.core.errores import ErrorAPI
from app.modules.autenticacion.modelos import Usuario
from app.modules.autenticacion.usuarios import EditarUsuario, editar_usuario


def test_gestion_roles_credenciales_y_ultimo_administrador(cliente):
    admin = cabecera(token(cliente, "admin@example.com", "clave-segura-admin"))
    operador = cabecera(token(cliente, "operador@example.com", "clave-segura-operador"))
    ruta = "/api/v1/usuarios"
    assert cliente.get(ruta).status_code == 401
    assert cliente.get(ruta, headers=operador).status_code == 403
    entrada = {"nombre": "Nuevo", "correo": "nuevo@example.com", "contrasena": "clave-nueva-segura", "rol": "OPERADOR"}
    assert cliente.post(ruta, headers=operador, json=entrada).status_code == 403
    creado = cliente.post(ruta, headers=admin, json=entrada)
    assert creado.status_code == 201, creado.text
    usuario = creado.json()["datos"]
    assert "contrasena" not in usuario and "hash_contrasena" not in usuario
    assert cliente.post(ruta, headers=admin, json={**entrada, "correo": "NUEVO@example.com"}).status_code == 409
    for cambio in ({"rol": "DUEÑO"}, {"nombre": "   "}, {"activo": None}, {}, {"hash_contrasena": "valor"}):
        assert cliente.patch(f'{ruta}/{usuario["id"]}', headers=admin, json=cambio).status_code == 422
    assert cliente.post(ruta, headers=admin, json={**entrada, "contrasena": "corta"}).status_code == 422
    lista = cliente.get(ruta, headers=admin).json()["datos"]
    admin_id = next(u["id"] for u in lista if u["correo"] == "admin@example.com")
    for cambio in ({"activo": False}, {"rol": "OPERADOR"}):
        fallo = cliente.patch(f"{ruta}/{admin_id}", headers=admin, json=cambio)
        assert fallo.status_code == 409 and fallo.json()["error"]["codigo"] == "ULTIMO_ADMINISTRADOR"
    nuevo_token = cabecera(token(cliente, entrada["correo"], entrada["contrasena"]))
    assert cliente.patch(f'{ruta}/{usuario["id"]}', headers=admin, json={"rol": "ADMINISTRADOR"}).status_code == 200
    assert cliente.get(ruta, headers=nuevo_token).status_code == 200
    assert cliente.patch(f'{ruta}/{usuario["id"]}', headers=admin, json={"activo": False}).status_code == 200
    assert cliente.get(ruta, headers=nuevo_token).status_code == 401
    assert cliente.post("/api/v1/autenticacion/iniciar-sesion", json={"correo": entrada["correo"], "contrasena": entrada["contrasena"]}).status_code == 401
    assert cliente.patch(f'{ruta}/{usuario["id"]}', headers=admin, json={"activo": True, "correo": "otro@example.com", "nombre": "Otro"}).status_code == 200
    assert token(cliente, "otro@example.com", entrada["contrasena"])


def test_cambios_concurrentes_no_eliminan_todos_los_administradores(cliente):
    if os.getenv("E03_POSTGRES_TEST") != "1":
        pytest.skip("Requiere PostgreSQL: E03_POSTGRES_TEST=1")
    admin = cabecera(token(cliente, "admin@example.com", "clave-segura-admin"))
    creado = cliente.post("/api/v1/usuarios", headers=admin, json={"nombre":"Otro admin", "correo":"otro@example.com", "contrasena":"clave-otro-admin", "rol":"ADMINISTRADOR"})
    assert creado.status_code == 201
    with contextmanager(cliente.app.dependency_overrides[obtener_sesion])() as sesion:
        sesiones = sessionmaker(bind=sesion.get_bind())
        ids = list(sesion.scalars(select(Usuario.id).where(Usuario.rol == "ADMINISTRADOR")))
    def desactivar(id_):
        try:
            with sesiones.begin() as sesion:
                editar_usuario(sesion, id_, id_, EditarUsuario(activo=False))
            return "OK"
        except ErrorAPI as error:
            return error.codigo
    with ThreadPoolExecutor(max_workers=2) as pool:
        resultados = list(pool.map(desactivar, ids))
    assert sorted(resultados) == ["OK", "ULTIMO_ADMINISTRADOR"]
    with sesiones() as sesion:
        assert len(list(sesion.scalars(select(Usuario).where(Usuario.rol == "ADMINISTRADOR", Usuario.activo.is_(True))))) == 1
