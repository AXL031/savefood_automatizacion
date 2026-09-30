"""Tablas del corte 0005_m01_ingredientes_recetas; cadena única sin reescribir revisiones previas."""

from alembic import op
import sqlalchemy as sa

revision = "0005_m01_ingredientes_recetas"
down_revision = "0004_e03_inicializacion"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('ingrediente',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('codigo', sa.String(length=160), nullable=False),
    sa.Column('nombre', sa.String(length=160), nullable=False),
    sa.Column('unidad_base', sa.String(length=10), nullable=False),
    sa.Column('activo', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('creado_en', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.CheckConstraint("unidad_base in ('g', 'kg', 'ml', 'l', 'unidad')", name='ck_ingrediente_unidad_base'),
    sa.CheckConstraint('length(trim(codigo)) > 0', name='ck_ingrediente_codigo'),
    sa.CheckConstraint('length(trim(nombre)) > 0', name='ck_ingrediente_nombre'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('codigo', name='uq_ingrediente_codigo')
    )
    op.create_table('receta',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('producto_id', sa.Integer(), nullable=False),
    sa.Column('version', sa.Integer(), nullable=False),
    sa.Column('activo', sa.Boolean(), server_default='true', nullable=False),
    sa.Column('motivo', sa.String(length=300), nullable=True),
    sa.Column('creado_por', sa.Integer(), nullable=True),
    sa.Column('creado_en', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.CheckConstraint('version >= 1', name='ck_receta_version'),
    sa.ForeignKeyConstraint(['creado_por'], ['usuario.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['producto_id'], ['producto.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('producto_id', 'version', name='uq_receta_producto_version')
    )
    op.create_index('uq_receta_activa_por_producto', 'receta', ['producto_id'], unique=True, postgresql_where=sa.text('activo'), sqlite_where=sa.text('activo = 1'))
    op.create_table('receta_ingrediente',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('receta_id', sa.Integer(), nullable=False),
    sa.Column('ingrediente_id', sa.Integer(), nullable=False),
    sa.Column('cantidad_por_unidad', sa.Numeric(precision=14, scale=3), nullable=False),
    sa.CheckConstraint('cantidad_por_unidad > 0', name='ck_receta_ingrediente_cantidad'),
    sa.ForeignKeyConstraint(['ingrediente_id'], ['ingrediente.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['receta_id'], ['receta.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('receta_id', 'ingrediente_id', name='uq_receta_ingrediente_pareja')
    )
    op.create_index('ix_receta_ingrediente_ingrediente', 'receta_ingrediente', ['ingrediente_id'], unique=False)

def downgrade():
    op.drop_index('ix_receta_ingrediente_ingrediente', table_name='receta_ingrediente')
    op.drop_table('receta_ingrediente')
    op.drop_index('uq_receta_activa_por_producto', table_name='receta', postgresql_where=sa.text('activo'), sqlite_where=sa.text('activo = 1'))
    op.drop_table('receta')
    op.drop_table('ingrediente')
