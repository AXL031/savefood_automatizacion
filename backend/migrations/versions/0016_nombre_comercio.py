"""Retira el nombre inicial de ejemplo sin modificar comercios configurados."""
from alembic import op
import sqlalchemy as sa

revision = "0016_nombre_comercio"
down_revision = "0015_flujo_promociones"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(sa.text("UPDATE negocio SET nombre = 'Mi comercio' "
                       "WHERE nombre = 'Comercio de demostración'"))


def downgrade():
    # El nombre es configuración del usuario: no sustituirlo al bajar revisión.
    pass
