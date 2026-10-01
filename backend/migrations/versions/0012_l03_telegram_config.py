"""Vincula la verificación a su credencial sin almacenar el token."""
from alembic import op
import sqlalchemy as sa

revision = "0012_l03_telegram_config"
down_revision = "0011_l02_compras"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("proveedor", sa.Column("destino_credencial_huella", sa.String(64), nullable=True))
    op.execute("UPDATE proveedor SET destino_verificado=false, destino_verificado_en=NULL")


def downgrade():
    # Las verificaciones nunca sobreviven a la pérdida de su evidencia.
    op.execute("UPDATE proveedor SET destino_verificado=false, destino_verificado_en=NULL")
    op.drop_column("proveedor", "destino_credencial_huella")
