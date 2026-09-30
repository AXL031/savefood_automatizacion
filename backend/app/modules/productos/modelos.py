"""Catálogo local y correspondencia explícita con los SKU del archivo."""

from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base


class Producto(Base):
    __tablename__ = "producto"
    __table_args__ = (
        UniqueConstraint("codigo", name="uq_producto_codigo"),
        CheckConstraint("length(trim(codigo)) > 0", name="ck_producto_codigo"),
        CheckConstraint("length(trim(nombre)) > 0", name="ck_producto_nombre"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    codigo: Mapped[str] = mapped_column(String(160), nullable=False)
    nombre: Mapped[str] = mapped_column(String(160), nullable=False)
    demostrar: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default="false")
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class SkuProducto(Base):
    __tablename__ = "sku_producto"
    __table_args__ = (
        UniqueConstraint("origen", "sku_externo", name="uq_sku_producto_origen_sku"),
        CheckConstraint("length(trim(origen)) > 0", name="ck_sku_producto_origen"),
        CheckConstraint("length(trim(sku_externo)) > 0", name="ck_sku_producto_sku"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("producto.id", ondelete="RESTRICT"), nullable=False)
    origen: Mapped[str] = mapped_column(String(40), nullable=False)
    sku_externo: Mapped[str] = mapped_column(String(160), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
