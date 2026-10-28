from datetime import datetime, timezone
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, JSON, String, Index
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class PagoTiendaPrueba(Base):
    """Operación de preproducción; no es una venta ni un movimiento de inventario."""
    __tablename__ = "pago_tienda_prueba"
    __table_args__ = (
        CheckConstraint("metodo IN ('CARD','YAPE','QR','PAGOEFECTIVO')", name="ck_pago_prueba_metodo"),
        CheckConstraint("monto_centimos > 0", name="ck_pago_prueba_monto"),
    )
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    clave_hash: Mapped[str] = mapped_column(String(64), unique=True)
    huella: Mapped[str] = mapped_column(String(64))
    operacion: Mapped[str] = mapped_column(String(12), unique=True)
    merchant_code: Mapped[str] = mapped_column(String(255))
    metodo: Mapped[str] = mapped_column(String(20))
    monto_centimos: Mapped[int] = mapped_column(Integer)
    estado: Mapped[str] = mapped_column(String(24), default="CREADO")
    snapshot: Mapped[dict] = mapped_column(JSON)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    actualizado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class TransaccionPaymePrueba(Base):
    __tablename__ = "transaccion_payme_prueba"
    transaction_id: Mapped[str] = mapped_column(String(128), primary_key=True)
    pago_id: Mapped[str] = mapped_column(ForeignKey("pago_tienda_prueba.id", ondelete="RESTRICT"), index=True)
    estado: Mapped[str] = mapped_column(String(24))
    detalles: Mapped[dict] = mapped_column(JSON)
    huella_evento: Mapped[str] = mapped_column(String(64))
    actualizado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class CatalogoPublicado(Base):
    __tablename__ = 'catalogo_publicado'
    __table_args__ = (CheckConstraint('id = 1 AND version > 0',name='ck_catalogo_publicado_version'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    origen: Mapped[str] = mapped_column(String(36),unique=True)
    version: Mapped[int] = mapped_column(Integer)
    huella: Mapped[str] = mapped_column(String(64))
    datos: Mapped[dict] = mapped_column(JSON)
    recibido_en: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc))


class PedidoComercial(Base):
    """Entrega durable del pago verificado; no es un segundo inventario ni ticket."""
    __tablename__ = 'pedido_comercial'
    __table_args__ = (CheckConstraint("estado IN ('PREPARANDO','RESERVADA','PENDIENTE_VENTA','REGISTRADA','LIBERACION_PENDIENTE','LIBERADA','REVISION_REQUERIDA') AND intentos >= 0",name='ck_pedido_comercial_estado'),
                     Index('ix_pedido_comercial_reintentos','estado','proximo_intento'))
    pago_id: Mapped[str] = mapped_column(ForeignKey('pago_tienda_prueba.id',ondelete='RESTRICT'),primary_key=True)
    origen: Mapped[str] = mapped_column(String(36))
    solicitud_reserva: Mapped[dict] = mapped_column(JSON)
    reserva: Mapped[dict | None] = mapped_column(JSON)
    evento_venta: Mapped[dict | None] = mapped_column(JSON)
    acuse: Mapped[dict | None] = mapped_column(JSON)
    estado: Mapped[str] = mapped_column(String(32),default='PREPARANDO')
    intentos: Mapped[int] = mapped_column(Integer,default=0)
    ultimo_error: Mapped[str | None] = mapped_column(String(160))
    proximo_intento: Mapped[datetime] = mapped_column(DateTime(timezone=True),default=lambda:datetime.now(timezone.utc))
