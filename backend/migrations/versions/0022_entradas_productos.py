"""Entradas administrativas de varios lotes de producto, con ingreso fechado."""
from alembic import op
import sqlalchemy as sa

revision = "0022_entradas_productos"
down_revision = "0021_ventas_presenciales"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("lote_producto", sa.Column("fecha_ingreso", sa.Date(), nullable=True))
    with op.batch_alter_table("movimiento_inventario") as t:
        t.drop_constraint("ck_movimiento_inventario_tipo", type_="check")
        t.create_check_constraint("ck_movimiento_inventario_tipo", "tipo in ('APERTURA', 'AJUSTE', 'RECEPCION', 'VENTA', 'ANULA_VENTA', 'ENTRADA')")
        t.create_check_constraint("ck_movimiento_entrada_producto", "tipo <> 'ENTRADA' OR (lote_producto_id IS NOT NULL AND delta > 0)")
    op.create_table("entrada_productos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuario.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("nombre_usuario", sa.String(150), nullable=False),
        sa.Column("clave", sa.String(80), nullable=False),
        sa.Column("huella", sa.String(64), nullable=False),
        sa.Column("fecha_entrada", sa.Date(), nullable=False),
        sa.Column("motivo", sa.String(300), nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("usuario_id", "clave", name="uq_entrada_productos_clave"),
        sa.CheckConstraint("length(trim(motivo)) >= 3", name="ck_entrada_productos_motivo"))
    op.create_index("ix_entrada_productos_fecha", "entrada_productos", ["fecha_entrada", "id"])
    op.create_table("linea_entrada_productos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("entrada_id", sa.Integer(), sa.ForeignKey("entrada_productos.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("producto_id", sa.Integer(), sa.ForeignKey("producto.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("lote_id", sa.Integer(), sa.ForeignKey("lote_producto.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("movimiento_id", sa.Integer(), sa.ForeignKey("movimiento_inventario.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("codigo_producto", sa.String(160), nullable=False),
        sa.Column("nombre_producto", sa.String(160), nullable=False),
        sa.Column("codigo_lote", sa.String(80), nullable=False),
        sa.Column("cantidad", sa.Integer(), nullable=False),
        sa.Column("fecha_elaboracion", sa.Date(), nullable=False),
        sa.Column("fecha_caducidad", sa.Date(), nullable=False),
        sa.Column("fecha_limite_venta", sa.Date(), nullable=False),
        sa.UniqueConstraint("lote_id"), sa.UniqueConstraint("movimiento_id"),
        sa.CheckConstraint("cantidad BETWEEN 1 AND 1000000", name="ck_linea_entrada_cantidad"),
        sa.CheckConstraint("fecha_elaboracion <= fecha_limite_venta AND fecha_limite_venta <= fecha_caducidad", name="ck_linea_entrada_fechas"))
    op.create_index("ix_linea_entrada_productos_entrada_id", "linea_entrada_productos", ["entrada_id"])
    op.create_index("ix_linea_entrada_productos_producto_id", "linea_entrada_productos", ["producto_id"])


def downgrade():
    for q in ("SELECT count(*) FROM entrada_productos", "SELECT count(*) FROM movimiento_inventario WHERE tipo='ENTRADA'",
              "SELECT count(*) FROM lote_producto WHERE fecha_ingreso IS NOT NULL"):
        if op.get_bind().execute(sa.text(q)).scalar_one():
            raise RuntimeError("Hay entradas de productos conservadas; no se elimina su evidencia.")
    op.drop_table("linea_entrada_productos")
    op.drop_table("entrada_productos")
    with op.batch_alter_table("movimiento_inventario") as t:
        t.drop_constraint("ck_movimiento_entrada_producto", type_="check")
        t.drop_constraint("ck_movimiento_inventario_tipo", type_="check")
        t.create_check_constraint("ck_movimiento_inventario_tipo", "tipo in ('APERTURA', 'AJUSTE', 'RECEPCION', 'VENTA', 'ANULA_VENTA')")
    op.drop_column("lote_producto", "fecha_ingreso")
