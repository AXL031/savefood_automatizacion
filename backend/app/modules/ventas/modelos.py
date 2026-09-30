"""Ventas agregadas y revisiones auditables de la sucursal local."""

from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base


class ImportacionVenta(Base):
    __tablename__ = "importacion_venta"
    __table_args__ = (
        UniqueConstraint("origen", "clave_importacion", name="uq_importacion_venta_clave"),
        CheckConstraint("filas_aceptadas >= 0", name="ck_importacion_venta_filas"),
        CheckConstraint("estado = 'COMPLETADA'", name="ck_importacion_venta_estado"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    origen: Mapped[str] = mapped_column(String(40), nullable=False)
    clave_importacion: Mapped[str] = mapped_column(String(128), nullable=False)
    huella_contenido: Mapped[str] = mapped_column(String(64), nullable=False)
    filas_aceptadas: Mapped[int] = mapped_column(Integer, nullable=False)
    estado: Mapped[str] = mapped_column(String(16), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class VentaDiaria(Base):
    __tablename__ = "venta_diaria"
    __table_args__ = (
        UniqueConstraint("producto_id", "fecha_local", name="uq_venta_diaria_producto_fecha"),
        Index("ix_venta_diaria_fecha", "fecha_local"),
        CheckConstraint("unidades_vendidas >= 0", name="ck_venta_diaria_unidades"),
        CheckConstraint("revision_actual >= 1", name="ck_venta_diaria_revision"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("producto.id", ondelete="RESTRICT"), nullable=False)
    fecha_local: Mapped[date] = mapped_column(Date, nullable=False)
    unidades_vendidas: Mapped[int] = mapped_column(Integer, nullable=False)
    importacion_id: Mapped[int | None] = mapped_column(ForeignKey("importacion_venta.id", ondelete="RESTRICT"))
    revision_actual: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    actualizado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class RevisionVenta(Base):
    __tablename__ = "revision_venta"
    __table_args__ = (
        UniqueConstraint("venta_id", "numero_revision", name="uq_revision_venta_numero"),
        CheckConstraint("numero_revision >= 1", name="ck_revision_venta_numero"),
        CheckConstraint("unidades_vendidas >= 0", name="ck_revision_venta_unidades"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    venta_id: Mapped[int] = mapped_column(ForeignKey("venta_diaria.id", ondelete="RESTRICT"), nullable=False)
    numero_revision: Mapped[int] = mapped_column(Integer, nullable=False)
    unidades_vendidas: Mapped[int] = mapped_column(Integer, nullable=False)
    origen_cambio: Mapped[str] = mapped_column(String(32), nullable=False)
    motivo: Mapped[str] = mapped_column(String(255), nullable=False)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuario.id", ondelete="RESTRICT"))
    importacion_id: Mapped[int | None] = mapped_column(ForeignKey("importacion_venta.id", ondelete="RESTRICT"))
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
