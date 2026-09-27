"""Reserva programaciones y ejecuciones del motor de demostración."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001b_automatizaciones"
down_revision = "0001a_configuracion"
branch_labels = None
depends_on = None

json_persistido = sa.JSON().with_variant(postgresql.JSONB, "postgresql")


def upgrade():
    op.create_table(
        "programacion_demo",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tipo", sa.String(32), nullable=False),
        sa.Column("ejecutar_desde_utc", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fecha_hora_simulada_local", sa.DateTime(timezone=False), nullable=False),
        sa.Column("parametros_json", json_persistido, nullable=False),
        sa.Column("clave_idempotencia", sa.String(128), nullable=False),
        sa.Column("huella_entrada", sa.String(64), nullable=False),
        sa.Column("estado", sa.String(16), nullable=False, server_default="PROGRAMADA"),
        sa.Column("despachada_en", sa.DateTime(timezone=True)),
        sa.Column("lease_hasta", sa.DateTime(timezone=True)),
        sa.Column("creado_por", sa.Integer(), sa.ForeignKey("usuario.id", ondelete="RESTRICT")),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("clave_idempotencia", name="uq_programacion_demo_clave"),
        sa.CheckConstraint("tipo IN ('GENERAR_PROPUESTA', 'EVALUAR_PROMOCION')", name="ck_programacion_demo_tipo"),
        sa.CheckConstraint("estado IN ('PROGRAMADA', 'DESPACHADA', 'CANCELADA')", name="ck_programacion_demo_estado"),
    )
    op.create_index("ix_programacion_demo_vencimientos", "programacion_demo", ["estado", "ejecutar_desde_utc"])
    op.create_table(
        "ejecucion_automatizacion",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("programacion_id", sa.Integer(), sa.ForeignKey("programacion_demo.id", ondelete="RESTRICT")),
        sa.Column("tipo", sa.String(32), nullable=False),
        sa.Column("clave_idempotencia", sa.String(128), nullable=False),
        sa.Column("huella_entrada", sa.String(64), nullable=False),
        sa.Column("datos_entrada_json", json_persistido, nullable=False),
        sa.Column("estado", sa.String(16), nullable=False, server_default="PENDIENTE"),
        sa.Column("inicio_en", sa.DateTime(timezone=True)),
        sa.Column("fin_en", sa.DateTime(timezone=True)),
        sa.Column("proximo_intento_en", sa.DateTime(timezone=True)),
        sa.Column("datos_salida_json", json_persistido),
        sa.Column("mensaje_error", sa.Text()),
        sa.UniqueConstraint("clave_idempotencia", name="uq_ejecucion_automatizacion_clave"),
        sa.UniqueConstraint("programacion_id", name="uq_ejecucion_automatizacion_programacion"),
        sa.CheckConstraint(
            "tipo IN ('PREPARAR_MODELO', 'EVALUAR_MODELO', 'GENERAR_PROPUESTA', 'EVALUAR_PRONOSTICO', 'EVALUAR_PROMOCION')",
            name="ck_ejecucion_automatizacion_tipo",
        ),
        sa.CheckConstraint(
            "estado IN ('PENDIENTE', 'EN_EJECUCION', 'REINTENTANDO', 'COMPLETADA', 'FALLIDA')",
            name="ck_ejecucion_automatizacion_estado",
        ),
    )
    op.create_index("ix_ejecucion_automatizacion_estado", "ejecucion_automatizacion", ["estado"])
    op.create_table(
        "intento_automatizacion",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ejecucion_id", sa.Integer(), sa.ForeignKey("ejecucion_automatizacion.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("numero_intento", sa.Integer(), nullable=False),
        sa.Column("inicio_en", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fin_en", sa.DateTime(timezone=True)),
        sa.Column("estado", sa.String(16), nullable=False),
        sa.Column("mensaje_error", sa.Text()),
        sa.UniqueConstraint("ejecucion_id", "numero_intento", name="uq_intento_automatizacion_numero"),
        sa.CheckConstraint("numero_intento BETWEEN 1 AND 3", name="ck_intento_automatizacion_numero"),
        sa.CheckConstraint("estado IN ('EN_EJECUCION', 'COMPLETADA', 'FALLIDA')", name="ck_intento_automatizacion_estado"),
    )


def downgrade():
    op.drop_table("intento_automatizacion")
    op.drop_index("ix_ejecucion_automatizacion_estado", table_name="ejecucion_automatizacion")
    op.drop_table("ejecucion_automatizacion")
    op.drop_index("ix_programacion_demo_vencimientos", table_name="programacion_demo")
    op.drop_table("programacion_demo")
