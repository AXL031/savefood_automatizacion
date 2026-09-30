"""Catálogo de ingredientes con unidad base inequívoca (M01)."""

from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base

# Unidades admitidas por la plantilla de primera carga. No se convierten entre sí:
# receta, lote y oferta de compra usan siempre la unidad base del ingrediente.
UNIDADES_BASE = ("g", "kg", "ml", "l", "unidad")


class Ingrediente(Base):
    __tablename__ = "ingrediente"
    __table_args__ = (
        UniqueConstraint("codigo", name="uq_ingrediente_codigo"),
        CheckConstraint("length(trim(codigo)) > 0", name="ck_ingrediente_codigo"),
        CheckConstraint("length(trim(nombre)) > 0", name="ck_ingrediente_nombre"),
        CheckConstraint(
            "unidad_base in ('g', 'kg', 'ml', 'l', 'unidad')", name="ck_ingrediente_unidad_base"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    codigo: Mapped[str] = mapped_column(String(160), nullable=False)
    nombre: Mapped[str] = mapped_column(String(160), nullable=False)
    unidad_base: Mapped[str] = mapped_column(String(10), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
