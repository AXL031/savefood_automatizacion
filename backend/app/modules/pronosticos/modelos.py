"""Artefactos, corridas y evaluaciones reproducibles del prototipo."""

from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Index, Integer, JSON, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base

JsonPersistido = JSON().with_variant(JSONB, "postgresql")


class ArtefactoModelo(Base):
    __tablename__ = "artefacto_modelo"
    __table_args__ = (
        UniqueConstraint("version_modelo", name="uq_artefacto_modelo_version"),
        CheckConstraint("estado = 'LISTO_DEMO'", name="ck_artefacto_modelo_estado"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    version_modelo: Mapped[str] = mapped_column(String(80), nullable=False)
    ruta_local: Mapped[str] = mapped_column(String(160), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    huella_datos_entrenamiento: Mapped[str] = mapped_column(String(64), nullable=False)
    fecha_corte_entrenamiento: Mapped[date] = mapped_column(Date, nullable=False)
    particion_json: Mapped[dict] = mapped_column(JsonPersistido, nullable=False)
    estado: Mapped[str] = mapped_column(String(16), nullable=False)
    metricas_json: Mapped[dict | None] = mapped_column(JsonPersistido)
    entrenado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class CorridaPronostico(Base):
    __tablename__ = "corrida_pronostico"
    __table_args__ = (
        UniqueConstraint("clave_ejecucion", name="uq_corrida_pronostico_clave"),
        CheckConstraint("tipo IN ('BACKTEST', 'DEMO_PROGRAMADA')", name="ck_corrida_pronostico_tipo"),
        CheckConstraint("estado IN ('COMPLETADA', 'SIN_COBERTURA')", name="ck_corrida_pronostico_estado"),
        Index("ix_corrida_pronostico_fecha", "fecha_objetivo"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ejecucion_id: Mapped[int] = mapped_column(ForeignKey("ejecucion_automatizacion.id", ondelete="RESTRICT"), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False)
    clave_ejecucion: Mapped[str] = mapped_column(String(128), nullable=False)
    huella_datos_entrada: Mapped[str] = mapped_column(String(64), nullable=False)
    fecha_objetivo: Mapped[date] = mapped_column(Date, nullable=False)
    modelo_id: Mapped[int] = mapped_column(ForeignKey("artefacto_modelo.id", ondelete="RESTRICT"), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    finalizado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Pronostico(Base):
    __tablename__ = "pronostico"
    __table_args__ = (
        UniqueConstraint("corrida_id", "producto_id", name="uq_pronostico_corrida_producto"),
        CheckConstraint("estado IN ('DISPONIBLE', 'HISTORIAL_INSUFICIENTE', 'PRODUCTO_NO_CUBIERTO')", name="ck_pronostico_estado"),
        CheckConstraint("(estado = 'DISPONIBLE' AND cantidad_pronosticada >= 0) OR (estado != 'DISPONIBLE' AND cantidad_pronosticada IS NULL)", name="ck_pronostico_cantidad_estado"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    corrida_id: Mapped[int] = mapped_column(ForeignKey("corrida_pronostico.id", ondelete="RESTRICT"), nullable=False)
    producto_id: Mapped[int] = mapped_column(ForeignKey("producto.id", ondelete="RESTRICT"), nullable=False)
    cantidad_pronosticada: Mapped[int | None] = mapped_column(Integer)
    estado: Mapped[str] = mapped_column(String(32), nullable=False)


class EvaluacionPronostico(Base):
    __tablename__ = "evaluacion_pronostico"
    __table_args__ = (
        UniqueConstraint("corrida_id", "producto_id", "revision_venta_id", name="uq_evaluacion_pronostico_revision"),
        CheckConstraint("cantidad_pronosticada >= 0 AND unidades_reales >= 0 AND error_absoluto >= 0", name="ck_evaluacion_pronostico_cantidades"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ejecucion_id: Mapped[int] = mapped_column(ForeignKey("ejecucion_automatizacion.id", ondelete="RESTRICT"), nullable=False)
    corrida_id: Mapped[int] = mapped_column(ForeignKey("corrida_pronostico.id", ondelete="RESTRICT"), nullable=False)
    pronostico_id: Mapped[int] = mapped_column(ForeignKey("pronostico.id", ondelete="RESTRICT"), nullable=False)
    revision_venta_id: Mapped[int] = mapped_column(ForeignKey("revision_venta.id", ondelete="RESTRICT"), nullable=False)
    producto_id: Mapped[int] = mapped_column(ForeignKey("producto.id", ondelete="RESTRICT"), nullable=False)
    cantidad_pronosticada: Mapped[int] = mapped_column(Integer, nullable=False)
    unidades_reales: Mapped[int] = mapped_column(Integer, nullable=False)
    error_absoluto: Mapped[int] = mapped_column(Integer, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
