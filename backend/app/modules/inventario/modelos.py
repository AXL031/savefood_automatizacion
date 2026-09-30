"""Stock por lotes y movimientos atómicos (V01/V02).

`saldo_disponible` es el saldo actual del lote. Solo cambia junto con un
`movimiento_inventario` en la misma transacción. Las lecturas agregadas
(disponibilidad por fecha) no son tablas.
"""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base

TIPO_APERTURA = "APERTURA"
TIPO_AJUSTE = "AJUSTE"
TIPOS_MOVIMIENTO = (TIPO_APERTURA, TIPO_AJUSTE)


class LoteIngrediente(Base):
    __tablename__ = "lote_ingrediente"
    __table_args__ = (
        UniqueConstraint("ingrediente_id", "codigo_lote", name="uq_lote_ingrediente_codigo"),
        CheckConstraint("saldo_disponible >= 0", name="ck_lote_ingrediente_saldo"),
        CheckConstraint("length(trim(codigo_lote)) > 0", name="ck_lote_ingrediente_codigo"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ingrediente_id: Mapped[int] = mapped_column(ForeignKey("ingrediente.id", ondelete="RESTRICT"), nullable=False)
    codigo_lote: Mapped[str] = mapped_column(String(80), nullable=False)
    lote_informado: Mapped[bool] = mapped_column(Boolean, nullable=False)
    fecha_caducidad: Mapped[date | None] = mapped_column(Date)
    saldo_disponible: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    actualizado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class LoteProducto(Base):
    __tablename__ = "lote_producto"
    __table_args__ = (
        UniqueConstraint("producto_id", "codigo_lote", name="uq_lote_producto_codigo"),
        CheckConstraint("saldo_disponible >= 0", name="ck_lote_producto_saldo"),
        CheckConstraint("length(trim(codigo_lote)) > 0", name="ck_lote_producto_codigo"),
        CheckConstraint(
            "fecha_limite_venta is null or fecha_caducidad is null or fecha_limite_venta <= fecha_caducidad",
            name="ck_lote_producto_limite_venta",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    producto_id: Mapped[int] = mapped_column(ForeignKey("producto.id", ondelete="RESTRICT"), nullable=False)
    codigo_lote: Mapped[str] = mapped_column(String(80), nullable=False)
    lote_informado: Mapped[bool] = mapped_column(Boolean, nullable=False)
    # Para pastelería, la caducidad es el último día de vida (día 5).
    fecha_caducidad: Mapped[date | None] = mapped_column(Date)
    fecha_limite_venta: Mapped[date | None] = mapped_column(Date)
    saldo_disponible: Mapped[int] = mapped_column(Integer, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    actualizado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class MovimientoInventario(Base):
    __tablename__ = "movimiento_inventario"
    __table_args__ = (
        UniqueConstraint("clave_operacion", name="uq_movimiento_inventario_clave"),
        CheckConstraint(
            "(lote_ingrediente_id is null) <> (lote_producto_id is null)",
            name="ck_movimiento_inventario_un_lote",
        ),
        CheckConstraint("delta <> 0", name="ck_movimiento_inventario_delta"),
        CheckConstraint(
            "lote_producto_id is null or delta = round(delta, 0)",
            name="ck_movimiento_inventario_delta_entero_producto",
        ),
        CheckConstraint("saldo_resultante >= 0", name="ck_movimiento_inventario_saldo"),
        CheckConstraint("tipo in ('APERTURA', 'AJUSTE')", name="ck_movimiento_inventario_tipo"),
        CheckConstraint("length(trim(motivo)) > 0", name="ck_movimiento_inventario_motivo"),
        Index("ix_movimiento_inventario_lote_producto", "lote_producto_id"),
        Index("ix_movimiento_inventario_lote_ingrediente", "lote_ingrediente_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lote_ingrediente_id: Mapped[int | None] = mapped_column(ForeignKey("lote_ingrediente.id", ondelete="RESTRICT"))
    lote_producto_id: Mapped[int | None] = mapped_column(ForeignKey("lote_producto.id", ondelete="RESTRICT"))
    delta: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    saldo_resultante: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    tipo: Mapped[str] = mapped_column(String(12), nullable=False)
    clave_operacion: Mapped[str] = mapped_column(String(200), nullable=False)
    motivo: Mapped[str] = mapped_column(String(300), nullable=False)
    usuario_id: Mapped[int | None] = mapped_column(ForeignKey("usuario.id", ondelete="RESTRICT"))
    # Hora local simulada del escenario; distinta del instante UTC de auditoría.
    efectivo_en_demo: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
