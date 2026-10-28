"""Pruebas repetibles explícitas sin alterar la protección de compras normales."""
from alembic import op
import sqlalchemy as sa

revision = "0020_pruebas_repetibles"
down_revision = "0019_tienda_clientes"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("propuesta_compra", sa.Column("prueba_repetible", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.drop_index("uq_propuesta_compra_fecha_activa", table_name="propuesta_compra")
    op.create_index("uq_propuesta_compra_fecha_activa", "propuesta_compra", ["fecha_objetivo"], unique=True,
                    postgresql_where=sa.text("activa AND NOT prueba_repetible"),
                    sqlite_where=sa.text("activa = 1 AND prueba_repetible = 0"))


def downgrade():
    if op.get_bind().execute(sa.text("SELECT 1 FROM propuesta_compra WHERE prueba_repetible = true LIMIT 1")).first():
        raise RuntimeError("Hay pruebas repetibles conservadas. No se elimina su marca ni se reescribe su historial.")
    op.drop_index("uq_propuesta_compra_fecha_activa", table_name="propuesta_compra")
    op.create_index("uq_propuesta_compra_fecha_activa", "propuesta_compra", ["fecha_objetivo"], unique=True,
                    postgresql_where=sa.text("activa"), sqlite_where=sa.text("activa = 1"))
    op.drop_column("propuesta_compra", "prueba_repetible")
