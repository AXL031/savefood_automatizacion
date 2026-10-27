"""Ciclo operativo, respuestas proveedor y tienda real.

Revision ID: 0020_operacion_integrada
Revises: 0019_tienda_clientes
"""
from alembic import op
import sqlalchemy as sa

revision = '0020_operacion_integrada'
down_revision = '0019_tienda_clientes'
branch_labels = depends_on = None


def upgrade():
    op.create_table('registro_operacion', sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('clave', sa.String(100), unique=True, nullable=False), sa.Column('tipo', sa.String(24), nullable=False),
        sa.Column('usuario_id', sa.Integer, sa.ForeignKey('usuario.id', ondelete='RESTRICT')),
        sa.Column('cliente_id', sa.Integer, sa.ForeignKey('cliente.id', ondelete='RESTRICT')),
        sa.Column('plan_id', sa.Integer, sa.ForeignKey('plan_produccion.id', ondelete='RESTRICT')),
        sa.Column('fecha', sa.Date, nullable=False), sa.Column('solicitud', sa.JSON, nullable=False),
        sa.Column('resultado', sa.JSON, nullable=False), sa.Column('creado_en', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("tipo in ('PRODUCCION','VENTA_INTERNA','VENTA_TIENDA','RECEPCION','PRECIO')", name='ck_registro_operacion_tipo'))
    op.create_table('configuracion_operacion', sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('datos', sa.JSON, nullable=False), sa.Column('proxima_revision', sa.DateTime(timezone=True)))
    op.create_table('aviso_operacion', sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('clave', sa.String(140), unique=True, nullable=False), sa.Column('titulo', sa.String(200), nullable=False),
        sa.Column('datos', sa.JSON, nullable=False), sa.Column('leido', sa.Boolean, nullable=False),
        sa.Column('resolucion', sa.String(1000)), sa.Column('resuelto_por', sa.Integer, sa.ForeignKey('usuario.id', ondelete='RESTRICT')),
        sa.Column('creado_en', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table('solicitud_proveedor', sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('pedido_id', sa.Integer, sa.ForeignKey('pedido_compra.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('token_hash', sa.String(64), unique=True, nullable=False), sa.Column('estado', sa.String(24), nullable=False),
        sa.Column('expira_en', sa.DateTime(timezone=True), nullable=False), sa.Column('respuesta', sa.JSON),
        sa.Column('creado_en', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index('ix_solicitud_proveedor_pedido_id', 'solicitud_proveedor', ['pedido_id'])
    op.create_table('ficha_tienda', sa.Column('producto_id', sa.Integer, sa.ForeignKey('producto.id', ondelete='RESTRICT'), primary_key=True),
        sa.Column('precio', sa.Numeric(12,2), nullable=False), sa.Column('version', sa.Integer, nullable=False),
        sa.Column('datos', sa.JSON, nullable=False), sa.CheckConstraint('precio > 0', name='ck_ficha_precio'))
    op.create_table('promocion_operacion', sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('clave', sa.String(120), unique=True, nullable=False),
        sa.Column('lote_id', sa.Integer, sa.ForeignKey('lote_producto.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('regla_id', sa.Integer, sa.ForeignKey('regla_promocion_demo.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('estado', sa.String(24), nullable=False), sa.Column('descuento', sa.Integer), sa.Column('motivo', sa.String(500), nullable=False),
        sa.Column('fecha', sa.Date, nullable=False), sa.Column('decidido_por', sa.Integer, sa.ForeignKey('usuario.id', ondelete='RESTRICT')),
        sa.Column('creado_en', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_table('cuenta_cliente_local', sa.Column('cliente_id', sa.Integer, sa.ForeignKey('cliente.id', ondelete='RESTRICT'), primary_key=True),
        sa.Column('correo', sa.String(254), unique=True, nullable=False), sa.Column('hash_contrasena', sa.String(255), nullable=False))
    with op.batch_alter_table('movimiento_inventario') as b:
        b.drop_constraint('ck_movimiento_inventario_tipo', type_='check')
        b.create_check_constraint('ck_movimiento_inventario_tipo', "tipo in ('APERTURA', 'AJUSTE', 'RECEPCION', 'PRODUCCION', 'VENTA', 'VENTA_TIENDA')")


def downgrade():
    c = op.get_bind()
    if c.execute(sa.text("SELECT count(*) FROM registro_operacion")).scalar() or c.execute(sa.text("SELECT count(*) FROM movimiento_inventario WHERE tipo in ('PRODUCCION','VENTA','VENTA_TIENDA')")).scalar():
        raise RuntimeError('No se elimina historia operativa: respalda y conserva la revisión 0020.')
    with op.batch_alter_table('movimiento_inventario') as b:
        b.drop_constraint('ck_movimiento_inventario_tipo', type_='check')
        b.create_check_constraint('ck_movimiento_inventario_tipo', "tipo in ('APERTURA', 'AJUSTE', 'RECEPCION')")
    for name in ['cuenta_cliente_local','promocion_operacion','ficha_tienda','solicitud_proveedor','aviso_operacion','configuracion_operacion','registro_operacion']:
        op.drop_table(name)
