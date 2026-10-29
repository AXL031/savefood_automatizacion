"""Backport 0023 sobre stock/caja de Cueva: sin reescribir revisiones remotas."""
import pytest
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, MetaData, CheckConstraint, event, text, inspect, insert
from app.modules.autenticacion.modelos import Usuario
from app.modules.productos.modelos import Producto
from app.core.base import Base
from app.principal import app  # noqa
from test_migraciones_entregas import cargar_revision


def test_0023_preserva_movimientos_entrada_venta_anulacion_y_evidencia():
    motor=create_engine('sqlite://')
    @event.listens_for(motor,'connect')
    def funciones(c,_): c.create_function('char_length',1,len)
    previo=MetaData()
    nuevas={'registro_operacion','configuracion_operacion','aviso_operacion','solicitud_proveedor','promocion_operacion'}
    for tabla in Base.metadata.sorted_tables: tabla.to_metadata(previo)
    mov=previo.tables['movimiento_inventario']
    for con in list(mov.constraints):
        if con.name in {'ck_movimiento_inventario_tipo','ck_movimiento_produccion_signo'}: mov.constraints.remove(con)
    mov.append_constraint(CheckConstraint("tipo in ('APERTURA','AJUSTE','RECEPCION','VENTA','ANULA_VENTA','ENTRADA')",name='ck_movimiento_inventario_tipo'))
    previo.create_all(motor,tables=[t for t in previo.sorted_tables if t.name not in nuevas])
    revision=cargar_revision('0023_operaciones_compatibles')
    with motor.begin() as c:
        c.execute(insert(Usuario).values(id=1,correo='fixture@example.com',nombre='QA',rol='ADMINISTRADOR',activo=True,hash_contrasena='fixture'))
        c.execute(insert(Producto).values(id=1,codigo='PAN',nombre='Pan',activo=True,demostrar=False))
        c.execute(text("INSERT INTO lote_producto (id,producto_id,codigo_lote,lote_informado,saldo_disponible,fecha_ingreso,fecha_caducidad,fecha_limite_venta) VALUES (1,1,'EXISTENTE',1,5,'2026-10-28','2026-10-30','2026-10-30')"))
        for tipo,delta in [('ENTRADA',5),('VENTA',-1),('ANULA_VENTA',1)]:
            c.execute(text("INSERT INTO movimiento_inventario (lote_producto_id,delta,saldo_resultante,tipo,clave_operacion,motivo,usuario_id,efectivo_en_demo) VALUES (1,:delta,5,:tipo,:tipo,'QA',1,'2026-10-28')"),{'tipo':tipo,'delta':delta})
        antes=c.execute(text('SELECT * FROM movimiento_inventario ORDER BY id')).all()
        with Operations.context(MigrationContext.configure(c)):
            revision.upgrade()
            assert compare_metadata(MigrationContext.configure(c),Base.metadata)==[]
            assert c.execute(text('SELECT * FROM movimiento_inventario ORDER BY id')).all()==antes
            assert c.execute(text('SELECT saldo_disponible,fecha_ingreso FROM lote_producto')).one()==(5,'2026-10-28')
            revision.downgrade()
            assert not nuevas.intersection(inspect(c).get_table_names())
            revision.upgrade()
            c.execute(text("INSERT INTO aviso_operacion (clave,titulo,datos,leido) VALUES ('fixture','Aviso conservado','{}',0)"))
            with pytest.raises(RuntimeError,match='historia operativa'): revision.downgrade()
            assert c.execute(text('SELECT count(*) FROM aviso_operacion')).scalar_one()==1
    motor.dispose()
