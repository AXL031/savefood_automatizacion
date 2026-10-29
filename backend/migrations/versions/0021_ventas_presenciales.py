"""Caja presencial, precios versionados y salidas de producto terminado."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0021_ventas_presenciales"
down_revision = "0020_pruebas_repetibles"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("movimiento_inventario") as t:
        t.drop_constraint("ck_movimiento_inventario_tipo", type_="check")
        t.create_check_constraint("ck_movimiento_inventario_tipo", "tipo in ('APERTURA', 'AJUSTE', 'RECEPCION', 'VENTA', 'ANULA_VENTA')")
        t.create_check_constraint("ck_movimiento_venta_producto", "tipo NOT IN ('VENTA','ANULA_VENTA') OR (lote_producto_id IS NOT NULL AND ((tipo='VENTA' AND delta < 0) OR (tipo='ANULA_VENTA' AND delta > 0)))")
    op.create_table('precio_producto_venta',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('producto_id', sa.Integer(), sa.ForeignKey('producto.id', ondelete="RESTRICT"), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('precio', sa.Numeric(8, 2), nullable=False),
        sa.Column('usuario_id', sa.Integer(), sa.ForeignKey('usuario.id', ondelete="RESTRICT"), nullable=False),
        sa.Column('clave', sa.String(80), nullable=False),
        sa.Column('huella', sa.String(64), nullable=False),
        sa.Column('creado_en', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint('version > 0 AND precio > 0 AND precio <= 999999.99', name='ck_precio_venta_valores'),
        sa.UniqueConstraint('usuario_id', 'clave', name='uq_precio_venta_clave'),
        sa.UniqueConstraint('producto_id', 'version', name='uq_precio_venta_version'))
    op.create_table('cotizacion_venta',
        sa.Column('id', sa.String(36), primary_key=True, nullable=False),
        sa.Column('usuario_id', sa.Integer(), sa.ForeignKey('usuario.id', ondelete="RESTRICT"), nullable=False),
        sa.Column('clave', sa.String(80), nullable=False),
        sa.Column('huella', sa.String(64), nullable=False),
        sa.Column('lineas', sa.JSON(none_as_null=True).with_variant(postgresql.JSONB(none_as_null=True), "postgresql"), nullable=False),
        sa.Column('total', sa.Numeric(8, 2), nullable=False),
        sa.Column('moneda', sa.String(3), nullable=False),
        sa.Column('vence_en', sa.DateTime(timezone=True), nullable=False),
        sa.Column('creado_en', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint('total > 0 AND total <= 999999.99', name='ck_cotizacion_venta_total'),
        sa.UniqueConstraint('usuario_id', 'clave', name='uq_cotizacion_venta_clave'))
    op.create_table('ticket_venta',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('cotizacion_id', sa.String(36), sa.ForeignKey('cotizacion_venta.id', ondelete="RESTRICT"), nullable=False),
        sa.Column('usuario_id', sa.Integer(), sa.ForeignKey('usuario.id', ondelete="RESTRICT"), nullable=False),
        sa.Column('nombre_usuario', sa.String(150), nullable=False),
        sa.Column('clave', sa.String(80), nullable=False),
        sa.Column('huella', sa.String(64), nullable=False),
        sa.Column('canal', sa.String(16), nullable=False),
        sa.Column('estado', sa.String(16), nullable=False),
        sa.Column('total', sa.Numeric(8, 2), nullable=False),
        sa.Column('moneda', sa.String(3), nullable=False),
        sa.Column('cobro', sa.JSON(none_as_null=True).with_variant(postgresql.JSONB(none_as_null=True), "postgresql"), nullable=False),
        sa.Column('anulacion', sa.JSON(none_as_null=True).with_variant(postgresql.JSONB(none_as_null=True), "postgresql"), nullable=True),
        sa.Column('anulado_por', sa.Integer(), sa.ForeignKey('usuario.id', ondelete="RESTRICT"), nullable=True),
        sa.Column('clave_anulacion', sa.String(80), nullable=True),
        sa.Column('vendida_en', sa.DateTime(timezone=True), nullable=False),
        sa.Column('fecha_local', sa.Date(), nullable=False),
        sa.Column('zona_horaria', sa.String(80), nullable=False),
        sa.CheckConstraint("canal = 'PRESENCIAL'", name='ck_ticket_canal'),
        sa.CheckConstraint("(estado = 'CONFIRMADA' AND anulacion IS NULL) OR (estado = 'ANULADA' AND anulacion IS NOT NULL)", name='ck_ticket_estado'),
        sa.CheckConstraint('total > 0 AND total <= 999999.99', name='ck_ticket_total'),
        sa.UniqueConstraint('anulado_por', 'clave_anulacion', name='uq_ticket_anulacion_clave'),
        sa.UniqueConstraint('cotizacion_id', name='uq_ticket_cotizacion'),
        sa.UniqueConstraint('usuario_id', 'clave', name='uq_ticket_venta_clave'))
    op.create_index('ix_ticket_venta_fecha', 'ticket_venta', ['fecha_local', 'id'], unique=False)
    op.create_table('linea_ticket_venta',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('ticket_id', sa.Integer(), sa.ForeignKey('ticket_venta.id', ondelete="RESTRICT"), nullable=False),
        sa.Column('producto_id', sa.Integer(), sa.ForeignKey('producto.id', ondelete="RESTRICT"), nullable=False),
        sa.Column('precio_id', sa.Integer(), sa.ForeignKey('precio_producto_venta.id', ondelete="RESTRICT"), nullable=False),
        sa.Column('nombre', sa.String(160), nullable=False),
        sa.Column('codigo', sa.String(160), nullable=False),
        sa.Column('cantidad', sa.Integer(), nullable=False),
        sa.Column('precio', sa.Numeric(8, 2), nullable=False),
        sa.Column('subtotal', sa.Numeric(8, 2), nullable=False),
        sa.CheckConstraint('cantidad BETWEEN 1 AND 1000 AND precio > 0 AND subtotal = round(cantidad * precio, 2)', name='ck_linea_ticket_importes'),
        sa.UniqueConstraint('ticket_id', 'producto_id', name='uq_linea_ticket_producto'))
    op.create_index('ix_linea_ticket_venta_ticket_id', 'linea_ticket_venta', ['ticket_id'], unique=False)
    op.create_table('salida_lote_venta',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('linea_id', sa.Integer(), sa.ForeignKey('linea_ticket_venta.id', ondelete="RESTRICT"), nullable=False),
        sa.Column('lote_id', sa.Integer(), sa.ForeignKey('lote_producto.id', ondelete="RESTRICT"), nullable=False),
        sa.Column('cantidad', sa.Integer(), nullable=False),
        sa.Column('movimiento_id', sa.Integer(), sa.ForeignKey('movimiento_inventario.id', ondelete="RESTRICT"), nullable=False),
        sa.Column('compensacion_id', sa.Integer(), sa.ForeignKey('movimiento_inventario.id', ondelete="RESTRICT"), nullable=True),
        sa.UniqueConstraint('compensacion_id', name=None),
        sa.UniqueConstraint('movimiento_id', name=None),
        sa.CheckConstraint('cantidad > 0', name='ck_salida_venta_cantidad'),
        sa.UniqueConstraint('linea_id', 'lote_id', name='uq_salida_venta_lote'))
    op.create_index('ix_salida_lote_venta_linea_id', 'salida_lote_venta', ['linea_id'], unique=False)


def downgrade():
    for tabla in ("ticket_venta", "cotizacion_venta", "precio_producto_venta"):
        if op.get_bind().execute(sa.text(f"SELECT count(*) FROM {tabla}")).scalar_one():
            raise RuntimeError("Hay operaciones de caja conservadas; no se elimina su evidencia.")
    if op.get_bind().execute(sa.text("SELECT count(*) FROM movimiento_inventario WHERE tipo IN ('VENTA','ANULA_VENTA')")).scalar_one():
        raise RuntimeError("Hay movimientos de ventas conservados.")
    op.drop_table('salida_lote_venta')
    op.drop_table('linea_ticket_venta')
    op.drop_table('ticket_venta')
    op.drop_table('cotizacion_venta')
    op.drop_table('precio_producto_venta')
    with op.batch_alter_table("movimiento_inventario") as t:
        t.drop_constraint("ck_movimiento_venta_producto", type_="check")
        t.drop_constraint("ck_movimiento_inventario_tipo", type_="check")
        t.create_check_constraint("ck_movimiento_inventario_tipo", "tipo in ('APERTURA', 'AJUSTE', 'RECEPCION')")
