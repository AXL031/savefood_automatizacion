"""Borradores trazables y reserva explícita de fecha; sin envío externo."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0011_l02_compras"
down_revision = "0010_m03_necesidades"
branch_labels = None
depends_on = None


def upgrade():
    json_tipo = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")
    op.create_table("propuesta_compra",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("plan_id", sa.Integer(), sa.ForeignKey("plan_produccion.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("fecha_objetivo", sa.Date(), nullable=False),
        sa.Column("estado", sa.String(24), nullable=False),
        sa.Column("activa", sa.Boolean(), nullable=False),
        sa.Column("modo_envio", sa.String(24), nullable=False),
        sa.Column("necesidades_json", json_tipo, nullable=False),
        sa.Column("incidencias_json", json_tipo, nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("cancelado_en", sa.DateTime(timezone=True)),
        sa.Column("cancelado_por", sa.Integer(), sa.ForeignKey("usuario.id", ondelete="RESTRICT")),
        sa.Column("motivo_cancelacion", sa.String(500)),
        sa.UniqueConstraint("plan_id", name="uq_propuesta_compra_plan"),
        sa.CheckConstraint("estado IN ('GENERADA','BLOQUEADA','SIN_FALTANTES','CANCELADA')", name="ck_propuesta_compra_estado"),
        sa.CheckConstraint("(estado IN ('GENERADA','BLOQUEADA') AND activa) OR (estado IN ('SIN_FALTANTES','CANCELADA') AND NOT activa)", name="ck_propuesta_compra_activa"),
        sa.CheckConstraint("modo_envio IN ('REQUIERE_APROBACION','AUTOMATICO')", name="ck_propuesta_compra_modo"))
    op.create_index("uq_propuesta_compra_fecha_activa", "propuesta_compra", ["fecha_objetivo"], unique=True,
                    sqlite_where=sa.text("activa = 1"), postgresql_where=sa.text("activa"))
    op.create_table("pedido_compra",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("propuesta_id", sa.Integer(), sa.ForeignKey("propuesta_compra.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("plan_id", sa.Integer(), sa.ForeignKey("plan_produccion.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("proveedor_id", sa.Integer(), sa.ForeignKey("proveedor.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("proveedor_json", json_tipo, nullable=False),
        sa.Column("estado", sa.String(24), nullable=False),
        sa.Column("modo_envio", sa.String(24), nullable=False),
        sa.Column("bloqueos_json", json_tipo, nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("plan_id", "proveedor_id", name="uq_pedido_plan_proveedor"),
        sa.CheckConstraint("estado IN ('BLOQUEADO','PENDIENTE_APROBACION','CANCELADO')", name="ck_pedido_compra_estado"))
    op.create_table("linea_pedido",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("pedido_id", sa.Integer(), sa.ForeignKey("pedido_compra.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("necesidad_ingrediente_id", sa.Integer(), sa.ForeignKey("necesidad_ingrediente.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("oferta_ingrediente_id", sa.Integer(), sa.ForeignKey("oferta_ingrediente.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("ingrediente_id", sa.Integer(), sa.ForeignKey("ingrediente.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("faltante_base", sa.Numeric(14, 3), nullable=False),
        sa.Column("cantidad_compra", sa.Numeric(20, 4), nullable=False),
        sa.Column("cantidad_base_pedida", sa.Numeric(30, 8), nullable=False),
        sa.Column("unidad_base", sa.String(16), nullable=False),
        sa.Column("unidad_compra", sa.String(30), nullable=False),
        sa.Column("oferta_json", json_tipo, nullable=False),
        sa.Column("ingrediente_json", json_tipo, nullable=False),
        sa.UniqueConstraint("necesidad_ingrediente_id", name="uq_linea_pedido_necesidad"),
        sa.CheckConstraint("faltante_base > 0 AND cantidad_compra > 0 AND cantidad_base_pedida >= faltante_base", name="ck_linea_pedido_cantidades"))


def downgrade():
    op.drop_table("linea_pedido")
    op.drop_table("pedido_compra")
    op.drop_index("uq_propuesta_compra_fecha_activa", table_name="propuesta_compra")
    op.drop_table("propuesta_compra")
