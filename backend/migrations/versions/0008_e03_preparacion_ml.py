"""Vincula primera carga, preparación y modelo sin reescribir revisiones aplicadas."""
from alembic import op
import sqlalchemy as sa

revision = "0008_e03_preparacion_ml"
down_revision = "0007_l01_proveedores"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("configuracion_inicial") as tabla:
        tabla.add_column(sa.Column("preparacion_ejecucion_id", sa.Integer(), nullable=True))
        tabla.add_column(sa.Column("modelo_id", sa.Integer(), nullable=True))
        tabla.add_column(sa.Column("preparacion_numero", sa.Integer(), nullable=False, server_default="0"))
        tabla.create_foreign_key("fk_inicializacion_preparacion", "ejecucion_automatizacion", ["preparacion_ejecucion_id"], ["id"], ondelete="RESTRICT")
        tabla.create_foreign_key("fk_inicializacion_modelo", "artefacto_modelo", ["modelo_id"], ["id"], ondelete="RESTRICT")
        tabla.create_check_constraint("ck_inicializacion_preparacion_numero", "preparacion_numero >= 0")


def downgrade():
    with op.batch_alter_table("configuracion_inicial") as tabla:
        tabla.drop_constraint("ck_inicializacion_preparacion_numero", type_="check")
        tabla.drop_constraint("fk_inicializacion_modelo", type_="foreignkey")
        tabla.drop_constraint("fk_inicializacion_preparacion", type_="foreignkey")
        tabla.drop_column("preparacion_numero")
        tabla.drop_column("modelo_id")
        tabla.drop_column("preparacion_ejecucion_id")
