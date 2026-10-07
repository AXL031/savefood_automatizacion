"""Puente de la base local: conservación, rechazo seguro y rollback real."""
import os
import importlib.util
from pathlib import Path
from datetime import date

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.modules.automatizaciones.servicio import crear_o_recuperar_ejecucion
from app.modules.pronosticos.modelos import ArtefactoModelo, CorridaPronostico

from test_preparacion_e03 import entorno

pytestmark = pytest.mark.skipif(os.getenv("E03_POSTGRES_TEST") != "1", reason="DDL transaccional requiere PostgreSQL aislado")
RUTA = Path(__file__).resolve().parents[2] / "migrations" / "conciliar_local.py"
spec = importlib.util.spec_from_file_location("puente_local", RUTA)
puente = importlib.util.module_from_spec(spec)
spec.loader.exec_module(puente)


def preparar_local(entorno, revision="0009_m02_planes"):
    _, sesiones, _ = entorno
    engine = sesiones.kw['bind']
    with engine.begin() as c, Operations.context(MigrationContext.configure(c)):
        for nombre in reversed(puente.PUBLICADAS):
            puente.cargar_revision(nombre, puente.RAIZ / "versions").downgrade()
        for nombre in puente.LOCALES:
            puente.cargar_revision(nombre, puente.RAIZ).upgrade()
            if nombre == revision:
                break
        c.execute(text("CREATE TABLE alembic_version (version_num varchar(32) PRIMARY KEY)"))
        c.execute(text("INSERT INTO alembic_version VALUES (:revision)"), {"revision": revision})
    return engine


def sembrar_corrida(engine):
    with Session(engine) as s, s.begin():
        modelo = ArtefactoModelo(version_modelo='conservar', ruta_local='fixture', sha256='a' * 64,
            huella_datos_entrenamiento='b' * 64, fecha_corte_entrenamiento=date(2022, 8, 31),
            particion_json={}, estado='LISTO_DEMO')
        s.add(modelo); s.flush()
        ejecucion = crear_o_recuperar_ejecucion(s, 'PREPARAR_MODELO', 'conservar', {})
        ejecucion.estado = 'COMPLETADA'
        ejecucion.datos_salida_json = {'modelo_id': modelo.id}
        corrida = CorridaPronostico(ejecucion_id=ejecucion.id, tipo='DEMO_PROGRAMADA',
            clave_ejecucion='conservar', huella_datos_entrada='c' * 64, fecha_objetivo=date(2022, 9, 24),
            modelo_id=modelo.id, estado='COMPLETADA')
        s.add(corrida); s.flush()
        return corrida.id, ejecucion.id, modelo.id


@pytest.mark.parametrize("revision", puente.LOCALES)
def test_concilia_y_conserva_inicializacion_catalogo_y_enlace(entorno, revision):
    engine = preparar_local(entorno, revision)
    _, ejecucion_id, modelo_id = sembrar_corrida(engine)
    with engine.begin() as c:
        c.execute(text("INSERT INTO producto (codigo,nombre,activo,demostrar) VALUES ('conservar','Conservar',true,false)"))
        c.execute(text("UPDATE configuracion_inicial SET huella_solicitud = :huella, fecha_objetivo_demo = '2022-09-24'"), {"huella": "a" * 64})
        anterior = c.execute(text("SELECT huella_solicitud,fecha_objetivo_demo FROM configuracion_inicial")).all()
        c.execute(text("UPDATE configuracion_inicial SET preparacion_ejecucion_id = :id"), {'id': ejecucion_id})
    with engine.begin() as c:
        assert puente.conciliar(c) == "0014_l04_recuperacion"
    with engine.begin() as c:
        assert c.execute(text("SELECT huella_solicitud,fecha_objetivo_demo FROM configuracion_inicial")).all() == anterior
        assert c.execute(text("SELECT codigo,nombre FROM producto")).one() == ('conservar','Conservar')
        assert c.execute(text("SELECT count(*) FROM plan_produccion")).scalar_one() == 0
        assert c.execute(text("SELECT count(*) FROM envio_pedido")).scalar_one() == 0
        assert c.execute(text("SELECT preparacion_ejecucion_id,modelo_id,preparacion_numero FROM configuracion_inicial")).one() == (ejecucion_id, modelo_id, 1)
        assert puente.conciliar(c) == "0014_l04_recuperacion"


def test_fallo_intermedio_revierte_ddl_revision_y_datos(entorno, monkeypatch):
    engine = preparar_local(entorno)
    real = puente.cargar_revision

    def inducir(nombre, carpeta):
        if nombre == "0009_m02_planificacion":
            raise RuntimeError("fallo inducido")
        return real(nombre, carpeta)

    monkeypatch.setattr(puente, "cargar_revision", inducir)
    with pytest.raises(RuntimeError, match="fallo inducido"), engine.begin() as c:
        puente.conciliar(c)
    with engine.connect() as c:
        assert c.execute(text("SELECT version_num FROM alembic_version")).scalar_one() == '0009_m02_planes'
        assert 'trazas_json' in {col['name'] for col in inspect(c).get_columns('plan_produccion')}
        assert 'modelo_id' not in {col['name'] for col in inspect(c).get_columns('configuracion_inicial')}
        assert c.execute(text("SELECT count(*) FROM configuracion_inicial")).scalar_one() == 1


def test_no_descarta_planes_existentes(entorno):
    engine = preparar_local(entorno)
    corrida_id, ejecucion_id, _ = sembrar_corrida(engine)
    with engine.begin() as c:
        c.execute(text("INSERT INTO plan_produccion (corrida_id,ejecucion_id,clave_ejecucion,huella_stock_recetas,fecha_objetivo,stock_leido_en,estado,trazas_json) VALUES (:corrida,:ejecucion,'conservar',:huella,'2022-09-24',now(),'PROPUESTO','{}')"), {"huella": "a" * 64, 'corrida': corrida_id, 'ejecucion': ejecucion_id})
    with pytest.raises(RuntimeError, match="planes o necesidades conservados"), engine.begin() as c:
        puente.conciliar(c)
    with engine.connect() as c:
        assert c.execute(text("SELECT clave_ejecucion FROM plan_produccion")).scalar_one() == 'conservar'
        assert c.execute(text("SELECT version_num FROM alembic_version")).scalar_one() == '0009_m02_planes'

def test_conserva_enlace_nulo_y_rechaza_motor_activo(entorno):
    engine = preparar_local(entorno)
    _, ejecucion_id, _ = sembrar_corrida(engine)
    with engine.begin() as c:
        c.execute(text("UPDATE ejecucion_automatizacion SET estado = 'PENDIENTE' WHERE id = :id"), {"id": ejecucion_id})
    with pytest.raises(RuntimeError, match="ejecuciones activas"), engine.begin() as c:
        puente.conciliar(c)
    with engine.begin() as c:
        assert c.execute(text("SELECT version_num FROM alembic_version")).scalar_one() == '0009_m02_planes'
        c.execute(text("UPDATE ejecucion_automatizacion SET estado = 'COMPLETADA' WHERE id = :id"), {"id": ejecucion_id})
    with engine.begin() as c:
        puente.conciliar(c)
        assert c.execute(text("SELECT preparacion_ejecucion_id,modelo_id,preparacion_numero FROM configuracion_inicial")).one() == (None, None, 0)
