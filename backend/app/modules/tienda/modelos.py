"""Clientes de la tienda. Separados de `usuario`: no tienen rol ni acceso administrativo."""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base


class ClienteTienda(Base):
    __tablename__ = "cliente"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Identificador estable de Google (claim `sub`); el correo puede cambiar.
    google_sub: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    correo: Mapped[str] = mapped_column(String(254), nullable=False)
    nombre: Mapped[str] = mapped_column(String(160), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    ultimo_acceso_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
