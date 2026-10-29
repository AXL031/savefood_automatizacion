"""Backport compatible de Bohorquez: producción, proveedores, avisos y monitor.

Revision ID: 0023_operaciones_compatibles
Revises: 0022_entradas_productos
"""
from alembic import op
import sqlalchemy as sa

revision = '0023_operaciones_compatibles'
down_revision = '0022_entradas_productos'
branch_labels = depends_on = None


def upgrade():
    op.create_table('registro_operacion', sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('clave', sa.String(100), unique=True, nullable=False), sa.Column('tipo', sa.String(24), nullable=False),
        sa.Column('usuario_id', sa.Integer, sa.ForeignKey('usuario.id', ondelete='RESTRICT')),
        sa.Column('plan_id', sa.Integer, sa.ForeignKey('plan_produccion.id', ondelete='RESTRICT')),
        sa.Column('fecha', sa.Date, nullable=False), sa.Column('solicitud', sa.JSON, nullable=False),
        sa.Column('resultado', sa.JSON, nullable=False), sa.Column('creado_en', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("tipo in ('PRODUCCION','RECEPCION')", name='ck_registro_operacion_tipo'))
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
    op.create_table('promocion_operacion', sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('clave', sa.String(120), unique=True, nullable=False),
        sa.Column('lote_id', sa.Integer, sa.ForeignKey('lote_producto.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('regla_id', sa.Integer, sa.ForeignKey('regla_promocion_demo.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('estado', sa.String(24), nullable=False), sa.Column('descuento', sa.Integer), sa.Column('motivo', sa.String(500), nullable=False),
        sa.Column('fecha', sa.Date, nullable=False), sa.Column('decidido_por', sa.Integer, sa.ForeignKey('usuario.id', ondelete='RESTRICT')),
        sa.Column('creado_en', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index('ix_registro_operacion_usuario_id', 'registro_operacion', ['usuario_id'])
    op.create_index('ix_registro_operacion_plan_id', 'registro_operacion', ['plan_id'])
    op.create_index('ix_aviso_operacion_resuelto_por', 'aviso_operacion', ['resuelto_por'])
    op.create_index('ix_promocion_operacion_lote_id', 'promocion_operacion', ['lote_id'])
    op.create_index('ix_promocion_operacion_regla_id', 'promocion_operacion', ['regla_id'])
    op.create_index('ix_promocion_operacion_decidido_por', 'promocion_operacion', ['decidido_por'])
    with op.batch_alter_table('movimiento_inventario') as b:
        b.drop_constraint('ck_movimiento_inventario_tipo', type_='check')
        b.create_check_constraint('ck_movimiento_inventario_tipo', "tipo in ('APERTURA', 'AJUSTE', 'RECEPCION', 'VENTA', 'ANULA_VENTA', 'ENTRADA', 'PRODUCCION')")
        b.create_check_constraint('ck_movimiento_produccion_signo', "tipo <> 'PRODUCCION' OR ((lote_producto_id IS NOT NULL AND delta > 0) OR (lote_ingrediente_id IS NOT NULL AND delta < 0))")


def downgrade():
    c = op.get_bind()
    if any(c.execute(sa.text(f'SELECT count(*) FROM {tabla}')).scalar() for tabla in ('registro_operacion','configuracion_operacion','aviso_operacion','solicitud_proveedor','promocion_operacion')) or c.execute(sa.text("SELECT count(*) FROM movimiento_inventario WHERE tipo = 'PRODUCCION'")).scalar():
        raise RuntimeError('No se elimina historia operativa: respalda y conserva la revisión 0023.')
    with op.batch_alter_table('movimiento_inventario') as b:
        b.drop_constraint('ck_movimiento_produccion_signo', type_='check')
        b.drop_constraint('ck_movimiento_inventario_tipo', type_='check')
        b.create_check_constraint('ck_movimiento_inventario_tipo', "tipo in ('APERTURA', 'AJUSTE', 'RECEPCION', 'VENTA', 'ANULA_VENTA', 'ENTRADA')")
    for name in ['promocion_operacion','solicitud_proveedor','aviso_operacion','configuracion_operacion','registro_operacion']:
        op.drop_table(name)
