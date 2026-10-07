"""M02/M03: propuestas inmutables; nunca reservan ni descuentan inventario."""

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, CheckConstraint, Date, DateTime, ForeignKey, Integer, JSON, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base


class PlanProduccion(Base):
    __tablename__ = "plan_produccion"
    __table_args__ = (UniqueConstraint("clave_ejecucion", name="uq_plan_clave"),
                      CheckConstraint("estado = 'PROPUESTO'", name="ck_plan_estado"))

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    corrida_id: Mapped[int] = mapped_column(ForeignKey("corrida_pronostico.id", ondelete="RESTRICT"), nullable=False, index=True)
    ejecucion_id: Mapped[int] = mapped_column(ForeignKey("ejecucion_automatizacion.id", ondelete="RESTRICT"), nullable=False)
    clave_ejecucion: Mapped[str] = mapped_column(String(128), nullable=False)
    huella_stock_recetas: Mapped[str] = mapped_column(String(64), nullable=False)
    fecha_objetivo: Mapped[date] = mapped_column(Date, nullable=False)
    stock_leido_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, default="PROPUESTO")
    trazas_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class ElementoPlan(Base):
    __tablename__ = "elemento_plan"
    __table_args__ = (UniqueConstraint("plan_id", "producto_id", name="uq_elemento_plan_producto"),
                      CheckConstraint("cantidad_pronosticada >= 0 AND stock_disponible >= 0 AND cantidad_producir >= 0", name="ck_elemento_plan_cantidades"))

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plan_produccion.id", ondelete="RESTRICT"), nullable=False)
    producto_id: Mapped[int] = mapped_column(ForeignKey("producto.id", ondelete="RESTRICT"), nullable=False)
    pronostico_id: Mapped[int] = mapped_column(ForeignKey("pronostico.id", ondelete="RESTRICT"), nullable=False)
    receta_id: Mapped[int] = mapped_column(ForeignKey("receta.id", ondelete="RESTRICT"), nullable=False)
    cantidad_pronosticada: Mapped[int] = mapped_column(Integer, nullable=False)
    stock_disponible: Mapped[int] = mapped_column(Integer, nullable=False)
    cantidad_producir: Mapped[int] = mapped_column(Integer, nullable=False)
    vigencia_stock_desconocida: Mapped[bool] = mapped_column(Boolean, nullable=False)


class NecesidadIngrediente(Base):
    __tablename__ = "necesidad_ingrediente"
    __table_args__ = (UniqueConstraint("plan_id", "ingrediente_id", name="uq_necesidad_plan_ingrediente"),
                      CheckConstraint("cantidad_requerida >= 0", name="ck_necesidad_requerida"),
                      CheckConstraint("(stock_conocido AND cantidad_disponible IS NOT NULL AND cantidad_faltante IS NOT NULL AND cantidad_disponible >= 0 AND cantidad_faltante >= 0) OR (NOT stock_conocido AND cantidad_disponible IS NULL AND cantidad_faltante IS NULL)", name="ck_necesidad_stock"))

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plan_produccion.id", ondelete="RESTRICT"), nullable=False)
    ingrediente_id: Mapped[int] = mapped_column(ForeignKey("ingrediente.id", ondelete="RESTRICT"), nullable=False)
    cantidad_requerida: Mapped[Decimal] = mapped_column(Numeric(18, 3), nullable=False)
    cantidad_disponible: Mapped[Decimal | None] = mapped_column(Numeric(18, 3))
    cantidad_faltante: Mapped[Decimal | None] = mapped_column(Numeric(18, 3))
    unidad: Mapped[str] = mapped_column(String(20), nullable=False)
    stock_conocido: Mapped[bool] = mapped_column(Boolean, nullable=False)
    vigencia_stock_desconocida: Mapped[bool] = mapped_column(Boolean, nullable=False)
