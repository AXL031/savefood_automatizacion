"""Aprobación automática configurable y modo conservado por sugerencia."""
from alembic import op
import sqlalchemy as sa

revision = '0025_modo_promociones'
down_revision = '0024_comercio_tienda'
branch_labels = depends_on = None


def upgrade():
    with op.batch_alter_table('negocio') as b:
        b.add_column(sa.Column('modo_publicacion_promociones', sa.String(20), nullable=False, server_default='REQUIERE_APROBACION'))
        b.create_check_constraint('ck_negocio_modo_promociones', "modo_publicacion_promociones IN ('REQUIERE_APROBACION','AUTOMATICO')")
    with op.batch_alter_table('promocion_operacion') as b:
        b.add_column(sa.Column('modo_publicacion', sa.String(20), nullable=False, server_default='REQUIERE_APROBACION'))
        b.create_check_constraint('ck_promocion_modo_publicacion', "modo_publicacion IN ('REQUIERE_APROBACION','AUTOMATICO')")


def downgrade():
    # Eliminar el snapshot borraría la evidencia de cómo se autorizó una promoción.
    raise RuntimeError('Conservar el modo de las promociones; restaurar un respaldo para retroceder.')
