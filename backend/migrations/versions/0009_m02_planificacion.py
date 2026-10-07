"""Planes y elementos reproducibles M02; no altera las revisiones aplicadas."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0009_m02_planificacion"
down_revision = "0008_e03_preparacion_ml"
branch_labels = None
depends_on = None


def upgrade():
    json_tipo = sa.JSON().with_variant(postgresql.JSONB(), "postgresql")
    op.create_table("plan_produccion",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("corrida_id", sa.Integer(), sa.ForeignKey("corrida_pronostico.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("ejecucion_id", sa.Integer(), sa.ForeignKey("ejecucion_automatizacion.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("clave_ejecucion", sa.String(128), nullable=False),
        sa.Column("huella_stock_recetas", sa.String(64), nullable=False),
        sa.Column("fecha_objetivo", sa.Date(), nullable=False),
        sa.Column("stock_leido_en", sa.DateTime(timezone=True), nullable=False),
        sa.Column("estado", sa.String(16), nullable=False),
        sa.Column("version_calculo", sa.String(16), nullable=False),
        sa.Column("origen_pronostico_json", json_tipo, nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("clave_ejecucion", name="uq_plan_produccion_clave"),
        sa.CheckConstraint("estado = 'PROPUESTO'", name="ck_plan_produccion_estado"))
    op.create_index("ix_plan_produccion_corrida", "plan_produccion", ["corrida_id"])
    op.create_table("elemento_plan",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("plan_id", sa.Integer(), sa.ForeignKey("plan_produccion.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("producto_id", sa.Integer(), sa.ForeignKey("producto.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("pronostico_id", sa.Integer(), sa.ForeignKey("pronostico.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("receta_id", sa.Integer(), sa.ForeignKey("receta.id", ondelete="RESTRICT")),
        sa.Column("cantidad_pronosticada", sa.Integer()),
        sa.Column("stock_disponible", sa.Integer()),
        sa.Column("cantidad_producir", sa.Integer()),
        sa.Column("estado", sa.String(32), nullable=False),
        sa.Column("receta_json", json_tipo),
        sa.Column("stock_json", json_tipo, nullable=False),
        sa.Column("avisos_json", json_tipo, nullable=False),
        sa.UniqueConstraint("plan_id", "producto_id", name="uq_elemento_plan_producto"),
        sa.CheckConstraint("estado IN ('CALCULADO', 'HISTORIAL_INSUFICIENTE', 'PRODUCTO_NO_CUBIERTO', 'SIN_RECETA', 'STOCK_DESCONOCIDO')", name="ck_elemento_plan_estado"),
        sa.CheckConstraint("cantidad_pronosticada IS NULL OR cantidad_pronosticada >= 0", name="ck_elemento_plan_pronostico"),
        sa.CheckConstraint("stock_disponible IS NULL OR stock_disponible >= 0", name="ck_elemento_plan_stock"),
        sa.CheckConstraint("(estado = 'CALCULADO' AND cantidad_producir IS NOT NULL AND cantidad_producir >= 0 AND cantidad_pronosticada IS NOT NULL AND stock_disponible IS NOT NULL AND receta_id IS NOT NULL) OR (estado != 'CALCULADO' AND cantidad_producir IS NULL)", name="ck_elemento_plan_calculo"),
        sa.CheckConstraint("estado != 'CALCULADO' OR cantidad_producir = CASE WHEN cantidad_pronosticada > stock_disponible THEN cantidad_pronosticada - stock_disponible ELSE 0 END", name="ck_elemento_plan_formula"))


def downgrade():
    op.drop_table("elemento_plan")
    op.drop_index("ix_plan_produccion_corrida", table_name="plan_produccion")
    op.drop_table("plan_produccion")
