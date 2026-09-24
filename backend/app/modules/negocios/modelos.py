from datetime import datetime, time, timezone

from sqlalchemy import CheckConstraint, DateTime, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base


class Negocio(Base):
    __tablename__ = "negocio"
    __table_args__ = (
        CheckConstraint("id = 1", name="ck_negocio_unico"),
        CheckConstraint("char_length(moneda) = 3", name="ck_negocio_moneda"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(160))
    zona_horaria: Mapped[str] = mapped_column(String(80))
    moneda: Mapped[str] = mapped_column(String(3))
    hora_apertura: Mapped[time | None] = mapped_column(Time, nullable=True)
    hora_cierre: Mapped[time | None] = mapped_column(Time, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    actualizado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
