"""Prueba del delta 0004→0007, reversibilidad y metadatos completos."""
import importlib.util
from pathlib import Path
import pytest

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


def cargar_revision(nombre):
    ruta = Path(__file__).resolve().parents[2] / "migrations" / "versions" / f"{nombre}.py"
    spec = importlib.util.spec_from_file_location(nombre, ruta)
    modulo = importlib.util.module_from_spec(spec); spec.loader.exec_module(modulo)
    return modulo


def test_migraciones_delta_reversible_y_unica_cabeza():
    backend = Path(__file__).resolve().parents[2]
    config = Config()
    config.set_main_option("script_location", str(backend / "migrations"))
    assert ScriptDirectory.from_config(config).get_heads() == ["0014_l04_recuperacion"]
    motor = create_engine("sqlite://")

    @event.listens_for(motor, "connect")
    def funciones(c, _):
        c.create_function("char_length", 1, len)
        c.execute("PRAGMA foreign_keys=ON")

    # La base previa se construye desde los modelos ya existentes: no modifica
    # datos ni revisiones aplicadas. Se ejecutan las tres nuevas migraciones.
    Base.metadata.create_all(motor, tables=[t for t in Base.metadata.sorted_tables if t.name not in NUEVAS])
    modulos = []
    for nombre in ("0005_m01_ingredientes_recetas", "0006_v01_inventario", "0007_l01_proveedores", "0012_l03_telegram_config"):
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


def test_migracion_0009_reversible_y_coherente_con_modelos():
    backend = Path(__file__).resolve().parents[2]
    motor = create_engine("sqlite://")
    @event.listens_for(motor, "connect")
    def funciones(c, _):
        c.create_function("char_length", 1, len)
        c.execute("PRAGMA foreign_keys=ON")
    tablas = {"plan_produccion", "elemento_plan", "necesidad_ingrediente"}
    Base.metadata.create_all(motor, tables=[t for t in Base.metadata.sorted_tables if t.name not in tablas])
    spec = importlib.util.spec_from_file_location("m02", backend / "migrations/versions/0009_m02_planificacion.py")
    modulo = importlib.util.module_from_spec(spec); spec.loader.exec_module(modulo)
    spec_m03 = importlib.util.spec_from_file_location("m03", backend / "migrations/versions/0010_m03_necesidades.py")
    m03 = importlib.util.module_from_spec(spec_m03); spec_m03.loader.exec_module(m03)
    with motor.begin() as conexion:
        contexto = MigrationContext.configure(conexion)
        with Operations.context(contexto):
            modulo.upgrade()
            m03.upgrade()
            assert tablas <= set(inspect(conexion).get_table_names())
            assert compare_metadata(contexto, Base.metadata) == []
            m03.downgrade()
            modulo.downgrade()
            assert not tablas.intersection(inspect(conexion).get_table_names())
            modulo.upgrade()
            m03.upgrade()
            assert compare_metadata(contexto, Base.metadata) == []
    motor.dispose()


def test_migracion_0008_conserva_carga_y_es_reversible():
    backend = Path(__file__).resolve().parents[2]
    motor = create_engine("sqlite://")
    @event.listens_for(motor, "connect")
    def funciones(c, _):
        c.create_function("char_length", 1, len)
    Base.metadata.create_all(motor, tables=[t for t in Base.metadata.sorted_tables if t.name != "configuracion_inicial"])
    def cargar(nombre):
        spec = importlib.util.spec_from_file_location(nombre, backend / "migrations" / "versions" / f"{nombre}.py")
        modulo = importlib.util.module_from_spec(spec); spec.loader.exec_module(modulo)
        return modulo
    anterior, nueva = cargar("0004_e03_inicializacion"), cargar("0008_e03_preparacion_ml")
    from sqlalchemy import text
    with motor.begin() as conexion:
        contexto = MigrationContext.configure(conexion)
        with Operations.context(contexto):
            anterior.upgrade()
            conexion.execute(text("UPDATE configuracion_inicial SET estado='DATOS_CARGADOS', huella_solicitud='previa'"))
            nueva.upgrade()
            assert conexion.execute(text("SELECT estado,huella_solicitud,preparacion_numero FROM configuracion_inicial")).one() == ("DATOS_CARGADOS", "previa", 0)
            assert compare_metadata(contexto, Base.metadata) == []
            nueva.downgrade()
            assert conexion.execute(text("SELECT huella_solicitud FROM configuracion_inicial")).scalar() == "previa"
            nueva.upgrade()
            assert compare_metadata(contexto, Base.metadata) == []
    motor.dispose()


def test_migracion_0011_reversible_y_coherente_con_modelos():
    backend = Path(__file__).resolve().parents[2]
    motor = create_engine("sqlite://")
    @event.listens_for(motor, "connect")
    def funciones(c, _):
        c.create_function("char_length", 1, len)
        c.execute("PRAGMA foreign_keys=ON")
    nuevas = {"propuesta_compra", "pedido_compra", "linea_pedido", "envio_pedido", "recuperacion_envio"}
    Base.metadata.create_all(motor, tables=[t for t in Base.metadata.sorted_tables if t.name not in nuevas])
    spec = importlib.util.spec_from_file_location("l02", backend / "migrations/versions/0011_l02_compras.py")
    modulo = importlib.util.module_from_spec(spec); spec.loader.exec_module(modulo)
    spec_envio = importlib.util.spec_from_file_location("l03", backend / "migrations/versions/0013_l03_aprobacion_envio.py")
    envio = importlib.util.module_from_spec(spec_envio); spec_envio.loader.exec_module(envio)
    recuperacion = cargar_revision("0014_l04_recuperacion")
    with motor.begin() as conexion:
        contexto = MigrationContext.configure(conexion)
        with Operations.context(contexto):
            modulo.upgrade()
            envio.upgrade()
            recuperacion.upgrade()
            assert compare_metadata(contexto, Base.metadata) == []
            recuperacion.downgrade()
            envio.downgrade()
            modulo.downgrade()
            assert not nuevas.intersection(inspect(conexion).get_table_names())
            modulo.upgrade()
            envio.upgrade()
            recuperacion.upgrade()
            assert compare_metadata(contexto, Base.metadata) == []
    motor.dispose()


def test_migracion_0012_conserva_proveedor_y_revoca_verificacion_heredada():
    from sqlalchemy import text
    backend = Path(__file__).resolve().parents[2]
    motor = create_engine("sqlite://")
    def cargar(nombre):
        spec = importlib.util.spec_from_file_location(nombre, backend / "migrations" / "versions" / f"{nombre}.py")
        modulo = importlib.util.module_from_spec(spec); spec.loader.exec_module(modulo)
        return modulo
    anterior = cargar("0007_l01_proveedores")
    nueva = cargar("0012_l03_telegram_config")
    with motor.begin() as conexion:
        contexto = MigrationContext.configure(conexion)
        with Operations.context(contexto):
            anterior.upgrade()
            conexion.execute(text("INSERT INTO proveedor (id,codigo,nombre,activo,chat_id_pruebas,destino_verificado,destino_verificado_en) VALUES (1,'TG','Prueba',true,'789',true,'2026-09-30')"))
            nueva.upgrade()
            assert conexion.execute(text("SELECT codigo,chat_id_pruebas,destino_verificado,destino_verificado_en,destino_credencial_huella FROM proveedor")).one() == ("TG", "789", False, None, None)
            nueva.downgrade()
            assert "destino_credencial_huella" not in {c["name"] for c in inspect(conexion).get_columns("proveedor")}
            nueva.upgrade()
            assert conexion.execute(text("SELECT count(*) FROM proveedor")).scalar() == 1
    motor.dispose()


def test_migracion_0013_conserva_borradores_y_protege_evidencia():
    from sqlalchemy import text
    backend = Path(__file__).resolve().parents[2]
    motor = create_engine("sqlite://")
    @event.listens_for(motor,"connect")
    def funciones(c,_): c.create_function("char_length",1,len)
    nuevas = {"propuesta_compra","pedido_compra","linea_pedido","envio_pedido","recuperacion_envio"}
    Base.metadata.create_all(motor,tables=[t for t in Base.metadata.sorted_tables if t.name not in nuevas])
    def cargar(nombre):
        spec=importlib.util.spec_from_file_location(nombre,backend/"migrations/versions"/f"{nombre}.py")
        modulo=importlib.util.module_from_spec(spec); spec.loader.exec_module(modulo)
        return modulo
    anterior,nueva=cargar("0011_l02_compras"),cargar("0013_l03_aprobacion_envio")
    recuperacion = cargar_revision("0014_l04_recuperacion")
    with motor.begin() as conexion:
        contexto=MigrationContext.configure(conexion)
        with Operations.context(contexto):
            anterior.upgrade()
            conexion.execute(text("INSERT INTO propuesta_compra (id,plan_id,fecha_objetivo,estado,activa,modo_envio,necesidades_json,incidencias_json) VALUES (1,1,'2022-08-24','GENERADA',true,'REQUIERE_APROBACION','{}','[]')"))
            conexion.execute(text("INSERT INTO pedido_compra (id,propuesta_id,plan_id,proveedor_id,proveedor_json,estado,modo_envio,bloqueos_json) VALUES (1,1,1,1,'{}','PENDIENTE_APROBACION','REQUIERE_APROBACION','[]')"))
            nueva.upgrade()
            recuperacion.upgrade()
            assert conexion.execute(text("SELECT estado,clave_decision,decidido_por,decision_json FROM pedido_compra")).one()==("PENDIENTE_APROBACION",None,None,None)
            assert compare_metadata(contexto,Base.metadata)==[]
            recuperacion.downgrade()
            nueva.downgrade()
            assert conexion.execute(text("SELECT estado FROM pedido_compra")).scalar()=="PENDIENTE_APROBACION"
            nueva.upgrade()
            conexion.execute(text("UPDATE pedido_compra SET estado='RECHAZADO',clave_decision='fixture',decidido_por=1,decidido_en='2026-09-30',decision_json='{}'"))
            with pytest.raises(RuntimeError,match="conservar su evidencia"): nueva.downgrade()
            assert "envio_pedido" in inspect(conexion).get_table_names()
            assert conexion.execute(text("SELECT clave_decision FROM pedido_compra")).scalar()=="fixture"
    motor.dispose()


def test_migracion_0014_conserva_envio_reversible_y_protege_recuperaciones():
    from sqlalchemy import text
    motor = create_engine("sqlite://")
    @event.listens_for(motor, "connect")
    def funciones(c, _): c.create_function("char_length", 1, len)
    nuevas = {"propuesta_compra", "pedido_compra", "linea_pedido", "envio_pedido", "recuperacion_envio"}
    Base.metadata.create_all(motor, tables=[t for t in Base.metadata.sorted_tables if t.name not in nuevas])
    l02, l03, l04 = (cargar_revision(n) for n in ("0011_l02_compras", "0013_l03_aprobacion_envio", "0014_l04_recuperacion"))
    with motor.begin() as conexion:
        contexto = MigrationContext.configure(conexion)
        with Operations.context(contexto):
            l02.upgrade(); l03.upgrade()
            conexion.execute(text("INSERT INTO propuesta_compra (id,plan_id,fecha_objetivo,estado,activa,modo_envio,necesidades_json,incidencias_json) VALUES (1,1,'2022-08-24','GENERADA',true,'AUTOMATICO','{}','[]')"))
            conexion.execute(text("INSERT INTO pedido_compra (id,propuesta_id,plan_id,proveedor_id,proveedor_json,estado,modo_envio,bloqueos_json) VALUES (1,1,1,1,'{}','ENVIADO','AUTOMATICO','[]')"))
            conexion.execute(text("INSERT INTO envio_pedido (id,pedido_id,numero_intento,estado,chat_id,credencial_huella,texto,fin_en,message_id) VALUES (1,1,1,'ENVIADO','123',:huella,'DEMOSTRACION conservada','2026-10-01',42)"), {"huella": "a"*64})
            consulta = text("SELECT numero_intento,estado,chat_id,texto,message_id FROM envio_pedido")
            previo = conexion.execute(consulta).one()
            l04.upgrade()
            assert conexion.execute(consulta).one() == previo
            assert compare_metadata(contexto, Base.metadata) == []
            l04.downgrade()
            assert conexion.execute(consulta).one() == previo
            assert "recuperacion_envio" not in inspect(conexion).get_table_names()
            l04.upgrade()
            conexion.execute(text("INSERT INTO recuperacion_envio (envio_id,clave_idempotencia,accion,usuario_id,nombre_usuario,evidencia,solicitud_json,resultado_anterior_json) VALUES (1,'fixture','CONFIRMAR_ENVIO',1,'Fixture','Evidencia de fixture aislada','{}','{}')"))
            with pytest.raises(RuntimeError, match="conservar su evidencia"):
                l04.downgrade()
            assert conexion.execute(consulta).one() == previo
            assert conexion.execute(text("SELECT count(*) FROM recuperacion_envio")).scalar() == 1
    motor.dispose()
