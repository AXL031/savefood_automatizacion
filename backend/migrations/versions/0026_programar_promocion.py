"""Programación explícita de una promoción con trazas del motor existente."""
from alembic import op
import sqlalchemy as sa

revision = '0026_programar_promocion'
down_revision = '0025_modo_promociones'
branch_labels = depends_on = None


def upgrade():
    op.add_column('promocion_operacion', sa.Column('programacion', sa.JSON(), nullable=True))


def downgrade():
    # JSON null puede ser una cadena JSON en SQLite o un SQL NULL en PostgreSQL.
    c=op.get_bind()
    if any(valor not in (None,'null') for valor in c.execute(sa.text('SELECT programacion FROM promocion_operacion')).scalars()):
        raise RuntimeError('Conservar las trazas de programación; revisar un respaldo para retroceder.')
    op.drop_column('promocion_operacion','programacion')
