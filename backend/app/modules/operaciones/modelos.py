"""Auditoría y estado del recorrido operativo; stock conserva tablas de Inventario."""
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, ForeignKey, Integer, JSON, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base import Base


class RegistroOperacion(Base):
    __tablename__ = 'registro_operacion'
    __table_args__ = (CheckConstraint("tipo in ('PRODUCCION','RECEPCION')", name='ck_registro_operacion_tipo'),)
    id: Mapped[int] = mapped_column(primary_key=True)
    clave: Mapped[str] = mapped_column(String(100), unique=True)
    tipo: Mapped[str] = mapped_column(String(24))
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey('usuario.id', ondelete='RESTRICT'), index=True)
    plan_id: Mapped[int | None] = mapped_column(ForeignKey('plan_produccion.id', ondelete='RESTRICT'), index=True)
    fecha: Mapped[date] = mapped_column(Date)
    solicitud: Mapped[dict] = mapped_column(JSON)
    resultado: Mapped[dict] = mapped_column(JSON, default=dict)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ConfiguracionOperacion(Base):
    __tablename__ = 'configuracion_operacion'
    id: Mapped[int] = mapped_column(primary_key=True)
    datos: Mapped[dict] = mapped_column(JSON)
    proxima_revision: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class AvisoOperacion(Base):
    __tablename__ = 'aviso_operacion'
    id: Mapped[int] = mapped_column(primary_key=True)
    clave: Mapped[str] = mapped_column(String(140), unique=True)
    titulo: Mapped[str] = mapped_column(String(200))
    datos: Mapped[dict] = mapped_column(JSON)
    leido: Mapped[bool] = mapped_column(Boolean, default=False)
    resolucion: Mapped[str | None] = mapped_column(String(1000))
    resuelto_por: Mapped[int | None] = mapped_column(ForeignKey('usuario.id', ondelete='RESTRICT'), index=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SolicitudProveedor(Base):
    __tablename__ = 'solicitud_proveedor'
    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey('pedido_compra.id', ondelete='RESTRICT'), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)
    estado: Mapped[str] = mapped_column(String(24), default='PENDIENTE')
    expira_en: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    respuesta: Mapped[dict | None] = mapped_column(JSON)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PromocionOperacion(Base):
    __tablename__ = 'promocion_operacion'
    id: Mapped[int] = mapped_column(primary_key=True)
    clave: Mapped[str] = mapped_column(String(120), unique=True)
    lote_id: Mapped[int] = mapped_column(ForeignKey('lote_producto.id', ondelete='RESTRICT'), index=True)
    regla_id: Mapped[int] = mapped_column(ForeignKey('regla_promocion_demo.id', ondelete='RESTRICT'), index=True)
    estado: Mapped[str] = mapped_column(String(24))
    descuento: Mapped[int | None] = mapped_column(Integer)
    motivo: Mapped[str] = mapped_column(String(500))
    fecha: Mapped[date] = mapped_column(Date)
    decidido_por: Mapped[int | None] = mapped_column(ForeignKey('usuario.id', ondelete='RESTRICT'), index=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

