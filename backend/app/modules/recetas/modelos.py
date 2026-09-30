"""Recetas versionadas por producto (M01).

Una receta es inmutable una vez creada: cambiarla crea la versión siguiente y
desactiva la anterior. Así un plan que guardó `receta_id` sigue explicando sus
cantidades aunque la receta del producto cambie después.
"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.base import Base


class Receta(Base):
    __tablename__ = "receta"
    __table_args__ = (
        UniqueConstraint("producto_id", "version", name="uq_receta_producto_version"),
        CheckConstraint("version >= 1", name="ck_receta_version"),
        # Una sola versión activa por producto.
        Index(
            "uq_receta_activa_por_producto",
            "producto_id",
            unique=True,
            postgresql_where=text("activo"),
            sqlite_where=text("activo = 1"),
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("producto.id", ondelete="RESTRICT"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default="true")
    motivo: Mapped[str | None] = mapped_column(String(300))
    creado_por: Mapped[int | None] = mapped_column(ForeignKey("usuario.id", ondelete="RESTRICT"))
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    lineas: Mapped[list["RecetaIngrediente"]] = relationship(
        back_populates="receta", order_by="RecetaIngrediente.id", lazy="selectin"
    )


class RecetaIngrediente(Base):
    __tablename__ = "receta_ingrediente"
    __table_args__ = (
        UniqueConstraint("receta_id", "ingrediente_id", name="uq_receta_ingrediente_pareja"),
        CheckConstraint("cantidad_por_unidad > 0", name="ck_receta_ingrediente_cantidad"),
        Index("ix_receta_ingrediente_ingrediente", "ingrediente_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    receta_id: Mapped[int] = mapped_column(ForeignKey("receta.id", ondelete="RESTRICT"), nullable=False)
    ingrediente_id: Mapped[int] = mapped_column(ForeignKey("ingrediente.id", ondelete="RESTRICT"), nullable=False)
    # Cantidad por UNA unidad de producto, en la unidad base del ingrediente.
    cantidad_por_unidad: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)

    receta: Mapped[Receta] = relationship(back_populates="lineas")
