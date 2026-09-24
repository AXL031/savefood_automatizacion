"""Negocio local y usuarios iniciales."""
from alembic import op
import sqlalchemy as sa

revision = "0001_nucleo"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "negocio",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nombre", sa.String(160), nullable=False),
        sa.Column("zona_horaria", sa.String(80), nullable=False),
        sa.Column("moneda", sa.String(3), nullable=False),
        sa.Column("hora_apertura", sa.Time(), nullable=True),
        sa.Column("hora_cierre", sa.Time(), nullable=True),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False),
        sa.Column("actualizado_en", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("id = 1", name="ck_negocio_unico"),
        sa.CheckConstraint("char_length(moneda) = 3", name="ck_negocio_moneda"),
    )
    op.create_table(
        "usuario",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("correo", sa.String(254), nullable=False),
        sa.Column("hash_contrasena", sa.String(512), nullable=False),
        sa.Column("nombre", sa.String(160), nullable=False),
        sa.Column("rol", sa.String(20), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False),
        sa.Column("actualizado_en", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("rol IN ('ADMINISTRADOR', 'OPERADOR')", name="ck_usuario_rol"),
    )
    op.create_index("uq_usuario_correo_normalizado", "usuario", [sa.text("lower(correo)")], unique=True)
    op.execute(
        "INSERT INTO negocio (id, nombre, zona_horaria, moneda, creado_en, actualizado_en) "
        "VALUES (1, 'Comercio de demostración', 'America/Lima', 'PEN', now(), now())"
    )


def downgrade():
    op.drop_index("uq_usuario_correo_normalizado", table_name="usuario")
    op.drop_table("usuario")
    op.drop_table("negocio")
