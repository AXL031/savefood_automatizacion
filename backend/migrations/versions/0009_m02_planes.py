"""M02/M03: planes y necesidades; revisión nueva tras 0008."""
from alembic import op
import sqlalchemy as sa

revision = "0009_m02_planes"
down_revision = "0008_e03_modelo"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('plan_produccion',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('corrida_id', sa.Integer(), nullable=False),
    sa.Column('ejecucion_id', sa.Integer(), nullable=False),
    sa.Column('clave_ejecucion', sa.String(length=128), nullable=False),
    sa.Column('huella_stock_recetas', sa.String(length=64), nullable=False),
    sa.Column('fecha_objetivo', sa.Date(), nullable=False),
    sa.Column('stock_leido_en', sa.DateTime(timezone=True), nullable=False),
    sa.Column('estado', sa.String(length=20), nullable=False),
    sa.Column('trazas_json', sa.JSON(), nullable=False),
    sa.Column('creado_en', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.CheckConstraint("estado = 'PROPUESTO'", name='ck_plan_estado'),
    sa.ForeignKeyConstraint(['corrida_id'], ['corrida_pronostico.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['ejecucion_id'], ['ejecucion_automatizacion.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('clave_ejecucion', name='uq_plan_clave')
    )
    op.create_index(op.f('ix_plan_produccion_corrida_id'), 'plan_produccion', ['corrida_id'], unique=False)
    op.create_table('elemento_plan',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('plan_id', sa.Integer(), nullable=False),
    sa.Column('producto_id', sa.Integer(), nullable=False),
    sa.Column('pronostico_id', sa.Integer(), nullable=False),
    sa.Column('receta_id', sa.Integer(), nullable=False),
    sa.Column('cantidad_pronosticada', sa.Integer(), nullable=False),
    sa.Column('stock_disponible', sa.Integer(), nullable=False),
    sa.Column('cantidad_producir', sa.Integer(), nullable=False),
    sa.Column('vigencia_stock_desconocida', sa.Boolean(), nullable=False),
    sa.CheckConstraint('cantidad_pronosticada >= 0 AND stock_disponible >= 0 AND cantidad_producir >= 0', name='ck_elemento_plan_cantidades'),
    sa.ForeignKeyConstraint(['plan_id'], ['plan_produccion.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['producto_id'], ['producto.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['pronostico_id'], ['pronostico.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['receta_id'], ['receta.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('plan_id', 'producto_id', name='uq_elemento_plan_producto')
    )
    op.create_table('necesidad_ingrediente',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('plan_id', sa.Integer(), nullable=False),
    sa.Column('ingrediente_id', sa.Integer(), nullable=False),
    sa.Column('cantidad_requerida', sa.Numeric(precision=18, scale=3), nullable=False),
    sa.Column('cantidad_disponible', sa.Numeric(precision=18, scale=3), nullable=True),
    sa.Column('cantidad_faltante', sa.Numeric(precision=18, scale=3), nullable=True),
    sa.Column('unidad', sa.String(length=20), nullable=False),
    sa.Column('stock_conocido', sa.Boolean(), nullable=False),
    sa.Column('vigencia_stock_desconocida', sa.Boolean(), nullable=False),
    sa.CheckConstraint('(stock_conocido AND cantidad_disponible IS NOT NULL AND cantidad_faltante IS NOT NULL AND cantidad_disponible >= 0 AND cantidad_faltante >= 0) OR (NOT stock_conocido AND cantidad_disponible IS NULL AND cantidad_faltante IS NULL)', name='ck_necesidad_stock'),
    sa.CheckConstraint('cantidad_requerida >= 0', name='ck_necesidad_requerida'),
    sa.ForeignKeyConstraint(['ingrediente_id'], ['ingrediente.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['plan_id'], ['plan_produccion.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('plan_id', 'ingrediente_id', name='uq_necesidad_plan_ingrediente')
    )

def downgrade():
    op.drop_table('necesidad_ingrediente')
    op.drop_table('elemento_plan')
    op.drop_index(op.f('ix_plan_produccion_corrida_id'), table_name='plan_produccion')
    op.drop_table('plan_produccion')
