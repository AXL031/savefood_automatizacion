"""Estado durable de la primera inicialización de la instalación local.

Hay una sola fila (`id = 1`) porque el prototipo es una instalación, un comercio
y una sucursal. La fila recuerda qué archivos se aceptaron y en qué punto del
recorrido está el sistema, para que un fallo de entrenamiento **no** obligue a
volver a cargar ventas ni stock.
"""

from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.base import Base

FILA_UNICA = 1

ESTADO_PENDIENTE = "PENDIENTE"
ESTADO_DATOS_CARGADOS = "DATOS_CARGADOS"
ESTADO_ENTRENANDO = "ENTRENANDO"
ESTADO_MODELO_LISTO = "MODELO_LISTO"
ESTADO_FALLIDA = "FALLIDA"

ESTADOS = (
    ESTADO_PENDIENTE,
    ESTADO_DATOS_CARGADOS,
    ESTADO_ENTRENANDO,
    ESTADO_MODELO_LISTO,
    ESTADO_FALLIDA,
)


class ConfiguracionInicial(Base):
    __tablename__ = "configuracion_inicial"
    __table_args__ = (
        CheckConstraint(f"id = {FILA_UNICA}", name="ck_configuracion_inicial_fila_unica"),
        CheckConstraint(
            "estado in ('PENDIENTE', 'DATOS_CARGADOS', 'ENTRENANDO', 'MODELO_LISTO', 'FALLIDA')",
            name="ck_configuracion_inicial_estado",
        ),
        CheckConstraint(
            "fecha_referencia_stock is null or fecha_objetivo_demo is null "
            "or fecha_referencia_stock < fecha_objetivo_demo",
            name="ck_configuracion_inicial_fechas",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=False)
    estado: Mapped[str] = mapped_column(String(20), nullable=False, server_default=ESTADO_PENDIENTE)

    # Huellas de la entrega aceptada. Se guardan para reconocer un reintento
    # idéntico; los archivos no se vuelven a leer en cada plan.
    huella_ventas: Mapped[str | None] = mapped_column(String(64))
    huella_catalogo: Mapped[str | None] = mapped_column(String(64))
    huella_solicitud: Mapped[str | None] = mapped_column(String(64))
    preparacion_ejecucion_id: Mapped[int | None] = mapped_column(
        ForeignKey("ejecucion_automatizacion.id", ondelete="RESTRICT",
                   name="fk_inicializacion_preparacion"), nullable=True
    )

    # Fechas del escenario simulado, en hora local del comercio.
    fecha_objetivo_demo: Mapped[date | None] = mapped_column(Date)
    fecha_referencia_stock: Mapped[date | None] = mapped_column(Date)

    iniciada_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completada_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    mensaje_error: Mapped[str | None] = mapped_column(Text)

    actualizado_en: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
