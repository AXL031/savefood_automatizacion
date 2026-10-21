"""Registro durable de mensajes de prueba solicitados por administrador."""
from alembic import op
import sqlalchemy as sa

revision = "0017_pruebas_proveedor"
down_revision = "0016_nombre_comercio"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("prueba_mensaje_proveedor",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("proveedor_id", sa.Integer(), sa.ForeignKey("proveedor.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuario.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("clave_idempotencia", sa.String(80), nullable=False, unique=True),
        sa.Column("chat_id", sa.String(64), nullable=False),
        sa.Column("credencial_huella", sa.String(64), nullable=False),
        sa.Column("texto", sa.Text(), nullable=False),
        sa.Column("revision_chat_confirmada", sa.Boolean(), nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("estado", sa.String(24), nullable=False),
        sa.Column("message_id", sa.BigInteger(), nullable=True),
        sa.Column("fecha_telegram", sa.DateTime(timezone=True), nullable=True),
        sa.Column("detalle", sa.String(300), nullable=False),
        sa.CheckConstraint("estado IN ('ENVIADO','FALLIDO','PENDIENTE_VERIFICACION')", name="ck_prueba_proveedor_estado"))
    op.create_index("ix_prueba_mensaje_proveedor_proveedor_id", "prueba_mensaje_proveedor", ["proveedor_id"])


def downgrade():
    op.drop_table("prueba_mensaje_proveedor")
