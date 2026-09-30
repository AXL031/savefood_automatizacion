"""Frontera real de ventas con inferencia y evaluación persistidas."""

import os

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite://")
os.environ.setdefault("JWT_SECRET", "clave-local-para-pruebas-de-pronosticos")

from datetime import date, timedelta

import pytest
import jwt
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.core.base import Base
from app.core.base_datos import obtener_sesion
from app.modules.autenticacion.modelos import Usuario
from app.modules.negocios.modelos import Negocio  # noqa: F401
from app.modules.automatizaciones.modelos import EjecucionAutomatizacion  # noqa: F401
from app.modules.productos.modelos import Producto, SkuProducto
from app.modules.pronosticos import servicio as inferencia
from app.modules.pronosticos.caracteristicas import FEATURES, construir_vector
from app.modules.pronosticos.evaluacion import detalle_evaluacion, evaluar_corrida
from app.modules.pronosticos.modelos import ArtefactoModelo, CorridaPronostico, EvaluacionPronostico
from app.modules.ventas.modelos import RevisionVenta, VentaDiaria
from app.modules.ventas.servicio import VentaHistorica, corregir_venta
from app.principal import app


def test_vector_ignora_venta_objetivo_y_conserva_ausencias():
    objetivo = date(2022, 8, 24)
    historial = [VentaHistorica(1, "BAGUETTE", objetivo - timedelta(days=1), 4, 1)]
    base = construir_vector("BAGUETTE", objetivo, historial)
    alterado = construir_vector("BAGUETTE", objetivo, historial + [
        VentaHistorica(1, "BAGUETTE", objetivo, 999, 2)
    ])
    assert base == alterado
    assert list(base) == FEATURES
    assert base["ventas_hace_7_dias"] is None
    assert base["conteo_28_dias"] == 1


@pytest.fixture
def contexto():
    engine = create_engine("sqlite:///:memory:")
    @event.listens_for(engine, "connect")
    def _char_length(conexion, _registro):
        conexion.create_function("char_length", 1, len)
    Base.metadata.create_all(engine)
    with Session(engine) as sesion:
        producto = Producto(codigo="baguette", nombre="Baguette")
        sesion.add(producto)
        sesion.flush()
        sesion.add(SkuProducto(producto_id=producto.id, origen="bakery", sku_externo="BAGUETTE"))
        ejecucion = EjecucionAutomatizacion(tipo="GENERAR_PROPUESTA", clave_idempotencia="prueba-k02",
            huella_entrada="a" * 64, datos_entrada_json={}, estado="PENDIENTE")
        sesion.add(ejecucion)
        modelo = ArtefactoModelo(version_modelo="demo-test", ruta_local="demo-test", sha256="b" * 64,
            huella_datos_entrenamiento="c" * 64, fecha_corte_entrenamiento=date(2022, 6, 30),
            particion_json={"inicio_prueba": "2022-08-01", "fin_prueba": "2022-08-31"}, estado="LISTO_DEMO")
        sesion.add(modelo)
        sesion.flush()
        objetivo = date(2022, 8, 24)
        for dias in range(1, 8):
            fecha = objetivo - timedelta(days=dias)
            venta = VentaDiaria(producto_id=producto.id, fecha_local=fecha, unidades_vendidas=dias,
                                revision_actual=1)
            sesion.add(venta)
            sesion.flush()
            sesion.add(RevisionVenta(venta_id=venta.id, numero_revision=1, unidades_vendidas=dias,
                                     origen_cambio="IMPORTACION", motivo="fixture"))
        sesion.flush()
        yield sesion, producto.id, ejecucion.id, modelo.id
    engine.dispose()


def test_inferencia_no_lee_real_objetivo_y_evaluacion_versiona_revision(contexto, monkeypatch):
    sesion, producto_id, ejecucion_id, modelo_id = contexto

    class ModeloFalso:
        feature_names_ = FEATURES
        def predict(self, tabla):
            assert tabla.iloc[0]["conteo_28_dias"] == 7
            return [5.2]

    monkeypatch.setattr(inferencia, "_cargar_cbm", lambda _: (ModeloFalso(), {
        "productos_entrenados": ["BAGUETTE"], "min_observaciones_previas_28_dias": 7,
    }))
    fecha = date(2022, 8, 24)
    args = dict(ejecucion_id=ejecucion_id, fecha_objetivo=fecha,
                producto_ids=[producto_id], modelo_id=modelo_id)
    corrida = inferencia.generar_corrida(sesion, clave_ejecucion="corrida-1", **args)
    assert inferencia.obtener_pronosticos(sesion, corrida.id)[0].cantidad_pronosticada == 5
    assert inferencia.generar_corrida(sesion, clave_ejecucion="corrida-1", **args).id == corrida.id

    venta_objetivo = VentaDiaria(producto_id=producto_id, fecha_local=fecha, unidades_vendidas=10, revision_actual=1)
    sesion.add(venta_objetivo)
    sesion.flush()
    sesion.add(RevisionVenta(venta_id=venta_objetivo.id, numero_revision=1, unidades_vendidas=10,
                             origen_cambio="IMPORTACION", motivo="fixture"))
    sesion.flush()
    segunda = inferencia.generar_corrida(sesion, clave_ejecucion="corrida-2", **args)
    assert segunda.huella_datos_entrada == corrida.huella_datos_entrada
    assert evaluar_corrida(sesion, corrida.id, ejecucion_id)["evaluaciones_nuevas"] == 1
    assert evaluar_corrida(sesion, corrida.id, ejecucion_id)["evaluaciones_nuevas"] == 0
    corregir_venta(sesion, venta_objetivo.id, 12, "Revisión posterior")
    assert evaluar_corrida(sesion, corrida.id, ejecucion_id)["evaluaciones_nuevas"] == 1
    assert len(sesion.scalars(select(EvaluacionPronostico).where(EvaluacionPronostico.corrida_id == corrida.id)).all()) == 2
    detalle = detalle_evaluacion(sesion, corrida)
    assert detalle["total_real_conocido"] == 12
    assert detalle["total_previsto_evaluable"] == 5


def test_api_pronosticos_protegida_y_lecturas_persistidas():
    engine = create_engine("sqlite+pysqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)

    @event.listens_for(engine, "connect")
    def _char_length(conexion, _registro):
        conexion.create_function("char_length", 1, len)

    Base.metadata.create_all(engine)
    with Session(engine) as sesion:
        usuario = Usuario(correo="admin-pronosticos@example.com", nombre="Admin", rol="ADMINISTRADOR",
                          activo=True, hash_contrasena="fixture")
        sesion.add(usuario)
        sesion.add(ArtefactoModelo(
            version_modelo="api-test", ruta_local="api-test", sha256="a" * 64,
            huella_datos_entrenamiento="b" * 64, fecha_corte_entrenamiento=date(2022, 6, 30),
            particion_json={"inicio_entrenamiento": "2021-01-01", "fin_entrenamiento": "2022-03-31",
                            "inicio_validacion": "2022-04-01", "fin_validacion": "2022-06-30",
                            "inicio_prueba": "2022-07-01", "fin_prueba": "2022-09-30"},
            estado="LISTO_DEMO",
        ))
        sesion.commit()
        usuario_id = usuario.id

    def sesion_de_prueba():
        with Session(engine) as sesion:
            yield sesion

    app.dependency_overrides[obtener_sesion] = sesion_de_prueba
    try:
        with TestClient(app) as cliente:
            ruta = "/api/v1/pronosticos/modelos"
            assert cliente.get(ruta).status_code == 401
            token = jwt.encode({"sub": str(usuario_id)}, os.environ["JWT_SECRET"], algorithm="HS256")
            cabeceras = {"Authorization": f"Bearer {token}"}
            respuesta = cliente.get(ruta, headers=cabeceras)
            assert respuesta.status_code == 200
            assert respuesta.json()["datos"][0]["version_modelo"] == "api-test"
            resumen = cliente.get("/api/v1/pronosticos/evaluacion?modelo_id=1", headers=cabeceras)
            assert resumen.status_code == 200
            assert resumen.json()["datos"]["metricas_globales"]["pares_evaluables"] == 0
            inicio = cliente.post("/api/v1/pronosticos/preparar-modelo", headers=cabeceras,
                                  json={"version_modelo": "api-test-2", "clave_idempotencia": "api-test-2"})
            assert inicio.status_code == 202
            assert inicio.json()["datos"]["estado"] == "PENDIENTE"
    finally:
        app.dependency_overrides.clear()
        engine.dispose()
