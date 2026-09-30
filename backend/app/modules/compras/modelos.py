"""Snapshots de compra y reserva de fecha; nunca modifican inventario."""
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import BigInteger, Boolean, CheckConstraint, Date, DateTime, ForeignKey, Index, Integer, JSON, Numeric, String, Text, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base import Base

JsonPersistido = JSON(none_as_null=True).with_variant(JSONB(none_as_null=True), "postgresql")


class PropuestaCompra(Base):
    __tablename__ = "propuesta_compra"
    __table_args__ = (
        UniqueConstraint("plan_id", name="uq_propuesta_compra_plan"),
        Index("uq_propuesta_compra_fecha_activa", "fecha_objetivo", unique=True,
              sqlite_where=text("activa = 1"), postgresql_where=text("activa")),
        CheckConstraint("estado IN ('GENERADA','BLOQUEADA','SIN_FALTANTES','CANCELADA')", name="ck_propuesta_compra_estado"),
        CheckConstraint("(estado IN ('GENERADA','BLOQUEADA') AND activa) OR (estado IN ('SIN_FALTANTES','CANCELADA') AND NOT activa)", name="ck_propuesta_compra_activa"),
        CheckConstraint("modo_envio IN ('REQUIERE_APROBACION','AUTOMATICO')", name="ck_propuesta_compra_modo"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plan_produccion.id", ondelete="RESTRICT"), nullable=False)
    fecha_objetivo: Mapped[date] = mapped_column(Date, nullable=False)
    estado: Mapped[str] = mapped_column(String(24), nullable=False)
    activa: Mapped[bool] = mapped_column(Boolean, nullable=False)
    modo_envio: Mapped[str] = mapped_column(String(24), nullable=False)
    necesidades_json: Mapped[dict] = mapped_column(JsonPersistido, nullable=False)
    incidencias_json: Mapped[list] = mapped_column(JsonPersistido, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    cancelado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cancelado_por: Mapped[int | None] = mapped_column(ForeignKey("usuario.id", ondelete="RESTRICT"))
    motivo_cancelacion: Mapped[str | None] = mapped_column(String(500))


class PedidoCompra(Base):
    __tablename__ = "pedido_compra"
    __table_args__ = (
        UniqueConstraint("plan_id", "proveedor_id", name="uq_pedido_plan_proveedor"),
        CheckConstraint("estado IN ('BLOQUEADO','PENDIENTE_APROBACION','CANCELADO','RECHAZADO','PENDIENTE_ENVIO','ENVIANDO','ENVIADO','FALLIDO','PENDIENTE_VERIFICACION')", name="ck_pedido_compra_estado"),
        UniqueConstraint("clave_decision", name="uq_pedido_clave_decision"),
        CheckConstraint("(clave_decision IS NULL AND decidido_por IS NULL AND decidido_en IS NULL AND decision_json IS NULL) OR (clave_decision IS NOT NULL AND decidido_por IS NOT NULL AND decidido_en IS NOT NULL AND decision_json IS NOT NULL)", name="ck_pedido_decision_completa"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    propuesta_id: Mapped[int] = mapped_column(ForeignKey("propuesta_compra.id", ondelete="RESTRICT"), nullable=False)
    plan_id: Mapped[int] = mapped_column(ForeignKey("plan_produccion.id", ondelete="RESTRICT"), nullable=False)
    proveedor_id: Mapped[int] = mapped_column(ForeignKey("proveedor.id", ondelete="RESTRICT"), nullable=False)
    proveedor_json: Mapped[dict] = mapped_column(JsonPersistido, nullable=False)
    estado: Mapped[str] = mapped_column(String(24), nullable=False)
    modo_envio: Mapped[str] = mapped_column(String(24), nullable=False)
    bloqueos_json: Mapped[list] = mapped_column(JsonPersistido, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    clave_decision: Mapped[str | None] = mapped_column(String(80))
    decidido_por: Mapped[int | None] = mapped_column(ForeignKey("usuario.id", ondelete="RESTRICT"))
    decidido_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    decision_json: Mapped[dict | None] = mapped_column(JsonPersistido)


class EnvioPedido(Base):
    __tablename__ = "envio_pedido"
    __table_args__ = (
        UniqueConstraint("pedido_id", name="uq_envio_pedido_unico"),
        CheckConstraint("numero_intento = 1", name="ck_envio_numero"),
        CheckConstraint("estado IN ('PENDIENTE_ENVIO','ENVIANDO','ENVIADO','FALLIDO','PENDIENTE_VERIFICACION')", name="ck_envio_estado"),
        CheckConstraint("(estado = 'ENVIADO' AND message_id IS NOT NULL AND message_id > 0 AND fin_en IS NOT NULL) OR (estado <> 'ENVIADO' AND message_id IS NULL)", name="ck_envio_confirmacion"),
        Index("ix_envio_pendiente", "estado", "lease_hasta"),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedido_compra.id", ondelete="RESTRICT"), nullable=False)
    numero_intento: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default="1")
    estado: Mapped[str] = mapped_column(String(24), nullable=False)
    chat_id: Mapped[str] = mapped_column(String(64), nullable=False)
    credencial_huella: Mapped[str] = mapped_column(String(64), nullable=False)
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    inicio_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    fin_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    fecha_telegram: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    message_id: Mapped[int | None] = mapped_column(BigInteger)
    codigo_error: Mapped[str | None] = mapped_column(String(64))
    detalle_error: Mapped[str | None] = mapped_column(String(500))
    despachado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    lease_hasta: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    token_despacho: Mapped[str | None] = mapped_column(String(36))


class LineaPedido(Base):
    __tablename__ = "linea_pedido"
    __table_args__ = (
        UniqueConstraint("necesidad_ingrediente_id", name="uq_linea_pedido_necesidad"),
        CheckConstraint("faltante_base > 0 AND cantidad_compra > 0 AND cantidad_base_pedida >= faltante_base", name="ck_linea_pedido_cantidades"),
    )
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    pedido_id: Mapped[int] = mapped_column(ForeignKey("pedido_compra.id", ondelete="RESTRICT"), nullable=False)
    necesidad_ingrediente_id: Mapped[int] = mapped_column(ForeignKey("necesidad_ingrediente.id", ondelete="RESTRICT"), nullable=False)
    oferta_ingrediente_id: Mapped[int] = mapped_column(ForeignKey("oferta_ingrediente.id", ondelete="RESTRICT"), nullable=False)
    ingrediente_id: Mapped[int] = mapped_column(ForeignKey("ingrediente.id", ondelete="RESTRICT"), nullable=False)
    faltante_base: Mapped[Decimal] = mapped_column(Numeric(14, 3), nullable=False)
    cantidad_compra: Mapped[Decimal] = mapped_column(Numeric(20, 4), nullable=False)
    cantidad_base_pedida: Mapped[Decimal] = mapped_column(Numeric(30, 8), nullable=False)
    unidad_base: Mapped[str] = mapped_column(String(16), nullable=False)
    unidad_compra: Mapped[str] = mapped_column(String(30), nullable=False)
    oferta_json: Mapped[dict] = mapped_column(JsonPersistido, nullable=False)
    ingrediente_json: Mapped[dict] = mapped_column(JsonPersistido, nullable=False)
