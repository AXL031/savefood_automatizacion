"""0024 preserva cotizaciones/tickets/líneas existentes y bloquea borrar evidencia."""
from datetime import datetime, date, timezone, timedelta
from uuid import uuid4
import pytest
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, event, inspect, insert, text, MetaData, Table
from app.core.base import Base
from app.principal import app  # noqa
from app.modules.autenticacion.modelos import Usuario
from app.modules.productos.modelos import Producto
from app.modules.ventas.modelos_caja import PrecioVenta
from test_migraciones_entregas import cargar_revision


def test_0024_preserva_caja_y_protege_publicacion():
    motor=create_engine('sqlite://')
    @event.listens_for(motor,'connect')
    def funciones(c,_):c.create_function('char_length',1,len)
    Base.metadata.create_all(motor)
    revision=cargar_revision('0024_comercio_tienda')
    with motor.begin() as c:
        with Operations.context(MigrationContext.configure(c)):
            revision.downgrade()
            c.execute(insert(Usuario).values(id=1,correo='fixture@example.com',nombre='QA',rol='ADMINISTRADOR',activo=True,hash_contrasena='fixture'))
            c.execute(insert(Producto).values(id=1,codigo='PAN',nombre='Pan',activo=True,demostrar=False))
            c.execute(insert(PrecioVenta).values(id=1,producto_id=1,usuario_id=1,clave='precio-anterior',huella='a'*64,version=1,precio='2.50'))
            ahora=datetime(2026,10,28,15,tzinfo=timezone.utc);cotid=str(uuid4());metadata=MetaData()
            cot=Table('cotizacion_venta',metadata,autoload_with=c)
            ticket=Table('ticket_venta',metadata,autoload_with=c)
            linea=Table('linea_ticket_venta',metadata,autoload_with=c)
            c.execute(cot.insert().values(id=cotid,usuario_id=1,clave='cot-anterior',huella='b'*64,lineas=[],total='5.00',moneda='PEN',vence_en=ahora+timedelta(minutes=5),creado_en=ahora))
            c.execute(ticket.insert().values(id=1,cotizacion_id=cotid,usuario_id=1,nombre_usuario='QA',clave='venta-anterior',huella='c'*64,canal='PRESENCIAL',estado='CONFIRMADA',total='5.00',moneda='PEN',cobro={},vendida_en=ahora,fecha_local=date(2026,10,28),zona_horaria='America/Lima'))
            c.execute(linea.insert().values(id=1,ticket_id=1,producto_id=1,precio_id=1,nombre='Pan anterior',codigo='PAN',cantidad=2,precio='2.50',subtotal='5.00'))
            anteriores={t.name:c.execute(t.select()).all() for t in (cot,ticket,linea)}
            revision.upgrade()
            assert compare_metadata(MigrationContext.configure(c),Base.metadata)==[]
            for t in (cot,ticket,linea):assert c.execute(t.select()).all()==anteriores[t.name]
            assert c.execute(text('SELECT canal,integracion_id FROM cotizacion_venta')).one()==('PRESENCIAL',None)
            assert c.execute(text('SELECT segmentos FROM linea_ticket_venta')).scalar_one() is None
            revision.downgrade();revision.upgrade()
            c.execute(text("INSERT INTO configuracion_comercio (id,origen,version) VALUES (1,:origen,0)"),{'origen':str(uuid4())})
            with pytest.raises(RuntimeError,match='Conservar evidencia'):revision.downgrade()
            assert c.execute(text('SELECT count(*) FROM ticket_venta')).scalar_one()==1
    motor.dispose()
