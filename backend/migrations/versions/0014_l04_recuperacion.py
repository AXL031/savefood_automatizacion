"""Intentos conservados y conciliación humana; no reescribe evidencia anterior."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0014_l04_recuperacion"
down_revision = "0013_l03_aprobacion_envio"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("envio_pedido") as tabla:
        tabla.drop_constraint("uq_envio_pedido_unico", type_="unique")
        tabla.drop_constraint("ck_envio_numero", type_="check")
        tabla.create_unique_constraint("uq_envio_pedido_intento", ["pedido_id", "numero_intento"])
        tabla.create_unique_constraint("uq_envio_evidencia_telegram", ["chat_id", "message_id"])
        tabla.create_check_constraint("ck_envio_numero", "numero_intento >= 1")
    op.create_table("recuperacion_envio",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("envio_id", sa.Integer(), sa.ForeignKey("envio_pedido.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("clave_idempotencia", sa.String(80), nullable=False),
        sa.Column("accion", sa.String(24), nullable=False),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuario.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("nombre_usuario", sa.String(150), nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("evidencia", sa.String(1500), nullable=False),
        sa.Column("solicitud_json", sa.JSON().with_variant(postgresql.JSONB(), "postgresql"), nullable=False),
        sa.Column("resultado_anterior_json", sa.JSON().with_variant(postgresql.JSONB(), "postgresql"), nullable=False),
        sa.Column("nuevo_envio_id", sa.Integer(), sa.ForeignKey("envio_pedido.id", ondelete="RESTRICT")),
        sa.UniqueConstraint("clave_idempotencia", name="uq_recuperacion_clave"),
        sa.CheckConstraint("accion IN ('CONFIRMAR_ENVIO','CONFIRMAR_NO_ENVIO','REINTENTAR')", name="ck_recuperacion_accion"),
        sa.CheckConstraint("length(evidencia) BETWEEN 10 AND 1500", name="ck_recuperacion_evidencia"),
    )


def downgrade():
    conexion = op.get_bind()
    if (conexion.execute(sa.text("SELECT count(*) FROM recuperacion_envio")).scalar()
            or conexion.execute(sa.text("SELECT count(*) FROM envio_pedido WHERE numero_intento > 1")).scalar()):
        raise RuntimeError("Hay recuperaciones o reintentos: conservar su evidencia con una migración correctiva.")
    op.drop_table("recuperacion_envio")
    with op.batch_alter_table("envio_pedido") as tabla:
        tabla.drop_constraint("uq_envio_pedido_intento", type_="unique")
        tabla.drop_constraint("uq_envio_evidencia_telegram", type_="unique")
        tabla.drop_constraint("ck_envio_numero", type_="check")
        tabla.create_unique_constraint("uq_envio_pedido_unico", ["pedido_id"])
        tabla.create_check_constraint("ck_envio_numero", "numero_intento = 1")
