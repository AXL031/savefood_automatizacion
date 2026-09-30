"""Tablas del corte 0007_l01_proveedores; cadena única sin reescribir revisiones previas."""

from alembic import op
import sqlalchemy as sa

revision = "0007_l01_proveedores"
down_revision = "0006_v01_inventario"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('proveedor',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('codigo', sa.String(length=30), nullable=False),
    sa.Column('nombre', sa.String(length=120), nullable=False),
    sa.Column('activo', sa.Boolean(), nullable=False),
    sa.Column('chat_id_pruebas', sa.String(length=64), nullable=True),
    sa.Column('destino_verificado', sa.Boolean(), nullable=False),
    sa.Column('destino_verificado_en', sa.DateTime(timezone=True), nullable=True),
    sa.CheckConstraint('length(trim(codigo)) > 0', name='ck_proveedor_codigo'),
    sa.CheckConstraint('length(trim(nombre)) > 0', name='ck_proveedor_nombre'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('codigo')
    )
    op.create_table('oferta_ingrediente',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('proveedor_id', sa.Integer(), nullable=False),
    sa.Column('ingrediente_id', sa.Integer(), nullable=False),
    sa.Column('descripcion', sa.String(length=120), nullable=False),
    sa.Column('unidad_compra', sa.String(length=30), nullable=False),
    sa.Column('factor_conversion', sa.Numeric(precision=14, scale=4), nullable=False),
    sa.Column('minimo', sa.Numeric(precision=14, scale=4), nullable=False),
    sa.Column('multiplo', sa.Numeric(precision=14, scale=4), nullable=False),
    sa.Column('activa', sa.Boolean(), nullable=False),
    sa.Column('preferida', sa.Boolean(), nullable=False),
    sa.CheckConstraint('factor_conversion > 0', name='ck_oferta_factor'),
    sa.CheckConstraint('minimo >= 0', name='ck_oferta_minimo'),
    sa.CheckConstraint('multiplo > 0', name='ck_oferta_multiplo'),
    sa.ForeignKeyConstraint(['ingrediente_id'], ['ingrediente.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['proveedor_id'], ['proveedor.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_oferta_ingrediente_ingrediente_id'), 'oferta_ingrediente', ['ingrediente_id'], unique=False)
    op.create_index('uq_oferta_preferida_activa', 'oferta_ingrediente', ['ingrediente_id'], unique=True, sqlite_where=sa.text('preferida = 1 AND activa = 1'), postgresql_where=sa.text('preferida AND activa'))

def downgrade():
    op.drop_index('uq_oferta_preferida_activa', table_name='oferta_ingrediente', sqlite_where=sa.text('preferida = 1 AND activa = 1'), postgresql_where=sa.text('preferida AND activa'))
    op.drop_index(op.f('ix_oferta_ingrediente_ingrediente_id'), table_name='oferta_ingrediente')
    op.drop_table('oferta_ingrediente')
    op.drop_table('proveedor')
