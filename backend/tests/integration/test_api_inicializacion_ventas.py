"""API de primera carga, catálogo y ventas: permisos, sobre y reglas visibles."""

import os

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite://")
os.environ.setdefault("JWT_SECRET", "clave-local-para-pruebas-de-inicializacion")

import pytest
from fastapi.testclient import TestClient
from pwdlib import PasswordHash
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from uuid import uuid4

from app.core.base import Base
from app.core.base_datos import obtener_sesion
from app.modules.autenticacion.modelos import Usuario
from app.modules.negocios.modelos import Negocio
from app.principal import app

PRODUCTOS = b"""codigo,nombre,sku_externo,demostrar
baguette,Baguette,BAGUETTE,si
croissant,Croissant,CROISSANT,si
banette,Banette,BANETTE,si
"""

INGREDIENTES = b"""codigo,nombre,unidad_base
harina,Harina,g
"""

RECETAS = b"""codigo_producto,codigo_ingrediente,cantidad_por_unidad
baguette,harina,250.500
croissant,harina,120
banette,harina,300
"""

STOCK = b"""tipo,codigo,cantidad,codigo_lote,fecha_caducidad,fecha_limite_venta
producto,baguette,4,PT-001,2022-08-25,2022-08-24
producto,croissant,0,,,
producto,banette,2,,,
ingrediente,harina,12000.500,ING-001,2022-12-31,
"""

VENTAS = b"""fecha_local,sku_externo,unidades_vendidas
2022-08-21,BAGUETTE,12
2022-08-21,CROISSANT,0
2022-08-22,BAGUETTE,15
2022-08-23,BANETTE,7
"""


def archivos(ventas: bytes = VENTAS) -> list[tuple[str, tuple[str, bytes, str]]]:
    crudos = {
        "productos.csv": PRODUCTOS,
        "ingredientes.csv": INGREDIENTES,
        "recetas.csv": RECETAS,
        "stock_inicial.csv": STOCK,
        "ventas.csv": ventas,
    }
    return [("archivos", (nombre, contenido, "text/csv")) for nombre, contenido in crudos.items()]


FECHAS = {"fecha_objetivo_demo": "2022-08-24", "fecha_referencia_stock": "2022-08-23"}


@pytest.fixture
def cliente(monkeypatch, tmp_path):
    # Identidad de credencial simulada; nunca consulta Telegram en esta fixture.
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123:token-falso-para-pruebas-locales")
    monkeypatch.setenv("TELEGRAM_CONFIG_DIR", str(tmp_path / "telegram-secrets"))
    admin_db = None
    esquema = None
    if os.getenv("E03_POSTGRES_TEST") == "1":
        url = os.environ["DATABASE_URL"]
        assert url.startswith("postgresql")
        esquema = "e03_test_" + uuid4().hex
        admin_db = create_engine(url)
        with admin_db.begin() as conexion:
            conexion.execute(text(f'CREATE SCHEMA "{esquema}"'))
        motor = create_engine(url, connect_args={"options": f"-csearch_path={esquema}"})
    else:
        motor = create_engine("sqlite+pysqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
        @event.listens_for(motor, "connect")
        def registrar_char_length(conexion, _registro):
            conexion.create_function("char_length", 1, len)

    Base.metadata.create_all(motor)
    from app.modules.inicializacion.modelos import ConfiguracionInicial
    with Session(motor) as inicial:
        inicial.add(ConfiguracionInicial(id=1, estado="PENDIENTE"))
        inicial.commit()
    cifrador = PasswordHash.recommended()
    with Session(motor) as sesion:
        sesion.add(Negocio(id=1, nombre="Prueba", zona_horaria="America/Lima", moneda="PEN"))
        sesion.add_all(
            [
                Usuario(correo="admin@example.com", nombre="Admin", rol="ADMINISTRADOR", activo=True,
                        hash_contrasena=cifrador.hash("clave-segura-admin")),
                Usuario(correo="operador@example.com", nombre="Operador", rol="OPERADOR", activo=True,
                        hash_contrasena=cifrador.hash("clave-segura-operador")),
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
    if admin_db is not None:
        with admin_db.begin() as conexion:
            conexion.execute(text(f'DROP SCHEMA "{esquema}" CASCADE'))
        admin_db.dispose()


def test_frontera_carga_recetas_stock_y_versiones(cliente):
    admin = cabecera(token(cliente, "admin@example.com", "clave-segura-admin"))
    carga = cliente.post("/api/v1/inicializacion/confirmar", data={**FECHAS, "clave_importacion": "frontera-1"},
                         files=archivos(), headers=admin)
    assert carga.status_code == 201, carga.text
    assert carga.json()["datos"]["estado"] == "DATOS_CARGADOS"
    assert carga.json()["datos"]["pendiente_de"] == []
    recetas = cliente.get("/api/v1/recetas", headers=admin).json()["datos"]
    assert len(recetas) == 3
    original = recetas[0]["receta"]
    nueva = cliente.post(f'/api/v1/recetas/productos/{original["producto_id"]}/versiones', headers=admin,
                          json={"motivo": "Ajuste de receta", "lineas": [
                              {"ingrediente_id": original["lineas"][0]["ingrediente_id"], "cantidad_por_unidad": "321.500"}]})
    assert nueva.status_code == 201, nueva.text
    anterior = cliente.get(f'/api/v1/recetas/{original["receta_id"]}', headers=admin).json()["datos"]
    assert anterior["lineas"] == original["lineas"]
    assert nueva.json()["datos"]["version"] == original["version"] + 1
    repetida = cliente.post("/api/v1/inicializacion/confirmar", data={**FECHAS, "clave_importacion": "frontera-1"},
                           files=archivos(), headers=admin)
    assert repetida.status_code == 201
    assert repetida.json()["datos"]["ya_estaba_cargada"] is True


def test_frontera_stock_invalido_revierte_carga_completa(cliente):
    admin = cabecera(token(cliente, "admin@example.com", "clave-segura-admin"))
    entrega = archivos()
    entrega = [(campo, (nombre, crudo.replace(b"2022-08-25", b"2022-09-25") if nombre == "stock_inicial.csv" else crudo, tipo))
               for campo, (nombre, crudo, tipo) in entrega]
    respuesta = cliente.post("/api/v1/inicializacion/confirmar", data={**FECHAS, "clave_importacion": "rollback-stock"},
                             files=entrega, headers=admin)
    assert respuesta.status_code == 422, respuesta.text
    assert respuesta.json()["error"]["codigo"] == "VIDA_UTIL_EXCEDIDA"
    assert cliente.get("/api/v1/productos", headers=admin).json()["datos"] == []
    assert cliente.get("/api/v1/ingredientes", headers=admin).json()["datos"] == []
    assert cliente.get("/api/v1/recetas", headers=admin).json()["datos"] == []
    assert cliente.get("/api/v1/inicializacion/estado", headers=admin).json()["datos"]["preparacion"] is None


def test_proveedores_api_permisos_referencia_y_oferta(cliente):
    admin = cabecera(token(cliente, "admin@example.com", "clave-segura-admin"))
    operador = cabecera(token(cliente, "operador@example.com", "clave-segura-operador"))
    assert cliente.get("/api/v1/proveedores").status_code == 401
    assert cliente.post("/api/v1/proveedores", headers=operador, json={"codigo": "P1", "nombre": "Prueba"}).status_code == 403
    p = cliente.post("/api/v1/proveedores", headers=admin, json={"codigo": "P1", "nombre": "Prueba", "chat_id_pruebas": "123"})
    assert p.status_code == 201, p.text
    pid = p.json()["datos"]["id"]
    oferta = {"ingrediente_id": 999, "descripcion": "Saco", "unidad_compra": "saco",
              "factor_conversion": "25000", "multiplo": "1", "minimo": "0", "preferida": True}
    assert cliente.post(f"/api/v1/proveedores/{pid}/ofertas", headers=admin, json=oferta).status_code == 404
    ingrediente = cliente.post("/api/v1/ingredientes", headers=admin, json={"codigo": "HAR", "nombre": "Harina", "unidad_base": "g"})
    oferta["ingrediente_id"] = ingrediente.json()["datos"]["id"]
    creada = cliente.post(f"/api/v1/proveedores/{pid}/ofertas", headers=admin, json=oferta)
    assert creada.status_code == 201, creada.text
    assert cliente.get(f"/api/v1/proveedores/{pid}/ofertas", headers=operador).json()["datos"][0]["id"] == creada.json()["datos"]["id"]
    preferida = cliente.get(f'/api/v1/proveedores/ofertas/preferida/{oferta["ingrediente_id"]}', headers=admin).json()["datos"]
    assert preferida["compra_automatica_habilitada"] is False
    verificacion = cliente.post(f"/api/v1/proveedores/{pid}/verificar-destino", headers=admin)
    assert verificacion.json()["datos"]["verificado"] is False
    assert "no configurado" in verificacion.json()["datos"]["detalle"]


def test_stock_cero_caducidad_ajuste_idempotente_y_saldo(cliente):
    admin = cabecera(token(cliente, "admin@example.com", "clave-segura-admin"))
    cliente.post("/api/v1/inicializacion/confirmar", data={**FECHAS, "clave_importacion": "stock-1"},
                 files=archivos(), headers=admin).raise_for_status()
    filas = cliente.get("/api/v1/inventario/disponibilidad?fecha=2022-08-24", headers=admin).json()["datos"]
    productos = {fila["codigo"]: fila for fila in filas if fila["tipo"] == "producto"}
    assert productos["croissant"]["cantidad_disponible"] == "0"
    assert productos["croissant"]["stock_conocido"] is True
    assert productos["baguette"]["cantidad_disponible"] == "4"
    movimientos = cliente.get("/api/v1/inventario/movimientos", headers=admin).json()["datos"]
    lote = next(m for m in movimientos if m["codigo_lote"] == "PT-001")["lote_id"]
    ajuste = {"tipo": "producto", "lote_id": lote, "delta": "-3", "motivo": "Merma de prueba",
              "clave_operacion": "ajuste-1", "efectivo_en_demo": "2022-08-24T10:00:00"}
    primero = cliente.post("/api/v1/inventario/ajustes", headers=admin, json=ajuste)
    assert primero.status_code == 201, primero.text
    assert primero.json()["datos"]["saldo_resultante"] == "1"
    repetido = cliente.post("/api/v1/inventario/ajustes", headers=admin, json=ajuste)
    assert repetido.status_code == 200
    assert repetido.json()["datos"]["movimiento_id"] == primero.json()["datos"]["movimiento_id"]
    otro_motivo = cliente.post("/api/v1/inventario/ajustes", headers=admin, json={**ajuste, "motivo": "Otro motivo"})
    assert otro_motivo.status_code == 409
    distinto = cliente.post("/api/v1/inventario/ajustes", headers=admin, json={**ajuste, "delta": "-2"})
    assert distinto.status_code == 409
    negativo = cliente.post("/api/v1/inventario/ajustes", headers=admin, json={**ajuste, "clave_operacion": "otra", "delta": "-2"})
    assert negativo.status_code == 409
    vencidos = cliente.get("/api/v1/inventario/disponibilidad?fecha=2022-08-26", headers=admin).json()["datos"]
    assert next(f for f in vencidos if f["codigo"] == "baguette")["cantidad_disponible"] == "0"


def token(cliente: TestClient, correo: str, contrasena: str) -> str:
    respuesta = cliente.post(
        "/api/v1/autenticacion/iniciar-sesion", json={"correo": correo, "contrasena": contrasena}
    )
    assert respuesta.status_code == 200
    return respuesta.json()["datos"]["token_acceso"]


def cabecera(valor: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {valor}"}


def test_estado_inicial_es_pendiente_y_exige_sesion(cliente: TestClient):
    assert cliente.get("/api/v1/inicializacion/estado").status_code == 401

    operador = cabecera(token(cliente, "operador@example.com", "clave-segura-operador"))
    respuesta = cliente.get("/api/v1/inicializacion/estado", headers=operador)
    assert respuesta.status_code == 200
    datos = respuesta.json()["datos"]
    assert datos["estado"] == "PENDIENTE"
    assert datos["huella_solicitud"] is None


def test_operador_no_puede_cargar(cliente: TestClient):
    operador = cabecera(token(cliente, "operador@example.com", "clave-segura-operador"))
    respuesta = cliente.post(
        "/api/v1/inicializacion/vista-previa", data=FECHAS, files=archivos(), headers=operador
    )
    assert respuesta.status_code == 403
    assert respuesta.json()["error"]["codigo"] == "PERMISO_DENEGADO"


def test_vista_previa_resume_sin_guardar(cliente: TestClient):
    admin = cabecera(token(cliente, "admin@example.com", "clave-segura-admin"))
    respuesta = cliente.post(
        "/api/v1/inicializacion/vista-previa", data=FECHAS, files=archivos(), headers=admin
    )
    assert respuesta.status_code == 200
    datos = respuesta.json()["datos"]
    assert datos["aceptable"] is True
    assert datos["ventas"]["filas"] == 4
    assert datos["ventas"]["primera_fecha"] == "2022-08-21"
    assert len(datos["catalogo"]["productos_demo"]) == 3
    assert len(datos["huellas"]["solicitud"]) == 64

    # La vista previa no persiste nada.
    assert cliente.get("/api/v1/productos", headers=admin).json()["datos"] == []
    assert cliente.get("/api/v1/inicializacion/estado", headers=admin).json()["datos"]["estado"] == "PENDIENTE"


def test_entrega_invalida_devuelve_errores_ubicados(cliente: TestClient):
    admin = cabecera(token(cliente, "admin@example.com", "clave-segura-admin"))
    malas = VENTAS + b"2022-08-23,DESCONOCIDO,3\n"
    respuesta = cliente.post(
        "/api/v1/inicializacion/vista-previa", data=FECHAS, files=archivos(malas), headers=admin
    )
    datos = respuesta.json()["datos"]
    assert datos["aceptable"] is False
    assert datos["total_errores"] == 1
    assert datos["errores"][0]["campo"].startswith("ventas.csv:6/")


def test_confirmar_persiste_y_expone_lo_pendiente(cliente: TestClient):
    admin = cabecera(token(cliente, "admin@example.com", "clave-segura-admin"))
    cuerpo = dict(FECHAS, clave_importacion="primera-carga-1")

    respuesta = cliente.post(
        "/api/v1/inicializacion/confirmar", data=cuerpo, files=archivos(), headers=admin
    )
    assert respuesta.status_code == 201
    datos = respuesta.json()["datos"]
    assert datos["productos"] == 3
    assert datos["ventas_diarias"] == 4
    # Los puertos reales de Max y Vera completan la transacción de la carga.
    assert datos["estado"] == "DATOS_CARGADOS"
    assert datos["pendiente_de"] == []

    productos = cliente.get("/api/v1/productos", headers=admin).json()["datos"]
    assert {fila["sku_externo"] for fila in productos} == {"BAGUETTE", "CROISSANT", "BANETTE"}

    ventas = cliente.get("/api/v1/ventas", headers=admin).json()["datos"]
    assert len(ventas) == 4
    # El cero explícito se conserva como dato conocido.
    assert any(fila["unidades_vendidas"] == 0 for fila in ventas)


def test_correccion_de_venta_conserva_la_revision_anterior(cliente: TestClient):
    admin = cabecera(token(cliente, "admin@example.com", "clave-segura-admin"))
    cliente.post(
        "/api/v1/inicializacion/confirmar",
        data=dict(FECHAS, clave_importacion="primera-carga-1"),
        files=archivos(),
        headers=admin,
    )
    ventas = cliente.get("/api/v1/ventas", headers=admin).json()["datos"]
    venta = next(fila for fila in ventas if fila["unidades_vendidas"] == 12)

    sin_motivo = cliente.patch(
        f"/api/v1/ventas/{venta['id']}", json={"unidades_vendidas": 13, "motivo": ""}, headers=admin
    )
    assert sin_motivo.status_code == 422

    corregida = cliente.patch(
        f"/api/v1/ventas/{venta['id']}",
        json={"unidades_vendidas": 13, "motivo": "Recuento manual del cierre"},
        headers=admin,
    )
    assert corregida.status_code == 200
    assert corregida.json()["datos"]["revision_actual"] == 2

    revisiones = cliente.get(f"/api/v1/ventas/{venta['id']}/revisiones", headers=admin).json()["datos"]
    assert [fila["unidades_vendidas"] for fila in revisiones] == [12, 13]
    assert revisiones[0]["origen_cambio"] == "IMPORTACION"
    assert revisiones[1]["origen_cambio"] == "CORRECCION"


def test_operador_no_puede_corregir_ventas(cliente: TestClient):
    admin = cabecera(token(cliente, "admin@example.com", "clave-segura-admin"))
    cliente.post(
        "/api/v1/inicializacion/confirmar",
        data=dict(FECHAS, clave_importacion="primera-carga-1"),
        files=archivos(),
        headers=admin,
    )
    venta = cliente.get("/api/v1/ventas", headers=admin).json()["datos"][0]

    operador = cabecera(token(cliente, "operador@example.com", "clave-segura-operador"))
    respuesta = cliente.patch(
        f"/api/v1/ventas/{venta['id']}",
        json={"unidades_vendidas": 1, "motivo": "Intento sin permiso"},
        headers=operador,
    )
    assert respuesta.status_code == 403


def test_filtro_por_rango_de_fechas(cliente: TestClient):
    admin = cabecera(token(cliente, "admin@example.com", "clave-segura-admin"))
    cliente.post(
        "/api/v1/inicializacion/confirmar",
        data=dict(FECHAS, clave_importacion="primera-carga-1"),
        files=archivos(),
        headers=admin,
    )
    respuesta = cliente.get(
        "/api/v1/ventas", params={"desde": "2022-08-22", "hasta": "2022-08-22"}, headers=admin
    )
    assert [fila["fecha_local"] for fila in respuesta.json()["datos"]] == ["2022-08-22"]

    invalido = cliente.get(
        "/api/v1/ventas", params={"desde": "2022-08-23", "hasta": "2022-08-21"}, headers=admin
    )
    assert invalido.status_code == 422
    assert invalido.json()["error"]["codigo"] == "RANGO_INVALIDO"
