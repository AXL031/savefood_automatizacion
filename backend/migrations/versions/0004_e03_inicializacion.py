"""Estado durable de la primera inicialización (E03).

Sucede a `0003_pronosticos` para no reescribir migraciones que el equipo ya
aplicó. Crea la fila única `configuracion_inicial` en estado `PENDIENTE`, que es
la frontera que Kevin y Axel consultan antes de entrenar o de despachar.
"""

from alembic import op
import sqlalchemy as sa

revision = "0004_e03_inicializacion"
down_revision = "0003_pronosticos"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "configuracion_inicial",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=False),
        sa.Column("estado", sa.String(20), nullable=False, server_default="PENDIENTE"),
        sa.Column("huella_ventas", sa.String(64), nullable=True),
        sa.Column("huella_catalogo", sa.String(64), nullable=True),
        sa.Column("huella_solicitud", sa.String(64), nullable=True),
        sa.Column("fecha_objetivo_demo", sa.Date(), nullable=True),
        sa.Column("fecha_referencia_stock", sa.Date(), nullable=True),
        sa.Column("iniciada_en", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completada_en", sa.DateTime(timezone=True), nullable=True),
        sa.Column("mensaje_error", sa.Text(), nullable=True),
        sa.Column(
            "actualizado_en",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint("id = 1", name="ck_configuracion_inicial_fila_unica"),
        sa.CheckConstraint(
            "estado in ('PENDIENTE', 'DATOS_CARGADOS', 'ENTRENANDO', 'MODELO_LISTO', 'FALLIDA')",
            name="ck_configuracion_inicial_estado",
        ),
        sa.CheckConstraint(
            "fecha_referencia_stock is null or fecha_objetivo_demo is null "
            "or fecha_referencia_stock < fecha_objetivo_demo",
            name="ck_configuracion_inicial_fechas",
        ),
    )
    # La fila existe desde el inicio: así toda lectura del estado encuentra
    # PENDIENTE en lugar de tener que distinguir «sin fila» de «sin cargar».
    op.execute("insert into configuracion_inicial (id, estado) values (1, 'PENDIENTE')")


def downgrade():
    op.drop_table("configuracion_inicial")
