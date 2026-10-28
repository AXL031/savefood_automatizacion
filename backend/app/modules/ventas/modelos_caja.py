"""Caja presencial: precios y tickets conservan sus versiones; no contienen pagos de tienda."""
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, Integer, JSON, Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base import Base

Json = JSON(none_as_null=True).with_variant(JSONB(none_as_null=True), "postgresql")


class PrecioVenta(Base):
    __tablename__ = "precio_producto_venta"
    __table_args__ = (UniqueConstraint("producto_id", "version", name="uq_precio_venta_version"),
        UniqueConstraint("usuario_id", "clave", name="uq_precio_venta_clave"),
        CheckConstraint("version > 0 AND precio > 0 AND precio <= 999999.99", name="ck_precio_venta_valores"))
    id: Mapped[int] = mapped_column(primary_key=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("producto.id", ondelete="RESTRICT"), nullable=False)
    version: Mapped[int] = mapped_column(nullable=False)
    precio: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuario.id", ondelete="RESTRICT"), nullable=False)
    clave: Mapped[str] = mapped_column(String(80), nullable=False)
    huella: Mapped[str] = mapped_column(String(64), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class CotizacionVenta(Base):
    __tablename__ = "cotizacion_venta"
    __table_args__ = (UniqueConstraint("usuario_id", "clave", name="uq_cotizacion_venta_clave"),
        UniqueConstraint("integracion_id", "clave", name="uq_cotizacion_integracion_clave"),
        CheckConstraint("(canal = 'PRESENCIAL' AND usuario_id IS NOT NULL AND integracion_id IS NULL) OR (canal = 'TIENDA' AND usuario_id IS NULL AND integracion_id IS NOT NULL)", name="ck_cotizacion_identidad"),
        CheckConstraint("total > 0 AND total <= 999999.99", name="ck_cotizacion_venta_total"))
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuario.id", ondelete="RESTRICT"))
    canal: Mapped[str] = mapped_column(String(16), nullable=False, default="PRESENCIAL", server_default="PRESENCIAL")
    integracion_id: Mapped[str | None] = mapped_column(String(64))
    clave: Mapped[str] = mapped_column(String(80), nullable=False)
    huella: Mapped[str] = mapped_column(String(64), nullable=False)
    lineas: Mapped[list] = mapped_column(Json, nullable=False)
    total: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    moneda: Mapped[str] = mapped_column(String(3), nullable=False)
    vence_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class TicketVenta(Base):
    __tablename__ = "ticket_venta"
    __table_args__ = (UniqueConstraint("cotizacion_id", name="uq_ticket_cotizacion"),
        UniqueConstraint("usuario_id", "clave", name="uq_ticket_venta_clave"),
        UniqueConstraint("anulado_por", "clave_anulacion", name="uq_ticket_anulacion_clave"),
        UniqueConstraint("integracion_id", "clave", name="uq_ticket_integracion_clave"),
        UniqueConstraint("integracion_id", "pedido_externo", name="uq_ticket_pedido_externo"),
        UniqueConstraint("pago_externo_id", name="uq_ticket_pago_externo"),
        CheckConstraint("(canal = 'PRESENCIAL' AND usuario_id IS NOT NULL AND integracion_id IS NULL AND pedido_externo IS NULL AND pago_externo_id IS NULL) OR (canal = 'TIENDA' AND usuario_id IS NULL AND integracion_id IS NOT NULL AND pedido_externo IS NOT NULL AND pago_externo_id IS NOT NULL)", name="ck_ticket_canal"),
        CheckConstraint("total > 0 AND total <= 999999.99", name="ck_ticket_total"),
        CheckConstraint("(estado = 'CONFIRMADA' AND anulacion IS NULL) OR (estado = 'ANULADA' AND anulacion IS NOT NULL)", name="ck_ticket_estado"),
        Index("ix_ticket_venta_fecha", "fecha_local", "id"))
    id: Mapped[int] = mapped_column(primary_key=True)
    cotizacion_id: Mapped[str] = mapped_column(ForeignKey("cotizacion_venta.id", ondelete="RESTRICT"), nullable=False)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuario.id", ondelete="RESTRICT"))
    integracion_id: Mapped[str | None] = mapped_column(String(64))
    pedido_externo: Mapped[str | None] = mapped_column(String(36))
    pago_externo_id: Mapped[str | None] = mapped_column(String(128))
    nombre_usuario: Mapped[str] = mapped_column(String(150), nullable=False)
    clave: Mapped[str] = mapped_column(String(80), nullable=False)
    huella: Mapped[str] = mapped_column(String(64), nullable=False)
    canal: Mapped[str] = mapped_column(String(16), nullable=False, default="PRESENCIAL")
    estado: Mapped[str] = mapped_column(String(16), nullable=False, default="CONFIRMADA")
    total: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    moneda: Mapped[str] = mapped_column(String(3), nullable=False)
    cobro: Mapped[dict] = mapped_column(Json, nullable=False)
    anulacion: Mapped[dict | None] = mapped_column(Json)
    anulado_por: Mapped[int | None] = mapped_column(ForeignKey("usuario.id", ondelete="RESTRICT"))
    clave_anulacion: Mapped[str | None] = mapped_column(String(80))
    vendida_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fecha_local: Mapped[date] = mapped_column(Date, nullable=False)
    zona_horaria: Mapped[str] = mapped_column(String(80), nullable=False)


class LineaTicketVenta(Base):
    __tablename__ = "linea_ticket_venta"
    __table_args__ = (UniqueConstraint("ticket_id", "producto_id", name="uq_linea_ticket_producto"),
        CheckConstraint("cantidad BETWEEN 1 AND 1000 AND precio > 0 AND subtotal >= 0 AND subtotal <= round(cantidad * precio, 2) AND (segmentos IS NOT NULL OR subtotal = round(cantidad * precio, 2))", name="ck_linea_ticket_importes"))
    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("ticket_venta.id", ondelete="RESTRICT"), nullable=False, index=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("producto.id", ondelete="RESTRICT"), nullable=False)
    precio_id: Mapped[int] = mapped_column(ForeignKey("precio_producto_venta.id", ondelete="RESTRICT"), nullable=False)
    nombre: Mapped[str] = mapped_column(String(160), nullable=False)
    codigo: Mapped[str] = mapped_column(String(160), nullable=False)
    cantidad: Mapped[int] = mapped_column(nullable=False)
    precio: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    subtotal: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False)
    segmentos: Mapped[list | None] = mapped_column(Json)


class SalidaLoteVenta(Base):
    __tablename__ = "salida_lote_venta"
    __table_args__ = (UniqueConstraint("linea_id", "lote_id", name="uq_salida_venta_lote"),
        CheckConstraint("cantidad > 0", name="ck_salida_venta_cantidad"))
    id: Mapped[int] = mapped_column(primary_key=True)
    linea_id: Mapped[int] = mapped_column(ForeignKey("linea_ticket_venta.id", ondelete="RESTRICT"), nullable=False, index=True)
    lote_id: Mapped[int] = mapped_column(ForeignKey("lote_producto.id", ondelete="RESTRICT"), nullable=False)
    cantidad: Mapped[int] = mapped_column(nullable=False)
    movimiento_id: Mapped[int] = mapped_column(ForeignKey("movimiento_inventario.id", ondelete="RESTRICT"), nullable=False, unique=True)
    compensacion_id: Mapped[int | None] = mapped_column(ForeignKey("movimiento_inventario.id", ondelete="RESTRICT"), unique=True)
