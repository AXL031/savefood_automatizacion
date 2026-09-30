"""Persistencia de artefactos, pronósticos y evaluación histórica de Kevin."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision = "0003_pronosticos"
down_revision = "0002_e01_ventas"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "artefacto_modelo",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("version_modelo", sa.String(80), nullable=False),
        sa.Column("ruta_local", sa.String(160), nullable=False),
        sa.Column("sha256", sa.String(64), nullable=False),
        sa.Column("huella_datos_entrenamiento", sa.String(64), nullable=False),
        sa.Column("fecha_corte_entrenamiento", sa.Date(), nullable=False),
        sa.Column("particion_json", JSONB(), nullable=False),
        sa.Column("estado", sa.String(16), nullable=False),
        sa.Column("metricas_json", JSONB()),
        sa.Column("entrenado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("version_modelo", name="uq_artefacto_modelo_version"),
        sa.CheckConstraint("estado = 'LISTO_DEMO'", name="ck_artefacto_modelo_estado"),
    )
    op.create_table(
        "corrida_pronostico",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ejecucion_id", sa.Integer(), sa.ForeignKey("ejecucion_automatizacion.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("tipo", sa.String(20), nullable=False),
        sa.Column("clave_ejecucion", sa.String(128), nullable=False),
        sa.Column("huella_datos_entrada", sa.String(64), nullable=False),
        sa.Column("fecha_objetivo", sa.Date(), nullable=False),
        sa.Column("modelo_id", sa.Integer(), sa.ForeignKey("artefacto_modelo.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("estado", sa.String(20), nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("finalizado_en", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("clave_ejecucion", name="uq_corrida_pronostico_clave"),
        sa.CheckConstraint("tipo IN ('BACKTEST', 'DEMO_PROGRAMADA')", name="ck_corrida_pronostico_tipo"),
        sa.CheckConstraint("estado IN ('COMPLETADA', 'SIN_COBERTURA')", name="ck_corrida_pronostico_estado"),
    )
    op.create_index("ix_corrida_pronostico_fecha", "corrida_pronostico", ["fecha_objetivo"])
    op.create_table(
        "pronostico",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("corrida_id", sa.Integer(), sa.ForeignKey("corrida_pronostico.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("producto_id", sa.Integer(), sa.ForeignKey("producto.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("cantidad_pronosticada", sa.Integer()),
        sa.Column("estado", sa.String(32), nullable=False),
        sa.UniqueConstraint("corrida_id", "producto_id", name="uq_pronostico_corrida_producto"),
        sa.CheckConstraint("estado IN ('DISPONIBLE', 'HISTORIAL_INSUFICIENTE', 'PRODUCTO_NO_CUBIERTO')", name="ck_pronostico_estado"),
        sa.CheckConstraint("(estado = 'DISPONIBLE' AND cantidad_pronosticada >= 0) OR (estado != 'DISPONIBLE' AND cantidad_pronosticada IS NULL)", name="ck_pronostico_cantidad_estado"),
    )
    op.create_table(
        "evaluacion_pronostico",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ejecucion_id", sa.Integer(), sa.ForeignKey("ejecucion_automatizacion.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("corrida_id", sa.Integer(), sa.ForeignKey("corrida_pronostico.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("pronostico_id", sa.Integer(), sa.ForeignKey("pronostico.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("revision_venta_id", sa.Integer(), sa.ForeignKey("revision_venta.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("producto_id", sa.Integer(), sa.ForeignKey("producto.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("cantidad_pronosticada", sa.Integer(), nullable=False),
        sa.Column("unidades_reales", sa.Integer(), nullable=False),
        sa.Column("error_absoluto", sa.Integer(), nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("corrida_id", "producto_id", "revision_venta_id", name="uq_evaluacion_pronostico_revision"),
        sa.CheckConstraint("cantidad_pronosticada >= 0 AND unidades_reales >= 0 AND error_absoluto >= 0", name="ck_evaluacion_pronostico_cantidades"),
    )


def downgrade():
    op.drop_table("evaluacion_pronostico")
    op.drop_table("pronostico")
    op.drop_index("ix_corrida_pronostico_fecha", table_name="corrida_pronostico")
    op.drop_table("corrida_pronostico")
    op.drop_table("artefacto_modelo")
