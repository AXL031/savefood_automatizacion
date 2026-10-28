"""DDL 0022, preservación de saldos y protección del historial de entradas."""
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, MetaData, CheckConstraint, event, text, inspect, insert
import pytest
from app.core.base import Base
from app.principal import app  # noqa
from app.modules.autenticacion.modelos import Usuario
from app.modules.productos.modelos import Producto
from test_migraciones_entregas import cargar_revision


def test_migracion_0022_conserva_lotes_metadatos_y_bloquea_borrar_entradas():
    motor=create_engine("sqlite://")
    @event.listens_for(motor,"connect")
    def funciones(c,_): c.create_function("char_length",1,len)
    previo=MetaData()
    for tabla in Base.metadata.sorted_tables: tabla.to_metadata(previo)
    nuevas={"entrada_productos","linea_entrada_productos"}
    previo.tables["lote_producto"]._columns.remove(previo.tables["lote_producto"].c.fecha_ingreso)
    mov=previo.tables["movimiento_inventario"]
    for con in list(mov.constraints):
        if con.name in {"ck_movimiento_inventario_tipo","ck_movimiento_entrada_producto"}: mov.constraints.remove(con)
    mov.append_constraint(CheckConstraint("tipo in ('APERTURA', 'AJUSTE', 'RECEPCION', 'VENTA', 'ANULA_VENTA')",name="ck_movimiento_inventario_tipo"))
    previo.create_all(motor,tables=[t for t in previo.sorted_tables if t.name not in nuevas])
    revision=cargar_revision("0022_entradas_productos")
    with motor.begin() as c:
        c.execute(insert(Usuario).values(id=1,correo="qa@example.com",nombre="QA",rol="ADMINISTRADOR",activo=True,hash_contrasena="fixture"))
        c.execute(insert(Producto).values(id=1,codigo="PAN",nombre="Pan",activo=True,demostrar=False))
        c.execute(text("INSERT INTO lote_producto (id,producto_id,codigo_lote,lote_informado,saldo_disponible,fecha_caducidad,fecha_limite_venta) VALUES (1,1,'ANTERIOR',1,4,'2026-10-03','2026-10-02')"))
        ctx=MigrationContext.configure(c)
        with Operations.context(ctx):
            revision.upgrade()
            assert compare_metadata(ctx,Base.metadata)==[]
            assert c.execute(text("SELECT saldo_disponible,fecha_ingreso FROM lote_producto")).one()==(4,None)
            revision.downgrade()
            assert not nuevas.intersection(inspect(c).get_table_names())
            assert c.execute(text("SELECT saldo_disponible FROM lote_producto")).scalar_one()==4
            revision.upgrade()
            c.execute(text("INSERT INTO entrada_productos (usuario_id,nombre_usuario,clave,huella,fecha_entrada,motivo) VALUES (1,'QA','entrada-qa-001','hash','2026-10-28','Entrada QA')"))
            with pytest.raises(RuntimeError,match="entradas de productos conservadas"):
                revision.downgrade()
            assert c.execute(text("SELECT count(*) FROM entrada_productos")).scalar_one()==1
    motor.dispose()
