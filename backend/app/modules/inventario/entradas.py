"""Entradas explícitas de producto terminado. Una transacción del consumidor."""
import hashlib
import json
import re
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Annotated
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from sqlalchemy import select, text

from app.core.errores import ErrorAPI
from app.modules.negocios.servicio import zona_horaria_negocio
from app.modules.productos.servicio import catalogo_para_ventas
from .modelos import EntradaProductos, LineaEntradaProductos, LoteProducto
from .servicio import _aplicar
from .vigencia import VIDA_MAXIMA_PRODUCTO_DIAS


def ahora():
    return datetime.now(timezone.utc)


class Estricta(BaseModel):
    model_config = ConfigDict(extra="forbid")


class LineaCrear(Estricta):
    producto_id: Annotated[int, Field(gt=0, strict=True)]
    codigo_lote: str = Field(min_length=1, max_length=80)
    cantidad: Annotated[int, Field(ge=1, le=1000000, strict=True)]
    fecha_elaboracion: date
    fecha_caducidad: date
    fecha_limite_venta: date

    @field_validator("codigo_lote")
    @classmethod
    def limpiar_lote(cls, v):
        if not v.strip():
            raise ValueError("Indica el código del lote.")
        return v.strip()

    @field_validator("fecha_elaboracion", "fecha_caducidad", "fecha_limite_venta", mode="before")
    @classmethod
    def fecha_iso(cls, v):
        if type(v) is not date and (not isinstance(v, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", v)):
            raise ValueError("Usa una fecha YYYY-MM-DD.")
        return v

    @model_validator(mode="after")
    def fechas(self):
        if not self.fecha_elaboracion <= self.fecha_limite_venta <= self.fecha_caducidad:
            raise ValueError("Elaboración, límite de venta y caducidad deben estar en ese orden.")
        if (self.fecha_caducidad - self.fecha_elaboracion).days >= VIDA_MAXIMA_PRODUCTO_DIAS:
            raise ValueError(f"La vida máxima del producto es {VIDA_MAXIMA_PRODUCTO_DIAS} días, contando elaboración.")
        return self


class EntradaCrear(Estricta):
    clave_operacion: str = Field(min_length=8, max_length=80, pattern=r"^[A-Za-z0-9._:-]+$")
    fecha_entrada: date
    motivo: str = Field(min_length=3, max_length=300)
    lineas: list[LineaCrear] = Field(min_length=1, max_length=100)

    _fecha_iso = field_validator("fecha_entrada", mode="before")(LineaCrear.fecha_iso.__func__)

    @field_validator("motivo")
    @classmethod
    def limpiar_motivo(cls, v):
        if len(v.strip()) < 3:
            raise ValueError("Escribe un motivo de al menos tres caracteres.")
        return v.strip()

    @model_validator(mode="after")
    def comprobar_lineas(self):
        pares = [(l.producto_id, l.codigo_lote) for l in self.lineas]
        if len(pares) != len(set(pares)):
            raise ValueError("No repitas el mismo lote de un producto en la entrada.")
        for l in self.lineas:
            if not l.fecha_elaboracion <= self.fecha_entrada <= l.fecha_limite_venta:
                raise ValueError("La entrada debe estar entre elaboración y límite de venta de cada lote.")
        self.lineas.sort(key=lambda l: (l.producto_id, l.codigo_lote))
        return self


def contexto(s):
    zona = zona_horaria_negocio(s)
    return {"fecha_actual": ahora().astimezone(ZoneInfo(zona)).date().isoformat(), "zona_horaria": zona,
            "vida_maxima_dias": VIDA_MAXIMA_PRODUCTO_DIAS,
            "productos": [p for p in catalogo_para_ventas(s) if p["activo"]]}


def registrar(s, datos: EntradaCrear, usuario):
    h = hashlib.sha256(json.dumps(datos.model_dump(mode="json", exclude={"clave_operacion"}), sort_keys=True).encode()).hexdigest()
    if s.get_bind().dialect.name == "postgresql":
        lock = int.from_bytes(hashlib.sha256(f"entrada-productos:{usuario.id}:{datos.clave_operacion}".encode()).digest()[:8], signed=True)
        s.execute(text("SELECT pg_advisory_xact_lock(:clave)"), {"clave": lock})
    anterior = s.scalar(select(EntradaProductos).where(EntradaProductos.usuario_id == usuario.id, EntradaProductos.clave == datos.clave_operacion))
    if anterior:
        if anterior.huella != h:
            raise ErrorAPI(409, "CLAVE_REUTILIZADA", "Esta clave corresponde a otra entrada. Revisa la original.")
        return anterior, True
    instante = ahora()
    local = instante.astimezone(ZoneInfo(zona_horaria_negocio(s)))
    if datos.fecha_entrada > local.date():
        raise ErrorAPI(422, "ENTRADA_FUTURA", "No puedes registrar una entrada con fecha futura.")
    ids = sorted({l.producto_id for l in datos.lineas})
    productos = {p["id"]: p for p in catalogo_para_ventas(s, ids, bloquear=True)}
    existentes = {(l.producto_id, l.codigo_lote) for l in s.scalars(select(LoteProducto).where(LoteProducto.producto_id.in_(ids)))}
    for l in datos.lineas:
        if l.producto_id not in productos or not productos[l.producto_id]["activo"]:
            raise ErrorAPI(409, "PRODUCTO_NO_DISPONIBLE", f"Producto #{l.producto_id} inexistente o inactivo.")
        if (l.producto_id, l.codigo_lote) in existentes:
            raise ErrorAPI(409, "LOTE_EXISTENTE", f"El lote {l.codigo_lote} de {productos[l.producto_id]['nombre']} ya existe. Usa otro código o registra un ajuste.")
    entrada = EntradaProductos(usuario_id=usuario.id, nombre_usuario=usuario.nombre, clave=datos.clave_operacion,
                                huella=h, fecha_entrada=datos.fecha_entrada, motivo=datos.motivo, creado_en=instante)
    s.add(entrada); s.flush()
    for n, l in enumerate(datos.lineas, 1):
        lote = LoteProducto(producto_id=l.producto_id, codigo_lote=l.codigo_lote, lote_informado=True,
            fecha_ingreso=datos.fecha_entrada, fecha_caducidad=l.fecha_caducidad,
            fecha_limite_venta=l.fecha_limite_venta, saldo_disponible=0)
        s.add(lote); s.flush()
        mov = _aplicar(s, tipo="producto", lote=lote, delta=Decimal(l.cantidad), tipo_movimiento="ENTRADA",
                       clave=f"entrada-productos-{entrada.id}-{n}", motivo=f"Entrada #{entrada.id}: {datos.motivo}"[:300],
                       efectivo_en_demo=datetime.combine(datos.fecha_entrada, local.time()), usuario_id=usuario.id)
        s.add(LineaEntradaProductos(entrada_id=entrada.id, producto_id=l.producto_id, lote_id=lote.id,
            movimiento_id=mov.movimiento_id, codigo_producto=productos[l.producto_id]["codigo"],
            nombre_producto=productos[l.producto_id]["nombre"], **l.model_dump(exclude={"producto_id"})))
    s.flush()
    return entrada, False


def detalle(s, id_):
    e = s.get(EntradaProductos, id_)
    if not e:
        raise ErrorAPI(404, "ENTRADA_NO_ENCONTRADA", "La entrada no existe.")
    return {**resumen(e), "lineas": [{"id": l.id, "producto_id": l.producto_id, "codigo_producto": l.codigo_producto,
        "nombre_producto": l.nombre_producto, "codigo_lote": l.codigo_lote, "lote_id": l.lote_id,
        "movimiento_id": l.movimiento_id, "cantidad": l.cantidad, "fecha_elaboracion": l.fecha_elaboracion.isoformat(),
        "fecha_caducidad": l.fecha_caducidad.isoformat(), "fecha_limite_venta": l.fecha_limite_venta.isoformat()}
        for l in s.scalars(select(LineaEntradaProductos).where(LineaEntradaProductos.entrada_id == id_).order_by(LineaEntradaProductos.id))]}


def resumen(e):
    return {"id": e.id, "numero": f"E-{e.id:08d}", "fecha_entrada": e.fecha_entrada.isoformat(),
            "motivo": e.motivo, "usuario_id": e.usuario_id, "nombre_usuario": e.nombre_usuario,
            "creado_en": e.creado_en.replace(tzinfo=timezone.utc).isoformat() if e.creado_en.tzinfo is None else e.creado_en.isoformat()}
