"""Enlace durable entre primera carga y preparación ML; conserva datos existentes."""

from alembic import op
import sqlalchemy as sa

revision = "0008_e03_modelo"
down_revision = "0007_l01_proveedores"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("configuracion_inicial") as tabla:
        tabla.add_column(sa.Column("preparacion_ejecucion_id", sa.Integer(), nullable=True))
        tabla.create_foreign_key("fk_inicializacion_preparacion", "ejecucion_automatizacion",
                                 ["preparacion_ejecucion_id"], ["id"], ondelete="RESTRICT")


def downgrade():
    with op.batch_alter_table("configuracion_inicial") as tabla:
        tabla.drop_constraint("fk_inicializacion_preparacion", type_="foreignkey")
        tabla.drop_column("preparacion_ejecucion_id")
