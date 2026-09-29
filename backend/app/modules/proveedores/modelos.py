"""Tablas propias: proveedor y oferta_ingrediente."""
from decimal import Decimal
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Numeric, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

try:  # AJUSTAR: usar la Base común del proyecto
    from app.db.base import Base
except ImportError:  # solo para pruebas aisladas
    from sqlalchemy.orm import DeclarativeBase

    class Base(DeclarativeBase):
        pass


class Proveedor(Base):
    __tablename__ = "proveedor"

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(30), unique=True)
    nombre: Mapped[str] = mapped_column(String(120))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    # Solo el identificador del chat; la credencial vive en configuración, nunca aquí.
    chat_id_pruebas: Mapped[str | None] = mapped_column(String(64), nullable=True)
    destino_verificado: Mapped[bool] = mapped_column(Boolean, default=False)
    destino_verificado_en: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    ofertas: Mapped[list["OfertaIngrediente"]] = relationship(back_populates="proveedor")


class OfertaIngrediente(Base):
    __tablename__ = "oferta_ingrediente"

    id: Mapped[int] = mapped_column(primary_key=True)
    proveedor_id: Mapped[int] = mapped_column(ForeignKey("proveedor.id"))
    # Ingrediente es de Max: se guarda solo el id, sin escribir su tabla.
    ingrediente_id: Mapped[int] = mapped_column(index=True)
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
        # Máximo una oferta preferida activa por ingrediente.
        Index(
            "uq_oferta_preferida_activa",
            "ingrediente_id",
            unique=True,
            sqlite_where=text("preferida = 1 AND activa = 1"),
            postgresql_where=text("preferida AND activa"),
        ),
    )
