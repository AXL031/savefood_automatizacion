"""Promociones sugeridas, configuración reutilizable y controles de programación."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0015_flujo_promociones"
down_revision = "0014_l04_recuperacion"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("regla_promocion_demo",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("parametros", sa.JSON(), nullable=False),
        sa.Column("creado_por", sa.Integer(), sa.ForeignKey("usuario.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("version", name="uq_regla_promocion_version"))
    op.create_table("evaluacion_promocion",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("regla_id", sa.Integer(), sa.ForeignKey("regla_promocion_demo.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("movimiento_id", sa.Integer(), sa.ForeignKey("movimiento_inventario.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("ejecucion_id", sa.Integer(), sa.ForeignKey("ejecucion_automatizacion.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("proponer", sa.Boolean(), nullable=False),
        sa.Column("motivo", sa.String(300), nullable=False),
        sa.Column("descuento_pct", sa.Integer()),
        sa.Column("lectura", sa.JSON(), nullable=False),
        sa.Column("fecha_hora_simulada", sa.DateTime(), nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("movimiento_id", name="uq_evaluacion_promocion_movimiento"),
        sa.UniqueConstraint("ejecucion_id", name="uq_evaluacion_promocion_ejecucion"),
        sa.CheckConstraint("descuento_pct IS NULL OR descuento_pct BETWEEN 1 AND 100", name="ck_evaluacion_promocion_descuento"))
    op.create_table("configuracion_flujo",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("parametros", sa.JSON().with_variant(postgresql.JSONB(), "postgresql"), nullable=False),
        sa.Column("actualizado_por", sa.Integer(), sa.ForeignKey("usuario.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("actualizado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("id = 1", name="ck_configuracion_flujo_unica"))
    with op.batch_alter_table("programacion_demo") as tabla:
        tabla.add_column(sa.Column("cambios_json", sa.JSON().with_variant(postgresql.JSONB(), "postgresql"), nullable=False, server_default="[]"))
        tabla.drop_constraint("ck_programacion_demo_estado", type_="check")
        tabla.create_check_constraint("ck_programacion_demo_estado", "estado IN ('PROGRAMADA','DESPACHADA','PAUSADA','CANCELADA')")
    with op.batch_alter_table("ejecucion_automatizacion") as tabla:
        tabla.drop_constraint("ck_ejecucion_automatizacion_estado", type_="check")
        tabla.create_check_constraint("ck_ejecucion_automatizacion_estado", "estado IN ('PENDIENTE','EN_EJECUCION','REINTENTANDO','COMPLETADA','FALLIDA','CANCELADA')")


def downgrade():
    conexion = op.get_bind()
    if (conexion.execute(sa.text("SELECT count(*) FROM evaluacion_promocion")).scalar()
        or conexion.execute(sa.text("SELECT count(*) FROM regla_promocion_demo")).scalar()
        or conexion.execute(sa.text("SELECT count(*) FROM configuracion_flujo")).scalar()
        or conexion.execute(sa.text("SELECT count(*) FROM programacion_demo WHERE estado IN ('PAUSADA','CANCELADA')")).scalar()):
        raise RuntimeError("Conservar reglas, evaluaciones y controles mediante una migración correctiva.")
    with op.batch_alter_table("ejecucion_automatizacion") as tabla:
        tabla.drop_constraint("ck_ejecucion_automatizacion_estado", type_="check")
        tabla.create_check_constraint("ck_ejecucion_automatizacion_estado", "estado IN ('PENDIENTE','EN_EJECUCION','REINTENTANDO','COMPLETADA','FALLIDA')")
    with op.batch_alter_table("programacion_demo") as tabla:
        tabla.drop_constraint("ck_programacion_demo_estado", type_="check")
        tabla.create_check_constraint("ck_programacion_demo_estado", "estado IN ('PROGRAMADA','DESPACHADA','CANCELADA')")
        tabla.drop_column("cambios_json")
    op.drop_table("configuracion_flujo")
    op.drop_table("evaluacion_promocion")
    op.drop_table("regla_promocion_demo")
