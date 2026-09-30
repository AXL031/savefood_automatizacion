"""Prueba del delta 0004→0007, reversibilidad y metadatos completos."""
import importlib.util
from pathlib import Path

from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from alembic.operations import Operations
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, event, inspect

from app.core.base import Base
from app.principal import app  # noqa: F401; carga los modelos de todas las rutas

NUEVAS = {"ingrediente", "receta", "receta_ingrediente", "lote_producto",
          "lote_ingrediente", "movimiento_inventario", "proveedor", "oferta_ingrediente"}


def test_migraciones_delta_reversible_y_unica_cabeza():
    backend = Path(__file__).resolve().parents[2]
    config = Config()
    config.set_main_option("script_location", str(backend / "migrations"))
    assert ScriptDirectory.from_config(config).get_heads() == ["0007_l01_proveedores"]
    motor = create_engine("sqlite://")

    @event.listens_for(motor, "connect")
    def funciones(c, _):
        c.create_function("char_length", 1, len)
        c.execute("PRAGMA foreign_keys=ON")

    # La base previa se construye desde los modelos ya existentes: no modifica
    # datos ni revisiones aplicadas. Se ejecutan las tres nuevas migraciones.
    Base.metadata.create_all(motor, tables=[t for t in Base.metadata.sorted_tables if t.name not in NUEVAS])
    modulos = []
    for nombre in ("0005_m01_ingredientes_recetas", "0006_v01_inventario", "0007_l01_proveedores"):
        spec = importlib.util.spec_from_file_location(nombre, backend / "migrations" / "versions" / f"{nombre}.py")
        modulo = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modulo)
        modulos.append(modulo)
    with motor.begin() as conexion:
        contexto = MigrationContext.configure(conexion)
        with Operations.context(contexto):
            for modulo in modulos:
                modulo.upgrade()
            assert NUEVAS <= set(inspect(conexion).get_table_names())
            assert compare_metadata(contexto, Base.metadata) == []
            for modulo in reversed(modulos):
                modulo.downgrade()
            assert not NUEVAS.intersection(inspect(conexion).get_table_names())
            for modulo in modulos:
                modulo.upgrade()
            assert compare_metadata(contexto, Base.metadata) == []
    motor.dispose()
