"""Tienda del cliente T02: clientes autenticados con Google (ADR-009)."""
from alembic import op
import sqlalchemy as sa

revision = "0019_tienda_clientes"
down_revision = "0018_recepcion_compras"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "cliente",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("google_sub", sa.String(255), nullable=False),
        sa.Column("correo", sa.String(254), nullable=False),
        sa.Column("nombre", sa.String(160), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ultimo_acceso_en", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("google_sub"),
    )


def downgrade():
    if op.get_bind().execute(sa.text("SELECT count(*) FROM cliente")).scalar():
        raise RuntimeError("Hay clientes registrados; conservarlos con una migración correctiva.")
    op.drop_table("cliente")
