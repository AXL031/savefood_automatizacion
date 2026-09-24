from datetime import datetime, timezone

from sqlalchemy import Boolean, CheckConstraint, DateTime, Index, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base


class Usuario(Base):
    __tablename__ = "usuario"
    __table_args__ = (CheckConstraint("rol IN ('ADMINISTRADOR', 'OPERADOR')", name="ck_usuario_rol"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    correo: Mapped[str] = mapped_column(String(254))
    hash_contrasena: Mapped[str] = mapped_column(String(512))
    nombre: Mapped[str] = mapped_column(String(160))
    rol: Mapped[str] = mapped_column(String(20))
    activo: Mapped[bool] = mapped_column(Boolean, default=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    actualizado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))


Index("uq_usuario_correo_normalizado", func.lower(Usuario.correo), unique=True)
