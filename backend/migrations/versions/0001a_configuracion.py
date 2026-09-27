"""Agrega el modo de aprobación para pedidos futuros del prototipo."""

from alembic import op
import sqlalchemy as sa

revision = "0001a_configuracion"
down_revision = "0001_nucleo"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "negocio",
        sa.Column(
            "modo_envio_pedidos",
            sa.String(20),
            nullable=False,
            server_default="REQUIERE_APROBACION",
        ),
    )
    op.create_check_constraint(
        "ck_negocio_modo_envio_pedidos",
        "negocio",
        "modo_envio_pedidos IN ('REQUIERE_APROBACION', 'AUTOMATICO')",
    )


def downgrade():
    op.drop_constraint("ck_negocio_modo_envio_pedidos", "negocio", type_="check")
    op.drop_column("negocio", "modo_envio_pedidos")
