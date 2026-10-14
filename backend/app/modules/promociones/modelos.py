"""Reglas inmutables y evaluaciones trazables; ninguna publica descuentos."""
from datetime import datetime
from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, JSON, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base import Base


class ReglaPromocionDemo(Base):
    __tablename__ = "regla_promocion_demo"
    __table_args__ = (UniqueConstraint("version", name="uq_regla_promocion_version"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    parametros: Mapped[dict] = mapped_column(JSON, nullable=False)
    creado_por: Mapped[int] = mapped_column(ForeignKey("usuario.id", ondelete="RESTRICT"), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class EvaluacionPromocion(Base):
    __tablename__ = "evaluacion_promocion"
    __table_args__ = (
        UniqueConstraint("movimiento_id", name="uq_evaluacion_promocion_movimiento"),
        UniqueConstraint("ejecucion_id", name="uq_evaluacion_promocion_ejecucion"),
        CheckConstraint("descuento_pct IS NULL OR descuento_pct BETWEEN 1 AND 100", name="ck_evaluacion_promocion_descuento"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    regla_id: Mapped[int] = mapped_column(ForeignKey("regla_promocion_demo.id", ondelete="RESTRICT"), nullable=False)
    movimiento_id: Mapped[int] = mapped_column(ForeignKey("movimiento_inventario.id", ondelete="RESTRICT"), nullable=False)
    ejecucion_id: Mapped[int] = mapped_column(ForeignKey("ejecucion_automatizacion.id", ondelete="RESTRICT"), nullable=False)
    proponer: Mapped[bool] = mapped_column(Boolean, nullable=False)
    motivo: Mapped[str] = mapped_column(String(300), nullable=False)
    descuento_pct: Mapped[int | None] = mapped_column(Integer)
    lectura: Mapped[dict] = mapped_column(JSON, nullable=False)
    fecha_hora_simulada: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
