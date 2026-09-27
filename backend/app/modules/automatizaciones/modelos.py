"""Programaciones y trazas durables del motor de demostración."""

from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base

JsonPersistido = JSON().with_variant(JSONB, "postgresql")


class ProgramacionDemo(Base):
    __tablename__ = "programacion_demo"
    __table_args__ = (
        UniqueConstraint("clave_idempotencia", name="uq_programacion_demo_clave"),
        CheckConstraint("tipo IN ('GENERAR_PROPUESTA', 'EVALUAR_PROMOCION')", name="ck_programacion_demo_tipo"),
        CheckConstraint("estado IN ('PROGRAMADA', 'DESPACHADA', 'CANCELADA')", name="ck_programacion_demo_estado"),
        Index("ix_programacion_demo_vencimientos", "estado", "ejecutar_desde_utc"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    tipo: Mapped[str] = mapped_column(String(32), nullable=False)
    ejecutar_desde_utc: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fecha_hora_simulada_local: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    parametros_json: Mapped[dict] = mapped_column(JsonPersistido, nullable=False)
    clave_idempotencia: Mapped[str] = mapped_column(String(128), nullable=False)
    huella_entrada: Mapped[str] = mapped_column(String(64), nullable=False)
    estado: Mapped[str] = mapped_column(String(16), nullable=False, default="PROGRAMADA", server_default="PROGRAMADA")
    despachada_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    lease_hasta: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    creado_por: Mapped[int | None] = mapped_column(ForeignKey("usuario.id", ondelete="RESTRICT"))
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())


class EjecucionAutomatizacion(Base):
    __tablename__ = "ejecucion_automatizacion"
    __table_args__ = (
        UniqueConstraint("clave_idempotencia", name="uq_ejecucion_automatizacion_clave"),
        UniqueConstraint("programacion_id", name="uq_ejecucion_automatizacion_programacion"),
        CheckConstraint(
            "tipo IN ('PREPARAR_MODELO', 'EVALUAR_MODELO', 'GENERAR_PROPUESTA', 'EVALUAR_PRONOSTICO', 'EVALUAR_PROMOCION')",
            name="ck_ejecucion_automatizacion_tipo",
        ),
        CheckConstraint(
            "estado IN ('PENDIENTE', 'EN_EJECUCION', 'REINTENTANDO', 'COMPLETADA', 'FALLIDA')",
            name="ck_ejecucion_automatizacion_estado",
        ),
        Index("ix_ejecucion_automatizacion_estado", "estado"),
        Index("ix_ejecucion_automatizacion_lease", "estado", "lease_hasta"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    programacion_id: Mapped[int | None] = mapped_column(ForeignKey("programacion_demo.id", ondelete="RESTRICT"))
    tipo: Mapped[str] = mapped_column(String(32), nullable=False)
    clave_idempotencia: Mapped[str] = mapped_column(String(128), nullable=False)
    huella_entrada: Mapped[str] = mapped_column(String(64), nullable=False)
    datos_entrada_json: Mapped[dict] = mapped_column(JsonPersistido, nullable=False)
    estado: Mapped[str] = mapped_column(String(16), nullable=False, default="PENDIENTE", server_default="PENDIENTE")
    inicio_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    fin_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    proximo_intento_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    despachada_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    lease_hasta: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    token_despacho: Mapped[str | None] = mapped_column(String(36))
    datos_salida_json: Mapped[dict | None] = mapped_column(JsonPersistido)
    mensaje_error: Mapped[str | None] = mapped_column(Text)


class IntentoAutomatizacion(Base):
    __tablename__ = "intento_automatizacion"
    __table_args__ = (
        UniqueConstraint("ejecucion_id", "numero_intento", name="uq_intento_automatizacion_numero"),
        CheckConstraint("numero_intento BETWEEN 1 AND 3", name="ck_intento_automatizacion_numero"),
        CheckConstraint("estado IN ('EN_EJECUCION', 'COMPLETADA', 'FALLIDA')", name="ck_intento_automatizacion_estado"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ejecucion_id: Mapped[int] = mapped_column(ForeignKey("ejecucion_automatizacion.id", ondelete="RESTRICT"), nullable=False)
    numero_intento: Mapped[int] = mapped_column(Integer, nullable=False)
    inicio_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    fin_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    estado: Mapped[str] = mapped_column(String(16), nullable=False)
    mensaje_error: Mapped[str | None] = mapped_column(Text)
