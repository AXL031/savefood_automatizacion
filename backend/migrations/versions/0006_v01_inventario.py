"""Tablas del corte 0006_v01_inventario; cadena única sin reescribir revisiones previas."""

from alembic import op
import sqlalchemy as sa

revision = "0006_v01_inventario"
down_revision = "0005_m01_ingredientes_recetas"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('lote_ingrediente',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ingrediente_id', sa.Integer(), nullable=False),
    sa.Column('codigo_lote', sa.String(length=80), nullable=False),
    sa.Column('lote_informado', sa.Boolean(), nullable=False),
    sa.Column('fecha_caducidad', sa.Date(), nullable=True),
    sa.Column('saldo_disponible', sa.Numeric(precision=14, scale=3), nullable=False),
    sa.Column('creado_en', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.Column('actualizado_en', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.CheckConstraint('length(trim(codigo_lote)) > 0', name='ck_lote_ingrediente_codigo'),
    sa.CheckConstraint('saldo_disponible >= 0', name='ck_lote_ingrediente_saldo'),
    sa.ForeignKeyConstraint(['ingrediente_id'], ['ingrediente.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('ingrediente_id', 'codigo_lote', name='uq_lote_ingrediente_codigo')
    )
    op.create_table('lote_producto',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('producto_id', sa.Integer(), nullable=False),
    sa.Column('codigo_lote', sa.String(length=80), nullable=False),
    sa.Column('lote_informado', sa.Boolean(), nullable=False),
    sa.Column('fecha_caducidad', sa.Date(), nullable=True),
    sa.Column('fecha_limite_venta', sa.Date(), nullable=True),
    sa.Column('saldo_disponible', sa.Integer(), nullable=False),
    sa.Column('creado_en', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.Column('actualizado_en', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.CheckConstraint('fecha_limite_venta is null or fecha_caducidad is null or fecha_limite_venta <= fecha_caducidad', name='ck_lote_producto_limite_venta'),
    sa.CheckConstraint('length(trim(codigo_lote)) > 0', name='ck_lote_producto_codigo'),
    sa.CheckConstraint('saldo_disponible >= 0', name='ck_lote_producto_saldo'),
    sa.ForeignKeyConstraint(['producto_id'], ['producto.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('producto_id', 'codigo_lote', name='uq_lote_producto_codigo')
    )
    op.create_table('movimiento_inventario',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('lote_ingrediente_id', sa.Integer(), nullable=True),
    sa.Column('lote_producto_id', sa.Integer(), nullable=True),
    sa.Column('delta', sa.Numeric(precision=14, scale=3), nullable=False),
    sa.Column('saldo_resultante', sa.Numeric(precision=14, scale=3), nullable=False),
    sa.Column('tipo', sa.String(length=12), nullable=False),
    sa.Column('clave_operacion', sa.String(length=200), nullable=False),
    sa.Column('motivo', sa.String(length=300), nullable=False),
    sa.Column('usuario_id', sa.Integer(), nullable=True),
    sa.Column('efectivo_en_demo', sa.DateTime(), nullable=False),
    sa.Column('creado_en', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.CheckConstraint("tipo in ('APERTURA', 'AJUSTE')", name='ck_movimiento_inventario_tipo'),
    sa.CheckConstraint('(lote_ingrediente_id is null) <> (lote_producto_id is null)', name='ck_movimiento_inventario_un_lote'),
    sa.CheckConstraint('delta <> 0', name='ck_movimiento_inventario_delta'),
    sa.CheckConstraint('length(trim(motivo)) > 0', name='ck_movimiento_inventario_motivo'),
    sa.CheckConstraint('lote_producto_id is null or delta = round(delta, 0)', name='ck_movimiento_inventario_delta_entero_producto'),
    sa.CheckConstraint('saldo_resultante >= 0', name='ck_movimiento_inventario_saldo'),
    sa.ForeignKeyConstraint(['lote_ingrediente_id'], ['lote_ingrediente.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['lote_producto_id'], ['lote_producto.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['usuario_id'], ['usuario.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('clave_operacion', name='uq_movimiento_inventario_clave')
    )
    op.create_index('ix_movimiento_inventario_lote_ingrediente', 'movimiento_inventario', ['lote_ingrediente_id'], unique=False)
    op.create_index('ix_movimiento_inventario_lote_producto', 'movimiento_inventario', ['lote_producto_id'], unique=False)

def downgrade():
    op.drop_index('ix_movimiento_inventario_lote_producto', table_name='movimiento_inventario')
    op.drop_index('ix_movimiento_inventario_lote_ingrediente', table_name='movimiento_inventario')
    op.drop_table('movimiento_inventario')
    op.drop_table('lote_producto')
    op.drop_table('lote_ingrediente')
