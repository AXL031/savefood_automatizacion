"""Recepciones explícitas auditadas y corrección enlazada de borradores bloqueados."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0018_recepcion_compras"
down_revision = "0017_pruebas_proveedor"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("propuesta_compra") as t:
        t.add_column(sa.Column("reemplazo_id", sa.Integer(), nullable=True))
        t.create_foreign_key("fk_propuesta_reemplazo", "propuesta_compra", ["reemplazo_id"], ["id"], ondelete="RESTRICT")
    with op.batch_alter_table("lote_ingrediente") as t:
        t.add_column(sa.Column("fecha_ingreso", sa.Date(), nullable=True))
    with op.batch_alter_table("movimiento_inventario") as t:
        t.drop_constraint("ck_movimiento_inventario_tipo", type_="check")
        t.create_check_constraint("ck_movimiento_inventario_tipo", "tipo in ('APERTURA', 'AJUSTE', 'RECEPCION')")
        t.create_check_constraint("ck_movimiento_recepcion_ingrediente", "tipo <> 'RECEPCION' OR lote_producto_id IS NULL")
    op.create_table("recepcion_pedido",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("pedido_id", sa.Integer(), sa.ForeignKey("pedido_compra.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("clave_idempotencia", sa.String(80), unique=True, nullable=False),
        sa.Column("usuario_id", sa.Integer(), sa.ForeignKey("usuario.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("nombre_usuario", sa.String(150), nullable=False),
        sa.Column("fecha_recepcion", sa.Date(), nullable=False),
        sa.Column("motivo", sa.String(300), nullable=False),
        sa.Column("solicitud_json", sa.JSON().with_variant(postgresql.JSONB(), "postgresql"), nullable=False),
        sa.Column("creado_en", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False))
    op.create_index("ix_recepcion_pedido_pedido_id", "recepcion_pedido", ["pedido_id"])
    op.create_table("linea_recepcion_pedido",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("recepcion_id", sa.Integer(), sa.ForeignKey("recepcion_pedido.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("linea_pedido_id", sa.Integer(), sa.ForeignKey("linea_pedido.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("cantidad_compra", sa.Numeric(20, 4), nullable=False),
        sa.Column("cantidad_base", sa.Numeric(14, 3), nullable=False),
        sa.Column("lote_id", sa.Integer(), sa.ForeignKey("lote_ingrediente.id", ondelete="RESTRICT"), unique=True, nullable=False),
        sa.Column("movimiento_id", sa.Integer(), sa.ForeignKey("movimiento_inventario.id", ondelete="RESTRICT"), unique=True, nullable=False),
        sa.Column("codigo_lote", sa.String(80), nullable=False),
        sa.Column("fecha_caducidad", sa.Date(), nullable=True),
        sa.UniqueConstraint("recepcion_id", "linea_pedido_id", name="uq_recepcion_linea"),
        sa.CheckConstraint("cantidad_compra > 0 AND cantidad_base > 0", name="ck_recepcion_cantidades"))
    op.create_index("ix_linea_recepcion_pedido_recepcion_id", "linea_recepcion_pedido", ["recepcion_id"])
    op.create_index("ix_linea_recepcion_pedido_linea_pedido_id", "linea_recepcion_pedido", ["linea_pedido_id"])


def downgrade():
    c = op.get_bind()
    if (c.execute(sa.text("SELECT count(*) FROM recepcion_pedido")).scalar_one()
            or c.execute(sa.text("SELECT count(*) FROM movimiento_inventario WHERE tipo='RECEPCION'")).scalar_one()
            or c.execute(sa.text("SELECT count(*) FROM propuesta_compra WHERE reemplazo_id IS NOT NULL")).scalar_one()
            or c.execute(sa.text("SELECT count(*) FROM lote_ingrediente WHERE fecha_ingreso IS NOT NULL")).scalar_one()):
        raise RuntimeError("Hay recepciones o correcciones conservadas; no se elimina su evidencia.")
    op.drop_table("linea_recepcion_pedido")
    op.drop_table("recepcion_pedido")
    with op.batch_alter_table("movimiento_inventario") as t:
        t.drop_constraint("ck_movimiento_recepcion_ingrediente", type_="check")
        t.drop_constraint("ck_movimiento_inventario_tipo", type_="check")
        t.create_check_constraint("ck_movimiento_inventario_tipo", "tipo in ('APERTURA', 'AJUSTE')")
    with op.batch_alter_table("lote_ingrediente") as t:
        t.drop_column("fecha_ingreso")
    with op.batch_alter_table("propuesta_compra") as t:
        t.drop_constraint("fk_propuesta_reemplazo", type_="foreignkey")
        t.drop_column("reemplazo_id")
