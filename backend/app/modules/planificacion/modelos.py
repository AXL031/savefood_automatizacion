"""M02: propuesta inmutable, con lecturas conservadas; nunca mueve stock."""
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, Integer, JSON, Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base

JsonPersistido = JSON().with_variant(JSONB, "postgresql")


class PlanProduccion(Base):
    __tablename__ = "plan_produccion"
    __table_args__ = (
        UniqueConstraint("clave_ejecucion", name="uq_plan_produccion_clave"),
        CheckConstraint("estado = 'PROPUESTO'", name="ck_plan_produccion_estado"),
        Index("ix_plan_produccion_corrida", "corrida_id"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    corrida_id: Mapped[int] = mapped_column(ForeignKey("corrida_pronostico.id", ondelete="RESTRICT"), nullable=False)
    ejecucion_id: Mapped[int] = mapped_column(ForeignKey("ejecucion_automatizacion.id", ondelete="RESTRICT"), nullable=False)
    clave_ejecucion: Mapped[str] = mapped_column(String(128), nullable=False)
    huella_stock_recetas: Mapped[str] = mapped_column(String(64), nullable=False)
    fecha_objetivo: Mapped[date] = mapped_column(Date, nullable=False)
    stock_leido_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    estado: Mapped[str] = mapped_column(String(16), nullable=False)
    version_calculo: Mapped[str] = mapped_column(String(16), nullable=False)
    origen_pronostico_json: Mapped[dict] = mapped_column(JsonPersistido, nullable=False)
    necesidades_estado: Mapped[str] = mapped_column(String(24), nullable=False, server_default="PENDIENTE_M03")
    necesidades_meta_json: Mapped[dict | None] = mapped_column(JsonPersistido)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class ElementoPlan(Base):
    __tablename__ = "elemento_plan"
    __table_args__ = (
        UniqueConstraint("plan_id", "producto_id", name="uq_elemento_plan_producto"),
        CheckConstraint("estado IN ('CALCULADO', 'HISTORIAL_INSUFICIENTE', 'PRODUCTO_NO_CUBIERTO', 'SIN_RECETA', 'STOCK_DESCONOCIDO')", name="ck_elemento_plan_estado"),
        CheckConstraint("cantidad_pronosticada IS NULL OR cantidad_pronosticada >= 0", name="ck_elemento_plan_pronostico"),
        CheckConstraint("stock_disponible IS NULL OR stock_disponible >= 0", name="ck_elemento_plan_stock"),
        CheckConstraint("(estado = 'CALCULADO' AND cantidad_producir IS NOT NULL AND cantidad_producir >= 0 AND cantidad_pronosticada IS NOT NULL AND stock_disponible IS NOT NULL AND receta_id IS NOT NULL) OR (estado != 'CALCULADO' AND cantidad_producir IS NULL)", name="ck_elemento_plan_calculo"),
        CheckConstraint("estado != 'CALCULADO' OR cantidad_producir = CASE WHEN cantidad_pronosticada > stock_disponible THEN cantidad_pronosticada - stock_disponible ELSE 0 END", name="ck_elemento_plan_formula"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plan_produccion.id", ondelete="RESTRICT"), nullable=False)
    producto_id: Mapped[int] = mapped_column(ForeignKey("producto.id", ondelete="RESTRICT"), nullable=False)
    pronostico_id: Mapped[int] = mapped_column(ForeignKey("pronostico.id", ondelete="RESTRICT"), nullable=False)
    receta_id: Mapped[int | None] = mapped_column(ForeignKey("receta.id", ondelete="RESTRICT"))
    cantidad_pronosticada: Mapped[int | None] = mapped_column(Integer)
    stock_disponible: Mapped[int | None] = mapped_column(Integer)
    cantidad_producir: Mapped[int | None] = mapped_column(Integer)
    estado: Mapped[str] = mapped_column(String(32), nullable=False)
    receta_json: Mapped[dict | None] = mapped_column(JsonPersistido)
    stock_json: Mapped[dict] = mapped_column(JsonPersistido, nullable=False)
    avisos_json: Mapped[list] = mapped_column(JsonPersistido, nullable=False)


class NecesidadIngrediente(Base):
    __tablename__ = "necesidad_ingrediente"
    __table_args__ = (
        UniqueConstraint("plan_id", "ingrediente_id", name="uq_necesidad_plan_ingrediente"),
        CheckConstraint("cantidad_necesaria >= 0", name="ck_necesidad_cantidad"),
        CheckConstraint("(estado = 'DISPONIBLE' AND stock_disponible IS NOT NULL AND stock_disponible >= 0 AND faltante IS NOT NULL AND faltante >= 0) OR (estado = 'STOCK_DESCONOCIDO' AND stock_disponible IS NULL AND faltante IS NULL)", name="ck_necesidad_estado"),
        CheckConstraint("faltante IS NULL OR faltante = CASE WHEN cantidad_necesaria > stock_disponible THEN cantidad_necesaria - stock_disponible ELSE 0 END", name="ck_necesidad_formula"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plan_produccion.id", ondelete="RESTRICT"), nullable=False)
    ingrediente_id: Mapped[int] = mapped_column(ForeignKey("ingrediente.id", ondelete="RESTRICT"), nullable=False)
    unidad_base: Mapped[str] = mapped_column(String(16), nullable=False)
    cantidad_necesaria: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    stock_disponible: Mapped[Decimal | None] = mapped_column(Numeric(14, 3))
    faltante: Mapped[Decimal | None] = mapped_column(Numeric(14, 3))
    estado: Mapped[str] = mapped_column(String(24), nullable=False)
    aportes_json: Mapped[list] = mapped_column(JsonPersistido, nullable=False)
    stock_json: Mapped[dict] = mapped_column(JsonPersistido, nullable=False)
