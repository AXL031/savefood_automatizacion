"""Adopta la cadena publicada sin reescribir revisiones ni borrar datos.

Solo las revisiones locales 0008/0009, con planes vacíos y motor detenido.
La operación completa comparte una transacción PostgreSQL; ante cualquier
error conserva el esquema y la revisión originales. No envía mensajes.
"""
import importlib.util
import os
from pathlib import Path

from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, inspect, text

RAIZ = Path(__file__).resolve().parent
LOCALES = ("0008_e03_modelo", "0009_m02_planes")
PUBLICADAS = (
    "0008_e03_preparacion_ml", "0009_m02_planificacion", "0010_m03_necesidades",
    "0011_l02_compras", "0012_l03_telegram_config", "0013_l03_aprobacion_envio",
    "0014_l04_recuperacion",
)


def cargar_revision(nombre, carpeta):
    spec = importlib.util.spec_from_file_location(nombre, carpeta / f"{nombre}.py")
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def conciliar(conexion):
    """El llamador abre y confirma la transacción; devuelve la revisión final."""
    if conexion.dialect.name != "postgresql":
        raise RuntimeError("La conciliación requiere PostgreSQL y su DDL transaccional.")
    conexion.execute(text("SELECT pg_advisory_xact_lock(7040062026)"))
    revision = conexion.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
    if revision == PUBLICADAS[-1]:
        return revision
    if revision not in LOCALES:
        raise RuntimeError(f"Revisión no compatible con este puente: {revision}.")
    conexion.execute(text("LOCK TABLE configuracion_inicial, ejecucion_automatizacion IN ACCESS EXCLUSIVE MODE"))
    if conexion.execute(text("SELECT count(*) FROM ejecucion_automatizacion WHERE estado IN ('PENDIENTE','EN_EJECUCION','REINTENTANDO')")).scalar_one():
        raise RuntimeError("Hay ejecuciones activas; terminar o resolver el motor antes de conciliar.")
    if revision == LOCALES[1]:
        conexion.execute(text("LOCK TABLE plan_produccion, elemento_plan, necesidad_ingrediente IN ACCESS EXCLUSIVE MODE"))
        for tabla in ("plan_produccion", "elemento_plan", "necesidad_ingrediente"):
            if conexion.execute(text(f"SELECT count(*) FROM {tabla}")).scalar_one():
                raise RuntimeError("Hay planes o necesidades conservados; requieren conversión de snapshots. No se ha borrado ningún dato.")
        columnas = {c['name'] for c in inspect(conexion).get_columns('plan_produccion')}
        if 'trazas_json' not in columnas or 'origen_pronostico_json' in columnas:
            raise RuntimeError("El esquema no coincide con la revisión local esperada.")
    enlaces = conexion.execute(text("SELECT id, preparacion_ejecucion_id FROM configuracion_inicial")).all()
    contexto = MigrationContext.configure(conexion)
    with Operations.context(contexto):
        if revision == LOCALES[1]:
            cargar_revision(LOCALES[1], RAIZ).downgrade()
        cargar_revision(LOCALES[0], RAIZ).downgrade()
        for nombre in PUBLICADAS:
            cargar_revision(nombre, RAIZ / "versions").upgrade()
    for id_, ejecucion_id in enlaces:
        # Preserva el enlace durable; el modelo de una tarea completada sigue
        # siendo el mismo artefacto, nunca se entrena de nuevo durante el puente.
        conexion.execute(text("""UPDATE configuracion_inicial
            SET preparacion_ejecucion_id = :ejecucion,
                preparacion_numero = CASE WHEN CAST(:ejecucion AS integer) IS NULL THEN 0 ELSE 1 END,
                modelo_id = (SELECT a.id FROM artefacto_modelo a
                    JOIN ejecucion_automatizacion e ON e.id = :ejecucion
                    WHERE a.id = (e.datos_salida_json ->> 'modelo_id')::integer)
            WHERE id = :id"""), {"id": id_, "ejecucion": ejecucion_id})
    from app.core.base import Base
    from app.principal import app  # noqa: F401; todos los metadatos públicos
    diferencias = compare_metadata(contexto, Base.metadata)
    if diferencias:
        raise RuntimeError(f"La conciliación no coincide con los modelos: {diferencias}")
    conexion.execute(text("UPDATE alembic_version SET version_num = :revision"), {"revision": PUBLICADAS[-1]})
    return PUBLICADAS[-1]


if __name__ == "__main__":
    motor = create_engine(os.environ["DATABASE_URL"])
    with motor.begin() as conexion:
        resultado = conciliar(conexion)
    print(f"Conciliación confirmada: {resultado}. Datos conservados; sin envíos.")
