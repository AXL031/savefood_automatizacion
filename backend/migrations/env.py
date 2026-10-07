import os
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.base import Base
from app.modules.autenticacion.modelos import Usuario  # noqa: F401
from app.modules.negocios.modelos import Negocio  # noqa: F401
from app.modules.automatizaciones.modelos import ProgramacionDemo, EjecucionAutomatizacion, IntentoAutomatizacion  # noqa: F401
from app.modules.productos.modelos import Producto, SkuProducto  # noqa: F401
from app.modules.ventas.modelos import ImportacionVenta, VentaDiaria, RevisionVenta  # noqa: F401
from app.modules.pronosticos.modelos import ArtefactoModelo, CorridaPronostico, Pronostico, EvaluacionPronostico  # noqa: F401
from app.modules.inicializacion.modelos import ConfiguracionInicial  # noqa: F401
from app.modules.ingredientes.modelos import Ingrediente  # noqa: F401
from app.modules.recetas.modelos import Receta, RecetaIngrediente  # noqa: F401
from app.modules.inventario.modelos import LoteProducto, LoteIngrediente, MovimientoInventario  # noqa: F401
from app.modules.proveedores.modelos import Proveedor, OfertaIngrediente  # noqa: F401
from app.modules.planificacion.modelos import PlanProduccion, ElementoPlan, NecesidadIngrediente  # noqa: F401

config = context.config
if config.config_file_name and config.get_section(config.config_ini_section, {}).get("loggers"):
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(
        url=os.environ["DATABASE_URL"],
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = os.environ["DATABASE_URL"]
    connectable = engine_from_config(configuration, prefix="sqlalchemy.", poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
