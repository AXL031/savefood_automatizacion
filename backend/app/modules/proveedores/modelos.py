"""Tablas propias: proveedor y oferta_ingrediente."""
from decimal import Decimal
from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base


class Proveedor(Base):
    __tablename__ = "proveedor"
    __table_args__ = (
        CheckConstraint("length(trim(codigo)) > 0", name="ck_proveedor_codigo"),
        CheckConstraint("length(trim(nombre)) > 0", name="ck_proveedor_nombre"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(30), unique=True)
    nombre: Mapped[str] = mapped_column(String(120))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    # Solo el identificador del chat; la credencial vive en configuración, nunca aquí.
    chat_id_pruebas: Mapped[str | None] = mapped_column(String(64), nullable=True)
    destino_verificado: Mapped[bool] = mapped_column(Boolean, default=False)
    destino_verificado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    ofertas: Mapped[list["OfertaIngrediente"]] = relationship(back_populates="proveedor")


class OfertaIngrediente(Base):
    __tablename__ = "oferta_ingrediente"

    id: Mapped[int] = mapped_column(primary_key=True)
    proveedor_id: Mapped[int] = mapped_column(ForeignKey("proveedor.id"))
    ingrediente_id: Mapped[int] = mapped_column(ForeignKey("ingrediente.id", ondelete="RESTRICT"), index=True)
    descripcion: Mapped[str] = mapped_column(String(120))
    unidad_compra: Mapped[str] = mapped_column(String(30))
    # Unidades base del ingrediente por cada unidad de compra. Siempre explícito.
    factor_conversion: Mapped[Decimal] = mapped_column(Numeric(14, 4))
    minimo: Mapped[Decimal] = mapped_column(Numeric(14, 4), default=0)
    multiplo: Mapped[Decimal] = mapped_column(Numeric(14, 4), default=1)
    activa: Mapped[bool] = mapped_column(Boolean, default=True)
    preferida: Mapped[bool] = mapped_column(Boolean, default=False)

    proveedor: Mapped[Proveedor] = relationship(back_populates="ofertas")

    __table_args__ = (
        CheckConstraint("factor_conversion > 0", name="ck_oferta_factor"),
        CheckConstraint("multiplo > 0", name="ck_oferta_multiplo"),
        CheckConstraint("minimo >= 0", name="ck_oferta_minimo"),
        # Máximo una oferta preferida activa por ingrediente.
        Index(
            "uq_oferta_preferida_activa",
            "ingrediente_id",
            unique=True,
            sqlite_where=text("preferida = 1 AND activa = 1"),
            postgresql_where=text("preferida AND activa"),
        ),
    )
