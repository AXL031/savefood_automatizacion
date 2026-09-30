"""Primer corte incremental de 0002: catálogo y ventas para la frontera E01/K02."""

from alembic import op
import sqlalchemy as sa

revision = "0002_e01_ventas"
down_revision = "0001c_motor"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "producto",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("codigo", sa.String(160), nullable=False),
        sa.Column("nombre", sa.String(160), nullable=False),
        sa.Column("demostrar", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("codigo", name="uq_producto_codigo"),
        sa.CheckConstraint("length(trim(codigo)) > 0", name="ck_producto_codigo"),
        sa.CheckConstraint("length(trim(nombre)) > 0", name="ck_producto_nombre"),
    )
    op.create_table(
        "sku_producto",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("producto_id", sa.Integer(), sa.ForeignKey("producto.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("origen", sa.String(40), nullable=False),
        sa.Column("sku_externo", sa.String(160), nullable=False),
        sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.UniqueConstraint("origen", "sku_externo", name="uq_sku_producto_origen_sku"),
        sa.CheckConstraint("length(trim(origen)) > 0", name="ck_sku_producto_origen"),
        sa.CheckConstraint("length(trim(sku_externo)) > 0", name="ck_sku_producto_sku"),
    )
    op.create_table(
        "importacion_venta",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("origen", sa.String(40), nullable=False),
        sa.Column("clave_importacion", sa.String(128), nullable=False),
        sa.Column("huella_contenido", sa.String(64), nullable=False),
        sa.Column("filas_aceptadas", sa.Integer(), nullable=False),
        sa.Column("estado", sa.String(16), nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("origen", "clave_importacion", name="uq_importacion_venta_clave"),
        sa.CheckConstraint("filas_aceptadas >= 0", name="ck_importacion_venta_filas"),
        sa.CheckConstraint("estado = 'COMPLETADA'", name="ck_importacion_venta_estado"),
    )
    op.create_table(
        "venta_diaria",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("producto_id", sa.Integer(), sa.ForeignKey("producto.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("fecha_local", sa.Date(), nullable=False),
        sa.Column("unidades_vendidas", sa.Integer(), nullable=False),
        sa.Column("importacion_id", sa.Integer(), sa.ForeignKey("importacion_venta.id", ondelete="RESTRICT")),
        sa.Column("revision_actual", sa.Integer(), nullable=False),
        sa.Column("actualizado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("producto_id", "fecha_local", name="uq_venta_diaria_producto_fecha"),
        sa.CheckConstraint("unidades_vendidas >= 0", name="ck_venta_diaria_unidades"),
        sa.CheckConstraint("revision_actual >= 1", name="ck_venta_diaria_revision"),
    )
    op.create_index("ix_venta_diaria_fecha", "venta_diaria", ["fecha_local"])
    op.create_table(
        "revision_venta",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("venta_id", sa.Integer(), sa.ForeignKey("venta_diaria.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("numero_revision", sa.Integer(), nullable=False),
        sa.Column("unidades_vendidas", sa.Integer(), nullable=False),
        sa.Column("origen_cambio", sa.String(32), nullable=False),
        sa.Column("motivo", sa.String(255), nullable=False),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuario.id", ondelete="RESTRICT")),
        sa.Column("importacion_id", sa.Integer(), sa.ForeignKey("importacion_venta.id", ondelete="RESTRICT")),
        sa.Column("creado_en", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("venta_id", "numero_revision", name="uq_revision_venta_numero"),
        sa.CheckConstraint("numero_revision >= 1", name="ck_revision_venta_numero"),
        sa.CheckConstraint("unidades_vendidas >= 0", name="ck_revision_venta_unidades"),
    )


def downgrade():
    op.drop_table("revision_venta")
    op.drop_index("ix_venta_diaria_fecha", table_name="venta_diaria")
    op.drop_table("venta_diaria")
    op.drop_table("importacion_venta")
    op.drop_table("sku_producto")
    op.drop_table("producto")
