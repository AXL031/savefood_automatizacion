"""Lease de publicación y recuperación para tareas programadas y eventos."""

from alembic import op
import sqlalchemy as sa

revision = "0001c_motor"
down_revision = "0001b_automatizaciones"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("ejecucion_automatizacion", sa.Column("despachada_en", sa.DateTime(timezone=True)))
    op.add_column("ejecucion_automatizacion", sa.Column("lease_hasta", sa.DateTime(timezone=True)))
    op.add_column("ejecucion_automatizacion", sa.Column("token_despacho", sa.String(36)))
    op.create_index("ix_ejecucion_automatizacion_lease", "ejecucion_automatizacion", ["estado", "lease_hasta"])


def downgrade():
    op.drop_index("ix_ejecucion_automatizacion_lease", table_name="ejecucion_automatizacion")
    op.drop_column("ejecucion_automatizacion", "token_despacho")
    op.drop_column("ejecucion_automatizacion", "lease_hasta")
    op.drop_column("ejecucion_automatizacion", "despachada_en")
