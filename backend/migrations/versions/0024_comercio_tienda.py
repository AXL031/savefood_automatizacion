"""Publicación HTTP, reservas y tickets del canal tienda; conserva caja previa."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0024_comercio_tienda'
down_revision = '0023_operaciones_compatibles'
branch_labels = depends_on = None
J = sa.JSON(none_as_null=True).with_variant(postgresql.JSONB(none_as_null=True), 'postgresql')
IDENTIDAD = "(canal = 'PRESENCIAL' AND usuario_id IS NOT NULL AND integracion_id IS NULL) OR (canal = 'TIENDA' AND usuario_id IS NULL AND integracion_id IS NOT NULL)"
TICKET = "(canal = 'PRESENCIAL' AND usuario_id IS NOT NULL AND integracion_id IS NULL AND pedido_externo IS NULL AND pago_externo_id IS NULL) OR (canal = 'TIENDA' AND usuario_id IS NULL AND integracion_id IS NOT NULL AND pedido_externo IS NOT NULL AND pago_externo_id IS NOT NULL)"


def upgrade():
    with op.batch_alter_table('cotizacion_venta') as b:
        b.alter_column('usuario_id', existing_type=sa.Integer(), nullable=True)
        b.add_column(sa.Column('canal', sa.String(16), nullable=False, server_default='PRESENCIAL'))
        b.add_column(sa.Column('integracion_id', sa.String(64)))
        b.create_unique_constraint('uq_cotizacion_integracion_clave', ['integracion_id','clave'])
        b.create_check_constraint('ck_cotizacion_identidad', IDENTIDAD)
    with op.batch_alter_table('ticket_venta') as b:
        b.alter_column('usuario_id', existing_type=sa.Integer(), nullable=True)
        b.add_column(sa.Column('integracion_id', sa.String(64)))
        b.add_column(sa.Column('pedido_externo', sa.String(36)))
        b.add_column(sa.Column('pago_externo_id', sa.String(128)))
        b.create_unique_constraint('uq_ticket_pago_externo', ['pago_externo_id'])
        b.create_unique_constraint('uq_ticket_integracion_clave', ['integracion_id','clave'])
        b.create_unique_constraint('uq_ticket_pedido_externo', ['integracion_id','pedido_externo'])
        b.drop_constraint('ck_ticket_canal', type_='check')
        b.create_check_constraint('ck_ticket_canal', TICKET)
    with op.batch_alter_table('linea_ticket_venta') as b:
        b.add_column(sa.Column('segmentos', J))
        b.drop_constraint('ck_linea_ticket_importes', type_='check')
        b.create_check_constraint('ck_linea_ticket_importes', "cantidad BETWEEN 1 AND 1000 AND precio > 0 AND subtotal >= 0 AND subtotal <= round(cantidad * precio, 2) AND (segmentos IS NOT NULL OR subtotal = round(cantidad * precio, 2))")
    op.create_table('configuracion_comercio', sa.Column('id',sa.Integer(),primary_key=True),
        sa.Column('origen',sa.String(36),nullable=False,unique=True),sa.Column('version',sa.Integer(),nullable=False),
        sa.CheckConstraint('id = 1 AND version >= 0',name='ck_comercio_unico'))
    op.create_table('publicacion_producto',
        sa.Column('producto_id',sa.Integer(),sa.ForeignKey('producto.id',ondelete='RESTRICT'),primary_key=True),
        sa.Column('publicado',sa.Boolean(),nullable=False),sa.Column('version',sa.Integer(),nullable=False),
        sa.Column('datos',sa.JSON(),nullable=False),sa.Column('usuario_id',sa.Integer(),sa.ForeignKey('usuario.id',ondelete='RESTRICT'),nullable=False),
        sa.Column('actualizado_en',sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False),
        sa.CheckConstraint('version > 0',name='ck_publicacion_version'))
    op.create_index('ix_publicacion_producto_usuario_id','publicacion_producto',['usuario_id'])
    op.create_table('evento_publicacion',sa.Column('id',sa.Integer(),primary_key=True),
        sa.Column('version',sa.Integer(),nullable=False,unique=True),sa.Column('huella',sa.String(64),nullable=False),
        sa.Column('datos',sa.JSON(),nullable=False),sa.Column('estado',sa.String(16),nullable=False),
        sa.Column('intentos',sa.Integer(),nullable=False),sa.Column('proximo_intento',sa.DateTime(timezone=True),nullable=False),
        sa.Column('ultimo_error',sa.String(160)),sa.Column('creado_en',sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False),
        sa.CheckConstraint("estado IN ('PENDIENTE','CONFIRMADO') AND intentos >= 0",name='ck_evento_publicacion_estado'))
    op.create_index('ix_evento_publicacion_pendiente','evento_publicacion',['estado','proximo_intento'])
    op.create_table('reserva_tienda',sa.Column('id',sa.String(36),primary_key=True),
        sa.Column('cotizacion_id',sa.String(36),sa.ForeignKey('cotizacion_venta.id',ondelete='RESTRICT'),nullable=False,unique=True),
        sa.Column('integracion_id',sa.String(64),nullable=False),sa.Column('clave',sa.String(80),nullable=False),
        sa.Column('huella',sa.String(64),nullable=False),sa.Column('estado',sa.String(16),nullable=False),
        sa.Column('motivo_liberacion',sa.String(24)),
        sa.Column('fecha_local',sa.Date(),nullable=False),sa.Column('zona_horaria',sa.String(80),nullable=False),
        sa.Column('vence_en',sa.DateTime(timezone=True),nullable=False),
        sa.Column('creado_en',sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=False),
        sa.UniqueConstraint('integracion_id','clave',name='uq_reserva_tienda_clave'),
        sa.CheckConstraint("estado IN ('ACTIVA','CONSUMIDA','LIBERADA')",name='ck_reserva_tienda_estado'))
    op.create_index('ix_reserva_tienda_vigencia','reserva_tienda',['estado','vence_en'])
    op.create_table('asignacion_reserva',sa.Column('id',sa.Integer(),primary_key=True),
        sa.Column('reserva_id',sa.String(36),sa.ForeignKey('reserva_tienda.id',ondelete='RESTRICT'),nullable=False),
        sa.Column('lote_id',sa.Integer(),sa.ForeignKey('lote_producto.id',ondelete='RESTRICT'),nullable=False),
        sa.Column('cantidad',sa.Integer(),nullable=False),sa.UniqueConstraint('reserva_id','lote_id',name='uq_asignacion_reserva_lote'),
        sa.CheckConstraint('cantidad > 0',name='ck_asignacion_reserva_cantidad'))
    op.create_index('ix_asignacion_reserva_reserva_id','asignacion_reserva',['reserva_id'])
    op.create_index('ix_asignacion_reserva_lote_id','asignacion_reserva',['lote_id'])


def downgrade():
    c=op.get_bind()
    if any(c.execute(sa.text(f'SELECT count(*) FROM {t}')).scalar() for t in ('configuracion_comercio','publicacion_producto','evento_publicacion','reserva_tienda','asignacion_reserva')) or c.execute(sa.text("SELECT count(*) FROM ticket_venta WHERE canal='TIENDA'")).scalar():
        raise RuntimeError('Conservar evidencia de comercio/reservas; no se elimina esta revisión con datos.')
    for tabla in ('asignacion_reserva','reserva_tienda','evento_publicacion','publicacion_producto','configuracion_comercio'): op.drop_table(tabla)
    with op.batch_alter_table('linea_ticket_venta') as b:
        b.drop_constraint('ck_linea_ticket_importes',type_='check')
        b.create_check_constraint('ck_linea_ticket_importes', 'cantidad BETWEEN 1 AND 1000 AND precio > 0 AND subtotal = round(cantidad * precio, 2)')
        b.drop_column('segmentos')
    with op.batch_alter_table('ticket_venta') as b:
        b.drop_constraint('ck_ticket_canal',type_='check')
        b.create_check_constraint('ck_ticket_canal', "canal = 'PRESENCIAL'")
        for nombre in ('uq_ticket_pago_externo','uq_ticket_integracion_clave','uq_ticket_pedido_externo'): b.drop_constraint(nombre,type_='unique')
        for columna in ('pago_externo_id','pedido_externo','integracion_id'): b.drop_column(columna)
        b.alter_column('usuario_id',existing_type=sa.Integer(),nullable=False)
    with op.batch_alter_table('cotizacion_venta') as b:
        b.drop_constraint('ck_cotizacion_identidad',type_='check')
        b.drop_constraint('uq_cotizacion_integracion_clave',type_='unique')
        b.drop_column('integracion_id'); b.drop_column('canal')
        b.alter_column('usuario_id',existing_type=sa.Integer(),nullable=False)
