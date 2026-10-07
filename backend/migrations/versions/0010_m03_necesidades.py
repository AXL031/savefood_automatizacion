"""Necesidades conservadas; planes anteriores quedan pendientes de completar."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0010_m03_necesidades"
down_revision = "0009_m02_planificacion"
branch_labels = None
depends_on = None


def upgrade():
    json_tipo = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")
    op.add_column("plan_produccion", sa.Column("necesidades_estado", sa.String(24), nullable=False, server_default="PENDIENTE_M03"))
    op.add_column("plan_produccion", sa.Column("necesidades_meta_json", json_tipo))
    op.create_table("necesidad_ingrediente",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("plan_id", sa.Integer(), sa.ForeignKey("plan_produccion.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("ingrediente_id", sa.Integer(), sa.ForeignKey("ingrediente.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("unidad_base", sa.String(16), nullable=False),
        sa.Column("cantidad_necesaria", sa.Numeric(14, 3), nullable=False),
        sa.Column("stock_disponible", sa.Numeric(14, 3)),
        sa.Column("faltante", sa.Numeric(14, 3)),
        sa.Column("estado", sa.String(24), nullable=False),
        sa.Column("aportes_json", json_tipo, nullable=False),
        sa.Column("stock_json", json_tipo, nullable=False),
        sa.UniqueConstraint("plan_id", "ingrediente_id", name="uq_necesidad_plan_ingrediente"),
        sa.CheckConstraint("cantidad_necesaria >= 0", name="ck_necesidad_cantidad"),
        sa.CheckConstraint("(estado = 'DISPONIBLE' AND stock_disponible IS NOT NULL AND stock_disponible >= 0 AND faltante IS NOT NULL AND faltante >= 0) OR (estado = 'STOCK_DESCONOCIDO' AND stock_disponible IS NULL AND faltante IS NULL)", name="ck_necesidad_estado"),
        sa.CheckConstraint("faltante IS NULL OR faltante = CASE WHEN cantidad_necesaria > stock_disponible THEN cantidad_necesaria - stock_disponible ELSE 0 END", name="ck_necesidad_formula"))


def downgrade():
    op.drop_table("necesidad_ingrediente")
    op.drop_column("plan_produccion", "necesidades_meta_json")
    op.drop_column("plan_produccion", "necesidades_estado")
