"""Publicación, reservas y entrega durable; la venta vive en ticket_venta."""
from datetime import date, datetime
from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, ForeignKey, Index, Integer, JSON, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base import Base


class ConfiguracionComercio(Base):
    __tablename__ = 'configuracion_comercio'
    __table_args__ = (CheckConstraint('id = 1 AND version >= 0', name='ck_comercio_unico'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    origen: Mapped[str] = mapped_column(String(36), unique=True)
    version: Mapped[int] = mapped_column(Integer, default=0)


class PublicacionProducto(Base):
    __tablename__ = 'publicacion_producto'
    __table_args__ = (CheckConstraint('version > 0', name='ck_publicacion_version'),)
    producto_id: Mapped[int] = mapped_column(ForeignKey('producto.id', ondelete='RESTRICT'), primary_key=True)
    publicado: Mapped[bool] = mapped_column(Boolean, default=False)
    version: Mapped[int] = mapped_column(Integer, default=1)
    datos: Mapped[dict] = mapped_column(JSON)
    usuario_id: Mapped[int] = mapped_column(ForeignKey('usuario.id', ondelete='RESTRICT'), index=True)
    actualizado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class EventoPublicacion(Base):
    __tablename__ = 'evento_publicacion'
    __table_args__ = (CheckConstraint("estado IN ('PENDIENTE','CONFIRMADO') AND intentos >= 0", name='ck_evento_publicacion_estado'),
                     Index('ix_evento_publicacion_pendiente', 'estado', 'proximo_intento'))
    id: Mapped[int] = mapped_column(primary_key=True)
    version: Mapped[int] = mapped_column(Integer, unique=True)
    huella: Mapped[str] = mapped_column(String(64))
    datos: Mapped[dict] = mapped_column(JSON)
    estado: Mapped[str] = mapped_column(String(16), default='PENDIENTE')
    intentos: Mapped[int] = mapped_column(Integer, default=0)
    proximo_intento: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ultimo_error: Mapped[str | None] = mapped_column(String(160))
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ReservaTienda(Base):
    __tablename__ = 'reserva_tienda'
    __table_args__ = (UniqueConstraint('integracion_id', 'clave', name='uq_reserva_tienda_clave'),
                     CheckConstraint("estado IN ('ACTIVA','CONSUMIDA','LIBERADA')", name='ck_reserva_tienda_estado'),
                     Index('ix_reserva_tienda_vigencia', 'estado', 'vence_en'))
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    cotizacion_id: Mapped[str] = mapped_column(ForeignKey('cotizacion_venta.id', ondelete='RESTRICT'), unique=True)
    integracion_id: Mapped[str] = mapped_column(String(64))
    clave: Mapped[str] = mapped_column(String(80))
    huella: Mapped[str] = mapped_column(String(64))
    estado: Mapped[str] = mapped_column(String(16), default='ACTIVA')
    motivo_liberacion: Mapped[str | None] = mapped_column(String(24))
    fecha_local: Mapped[date] = mapped_column(Date)
    zona_horaria: Mapped[str] = mapped_column(String(80))
    vence_en: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AsignacionReserva(Base):
    __tablename__ = 'asignacion_reserva'
    __table_args__ = (UniqueConstraint('reserva_id', 'lote_id', name='uq_asignacion_reserva_lote'),
                     CheckConstraint('cantidad > 0', name='ck_asignacion_reserva_cantidad'))
    id: Mapped[int] = mapped_column(primary_key=True)
    reserva_id: Mapped[str] = mapped_column(ForeignKey('reserva_tienda.id', ondelete='RESTRICT'), index=True)
    lote_id: Mapped[int] = mapped_column(ForeignKey('lote_producto.id', ondelete='RESTRICT'), index=True)
    cantidad: Mapped[int] = mapped_column(Integer)
