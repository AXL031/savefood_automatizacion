"""Decisiones administrativas y outbox de envío; sin modificar revisiones previas."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0013_l03_aprobacion_envio"
down_revision = "0012_l03_telegram_config"
branch_labels = None
depends_on = None

ESTADOS = "estado IN ('BLOQUEADO','PENDIENTE_APROBACION','CANCELADO','RECHAZADO','PENDIENTE_ENVIO','ENVIANDO','ENVIADO','FALLIDO','PENDIENTE_VERIFICACION')"
DECISION = "(clave_decision IS NULL AND decidido_por IS NULL AND decidido_en IS NULL AND decision_json IS NULL) OR (clave_decision IS NOT NULL AND decidido_por IS NOT NULL AND decidido_en IS NOT NULL AND decision_json IS NOT NULL)"


def upgrade():
    json_tipo = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")
    with op.batch_alter_table("pedido_compra") as tabla:
        tabla.drop_constraint("ck_pedido_compra_estado", type_="check")
        tabla.add_column(sa.Column("clave_decision", sa.String(80)))
        tabla.add_column(sa.Column("decidido_por", sa.Integer()))
        tabla.add_column(sa.Column("decidido_en", sa.DateTime(timezone=True)))
        tabla.add_column(sa.Column("decision_json", json_tipo))
        tabla.create_foreign_key("fk_pedido_decidido_por", "usuario", ["decidido_por"], ["id"], ondelete="RESTRICT")
        tabla.create_unique_constraint("uq_pedido_clave_decision", ["clave_decision"])
        tabla.create_check_constraint("ck_pedido_compra_estado", ESTADOS)
        tabla.create_check_constraint("ck_pedido_decision_completa", DECISION)
    op.create_table("envio_pedido",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("pedido_id", sa.Integer(), sa.ForeignKey("pedido_compra.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("numero_intento", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("estado", sa.String(24), nullable=False),
        sa.Column("chat_id", sa.String(64), nullable=False),
        sa.Column("credencial_huella", sa.String(64), nullable=False),
        sa.Column("texto", sa.Text(), nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("inicio_en", sa.DateTime(timezone=True)),
        sa.Column("fin_en", sa.DateTime(timezone=True)),
        sa.Column("fecha_telegram", sa.DateTime(timezone=True)),
        sa.Column("message_id", sa.BigInteger()),
        sa.Column("codigo_error", sa.String(64)),
        sa.Column("detalle_error", sa.String(500)),
        sa.Column("despachado_en", sa.DateTime(timezone=True)),
        sa.Column("lease_hasta", sa.DateTime(timezone=True)),
        sa.Column("token_despacho", sa.String(36)),
        sa.UniqueConstraint("pedido_id", name="uq_envio_pedido_unico"),
        sa.CheckConstraint("numero_intento = 1", name="ck_envio_numero"),
        sa.CheckConstraint("estado IN ('PENDIENTE_ENVIO','ENVIANDO','ENVIADO','FALLIDO','PENDIENTE_VERIFICACION')", name="ck_envio_estado"),
        sa.CheckConstraint("(estado = 'ENVIADO' AND message_id IS NOT NULL AND message_id > 0 AND fin_en IS NOT NULL) OR (estado <> 'ENVIADO' AND message_id IS NULL)", name="ck_envio_confirmacion"))
    op.create_index("ix_envio_pendiente", "envio_pedido", ["estado", "lease_hasta"])


def downgrade():
    actividad = op.get_bind().scalar(sa.text("SELECT count(*) FROM pedido_compra WHERE clave_decision IS NOT NULL"))
    if actividad:
        raise RuntimeError("No revertir 0013 con decisiones de pedidos: conservar su evidencia y usar migración correctiva.")
    op.drop_table("envio_pedido")
    with op.batch_alter_table("pedido_compra") as tabla:
        tabla.drop_constraint("ck_pedido_compra_estado", type_="check")
        tabla.drop_constraint("ck_pedido_decision_completa", type_="check")
        tabla.drop_constraint("uq_pedido_clave_decision", type_="unique")
        tabla.drop_constraint("fk_pedido_decidido_por", type_="foreignkey")
        for columna in ("clave_decision", "decidido_por", "decidido_en", "decision_json"):
            tabla.drop_column(columna)
        tabla.create_check_constraint("ck_pedido_compra_estado", "estado IN ('BLOQUEADO','PENDIENTE_APROBACION','CANCELADO')")
