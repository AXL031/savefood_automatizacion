"""Interfaz pública del inventario por lotes (V01 apertura, V02 ajustes y disponibilidad).

Reglas comunes a apertura y ajuste:

- El lote se bloquea (`SELECT ... FOR UPDATE`) antes de leer su saldo.
- Movimiento y saldo se escriben juntos; ninguna función confirma: el llamador
  (ruta HTTP o importador de Edu) hace commit o rollback.
- `clave_operacion` es única. La misma clave con los mismos parámetros devuelve
  el movimiento existente sin tocar el saldo; con otros parámetros es
  `409 CLAVE_REUTILIZADA`.
- El saldo final nunca queda negativo.

La disponibilidad por fecha solo lee: aplica las reglas de `vigencia.py` y no
modifica saldos.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import date, datetime, time, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errores import ErrorAPI
from app.modules.ingredientes import servicio as ingredientes
from app.modules.inventario import vigencia as reglas
from app.modules.inventario.modelos import (
    TIPO_AJUSTE,
    TIPO_APERTURA,
    LoteIngrediente,
    LoteProducto,
    MovimientoInventario,
)
from app.modules.productos.modelos import Producto

PRODUCTO = "producto"
INGREDIENTE = "ingrediente"
TIPOS_ITEM = (PRODUCTO, INGREDIENTE)
UNIDAD_PRODUCTO = "unidad"

_CUANTO = Decimal("0.001")
# La apertura representa el cierre del día de referencia del stock.
HORA_CIERRE_APERTURA = time(23, 59)


# --- Utilidades ------------------------------------------------------------------


def _modelo(tipo: str):
    if tipo == PRODUCTO:
        return LoteProducto
    if tipo == INGREDIENTE:
        return LoteIngrediente
    raise ErrorAPI(422, "TIPO_INVALIDO", f"El tipo debe ser 'producto' o 'ingrediente'; llegó {tipo!r}.")


def _cantidad(tipo: str, valor: Decimal, contexto: str, permitir_cero: bool = False) -> Decimal:
    if not isinstance(valor, Decimal):
        valor = Decimal(str(valor))
    if not valor.is_finite():
        raise ErrorAPI(422, "CANTIDAD_INVALIDA", f"{contexto}: cantidad inválida.")
    if valor == 0 and not permitir_cero:
        raise ErrorAPI(422, "CANTIDAD_INVALIDA", f"{contexto}: el ajuste no puede ser cero.")
    if abs(valor) >= Decimal("100000000000"):
        raise ErrorAPI(422, "CANTIDAD_INVALIDA", f"{contexto}: la cantidad es demasiado grande.")
    if tipo == PRODUCTO and valor != valor.to_integral_value():
        raise ErrorAPI(422, "CANTIDAD_INVALIDA", f"{contexto}: el producto terminado se cuenta en unidades enteras.")
    if tipo == INGREDIENTE and -valor.as_tuple().exponent > 3:
        raise ErrorAPI(422, "CANTIDAD_INVALIDA", f"{contexto}: se admiten hasta 3 decimales en la unidad base.")
    return valor.quantize(Decimal(1) if tipo == PRODUCTO else _CUANTO, rounding=ROUND_HALF_UP)


def _saldo(tipo: str, lote) -> Decimal:
    valor = Decimal(lote.saldo_disponible)
    return valor.quantize(Decimal(1) if tipo == PRODUCTO else _CUANTO)


def _fijar_saldo(tipo: str, lote, saldo: Decimal) -> None:
    lote.saldo_disponible = int(saldo) if tipo == PRODUCTO else saldo
    lote.actualizado_en = datetime.now(timezone.utc)


def _tipo_de_movimiento(movimiento: MovimientoInventario) -> tuple[str, int]:
    if movimiento.lote_producto_id is not None:
        return PRODUCTO, movimiento.lote_producto_id
    return INGREDIENTE, movimiento.lote_ingrediente_id


def _bloquear_lote(sesion: Session, tipo: str, lote_id: int):
    modelo = _modelo(tipo)
    lote = sesion.scalar(select(modelo).where(modelo.id == lote_id).with_for_update())
    if lote is None:
        raise ErrorAPI(404, "LOTE_NO_ENCONTRADO", f"No existe el lote de {tipo} {lote_id}.")
    return lote


def _movimiento_por_clave(sesion: Session, clave: str) -> MovimientoInventario | None:
    return sesion.scalar(select(MovimientoInventario).where(MovimientoInventario.clave_operacion == clave))


@dataclass(frozen=True)
class ResultadoMovimiento:
    movimiento_id: int
    tipo_item: str
    lote_id: int
    tipo_movimiento: str
    delta: Decimal
    saldo_resultante: Decimal
    efectivo_en_demo: datetime
    repetido: bool


def _resultado(movimiento: MovimientoInventario, repetido: bool) -> ResultadoMovimiento:
    tipo, lote_id = _tipo_de_movimiento(movimiento)
    cuanto = Decimal(1) if tipo == PRODUCTO else _CUANTO
    return ResultadoMovimiento(
        movimiento_id=movimiento.id,
        tipo_item=tipo,
        lote_id=lote_id,
        tipo_movimiento=movimiento.tipo,
        delta=Decimal(movimiento.delta).quantize(cuanto),
        saldo_resultante=Decimal(movimiento.saldo_resultante).quantize(cuanto),
        efectivo_en_demo=movimiento.efectivo_en_demo,
        repetido=repetido,
    )


def _aplicar(
    sesion: Session,
    *,
    tipo: str,
    lote,
    delta: Decimal,
    tipo_movimiento: str,
    clave: str,
    motivo: str,
    efectivo_en_demo: datetime,
    usuario_id: int | None,
) -> ResultadoMovimiento:
    """Núcleo común: el lote ya está bloqueado por el llamador."""
    existente = _movimiento_por_clave(sesion, clave)
    if existente is not None:
        tipo_existente, lote_existente = _tipo_de_movimiento(existente)
        mismo = (
            tipo_existente == tipo
            and lote_existente == lote.id
            and existente.tipo == tipo_movimiento
            and Decimal(existente.delta) == delta
        )
        if not mismo:
            raise ErrorAPI(
                409,
                "CLAVE_REUTILIZADA",
                "La clave de operación ya se usó con otro lote, cantidad o tipo de movimiento.",
            )
        return _resultado(existente, repetido=True)

    saldo_final = _saldo(tipo, lote) + delta
    if saldo_final < 0:
        raise ErrorAPI(
            409,
            "SALDO_INSUFICIENTE",
            f"El lote {lote.codigo_lote!r} tiene {_saldo(tipo, lote)}; restar {abs(delta)} lo dejaría negativo.",
        )
    movimiento = MovimientoInventario(
        lote_producto_id=lote.id if tipo == PRODUCTO else None,
        lote_ingrediente_id=lote.id if tipo == INGREDIENTE else None,
        delta=delta,
        saldo_resultante=saldo_final,
        tipo=tipo_movimiento,
        clave_operacion=clave,
        motivo=motivo,
        usuario_id=usuario_id,
        efectivo_en_demo=efectivo_en_demo,
    )
    sesion.add(movimiento)
    _fijar_saldo(tipo, lote, saldo_final)
    sesion.flush()
    return _resultado(movimiento, repetido=False)


# --- V01: apertura en la sesión de la primera carga ------------------------------


def _codigo_lote(tipo: str, codigo: str, codigo_lote: str | None) -> tuple[str, bool]:
    if codigo_lote:
        if len(codigo_lote) > 80:
            raise ErrorAPI(422, "LOTE_INVALIDO", f"El código de lote de {codigo!r} supera 80 caracteres.")
        return codigo_lote, True
    # Código técnico estable: el mismo archivo produce el mismo lote al reintentar.
    return "SIN-LOTE-" + hashlib.sha256(f"{tipo}|{codigo}".encode("utf-8")).hexdigest()[:12].upper(), False


def _clave_apertura(base: str, tipo: str, codigo: str, codigo_lote: str) -> str:
    huella = hashlib.sha256(f"{tipo}|{codigo}|{codigo_lote}".encode("utf-8")).hexdigest()[:16]
    return f"{base[:150]}-{huella}"


class ServicioInventarioV01:
    """Implementación del puerto `ServicioInventario` de la primera carga."""

    def registrar_apertura(
        self,
        sesion: Session,
        filas,
        producto_por_codigo: dict[str, int],
        ingrediente_por_codigo: dict[str, int],
        efectivo_en_demo: date,
        clave_operacion_base: str,
    ) -> int:
        """Crea lotes y movimientos `APERTURA`. No confirma.

        - Cantidad explícita `0`: lote con saldo cero y **sin** movimiento.
        - Cantidad positiva: un único movimiento `APERTURA` con clave derivada
          de la base, el ítem y el lote; reintentar no vuelve a sumar.
        - Producto con caducidad más allá de la vida máxima (5 días) desde la
          fecha de referencia se rechaza: no puede existir ese lote.
        Devuelve cuántos movimientos nuevos insertó.
        """
        if not clave_operacion_base or not clave_operacion_base.strip():
            raise ErrorAPI(422, "CLAVE_OBLIGATORIA", "La apertura necesita una clave de operación base.")
        efectivo = datetime.combine(efectivo_en_demo, HORA_CIERRE_APERTURA)
        insertados = 0
        for fila in filas:
            tipo = (fila.tipo or "").strip().lower()
            catalogo = producto_por_codigo if tipo == PRODUCTO else ingrediente_por_codigo
            _modelo(tipo)
            if fila.codigo not in catalogo:
                raise ErrorAPI(422, "REFERENCIA_ROTA", f"No existe {tipo} {fila.codigo!r} para abrir su lote.")
            item_id = catalogo[fila.codigo]
            cantidad = _cantidad(tipo, fila.cantidad, f"Stock de {fila.codigo!r}", permitir_cero=True)
            if cantidad < 0:
                raise ErrorAPI(422, "CANTIDAD_INVALIDA", f"Stock de {fila.codigo!r}: no puede ser negativo.")
            if tipo == INGREDIENTE and fila.fecha_limite_venta is not None:
                raise ErrorAPI(422, "FECHA_INVALIDA", "La fecha límite de venta solo aplica a producto terminado.")
            if tipo == PRODUCTO:
                maxima = reglas.caducidad_maxima_producto(efectivo_en_demo)
                for nombre, valor in (("caducidad", fila.fecha_caducidad), ("límite de venta", fila.fecha_limite_venta)):
                    if valor is not None and valor > maxima:
                        raise ErrorAPI(
                            422,
                            "VIDA_UTIL_EXCEDIDA",
                            f"El lote de {fila.codigo!r} declara {nombre} {valor}; con vida máxima de "
                            f"{reglas.VIDA_MAXIMA_PRODUCTO_DIAS} días no puede pasar de {maxima}.",
                        )
            codigo_lote, informado = _codigo_lote(tipo, fila.codigo, fila.codigo_lote)
            modelo = _modelo(tipo)
            filtro_item = modelo.producto_id == item_id if tipo == PRODUCTO else modelo.ingrediente_id == item_id
            lote = sesion.scalar(
                select(modelo).where(filtro_item, modelo.codigo_lote == codigo_lote).with_for_update()
            )
            clave = _clave_apertura(clave_operacion_base, tipo, fila.codigo, codigo_lote)

            if lote is not None:
                # Reintento: solo es válido si describe exactamente lo ya abierto.
                mismas_fechas = lote.fecha_caducidad == fila.fecha_caducidad and (
                    tipo == INGREDIENTE or lote.fecha_limite_venta == fila.fecha_limite_venta
                )
                previo = _movimiento_por_clave(sesion, clave)
                if cantidad == 0 and mismas_fechas and previo is None:
                    continue
                if cantidad > 0 and mismas_fechas and previo is not None and Decimal(previo.delta) == cantidad:
                    continue
                raise ErrorAPI(
                    409,
                    "LOTE_EXISTENTE",
                    f"El lote {codigo_lote!r} de {fila.codigo!r} ya existe con otros datos.",
                )

            lote = modelo(
                codigo_lote=codigo_lote,
                lote_informado=informado,
                fecha_caducidad=fila.fecha_caducidad,
                saldo_disponible=0 if tipo == PRODUCTO else Decimal("0.000"),
            )
            if tipo == PRODUCTO:
                lote.producto_id = item_id
                lote.fecha_limite_venta = fila.fecha_limite_venta
            else:
                lote.ingrediente_id = item_id
            sesion.add(lote)
            sesion.flush()

            if cantidad > 0:
                _aplicar(
                    sesion,
                    tipo=tipo,
                    lote=lote,
                    delta=cantidad,
                    tipo_movimiento=TIPO_APERTURA,
                    clave=clave,
                    motivo="Apertura de primera carga",
                    efectivo_en_demo=efectivo,
                    usuario_id=None,
                )
                insertados += 1
        return insertados


# --- V02: ajustes -----------------------------------------------------------------


@dataclass(frozen=True)
class SolicitudAjuste:
    tipo_item: str
    lote_id: int
    delta: Decimal
    motivo: str
    clave_operacion: str
    efectivo_en_demo: datetime


def registrar_ajuste(sesion: Session, solicitud: SolicitudAjuste, usuario_id: int | None) -> ResultadoMovimiento:
    """Aplica un delta a un lote con bloqueo. No confirma.

    Dos ajustes concurrentes al mismo lote se serializan por el bloqueo de fila:
    el segundo lee el saldo que dejó el primero, así que no hay saldo negativo.
    """
    tipo = (solicitud.tipo_item or "").strip().lower()
    _modelo(tipo)
    delta = _cantidad(tipo, solicitud.delta, "Ajuste")
    motivo = (solicitud.motivo or "").strip()
    if len(motivo) < 3:
        raise ErrorAPI(422, "MOTIVO_OBLIGATORIO", "Indica el motivo del ajuste (mínimo 3 caracteres).")
    clave = (solicitud.clave_operacion or "").strip()
    if not clave or len(clave) > 200:
        raise ErrorAPI(422, "CLAVE_INVALIDA", "La clave de operación es obligatoria y admite hasta 200 caracteres.")
    efectivo = solicitud.efectivo_en_demo
    if efectivo.tzinfo is not None:
        raise ErrorAPI(422, "HORA_INVALIDA", "efectivo_en_demo es hora local del escenario, sin zona horaria.")

    lote = _bloquear_lote(sesion, tipo, solicitud.lote_id)
    return _aplicar(
        sesion,
        tipo=tipo,
        lote=lote,
        delta=delta,
        tipo_movimiento=TIPO_AJUSTE,
        clave=clave,
        motivo=motivo[:300],
        efectivo_en_demo=efectivo,
        usuario_id=usuario_id,
    )


# --- V02: disponibilidad por fecha (para el plan de Max) ---------------------------


@dataclass(frozen=True)
class LoteLeido:
    lote_id: int
    codigo_lote: str
    lote_informado: bool
    fecha_caducidad: date | None
    fecha_limite_venta: date | None
    saldo: Decimal
    estado: str
    dia_de_vida: int | None
    cuenta: bool
    motivo: str


@dataclass
class DisponibilidadItem:
    tipo: str
    item_id: int
    codigo: str
    nombre: str
    unidad: str
    stock_conocido: bool
    # `None` cuando no hay ningún lote registrado: desconocido, no cero.
    cantidad_disponible: Decimal | None
    cantidad_prioridad: Decimal
    cantidad_excluida: Decimal
    vigencia_desconocida: bool
    lotes: list[LoteLeido] = field(default_factory=list)


@dataclass(frozen=True)
class Disponibilidad:
    fecha: date
    leido_en: datetime
    huella: str
    items: list[DisponibilidadItem]

    def de(self, tipo: str, item_id: int) -> DisponibilidadItem | None:
        for item in self.items:
            if item.tipo == tipo and item.item_id == item_id:
                return item
        return None


def _lote_leido(tipo: str, lote, fecha: date) -> LoteLeido:
    if tipo == PRODUCTO:
        vig = reglas.vigencia_producto(fecha, lote.fecha_caducidad, lote.fecha_limite_venta)
    else:
        vig = reglas.vigencia_ingrediente(fecha, lote.fecha_caducidad)
    return LoteLeido(
        lote_id=lote.id,
        codigo_lote=lote.codigo_lote,
        lote_informado=lote.lote_informado,
        fecha_caducidad=lote.fecha_caducidad,
        fecha_limite_venta=getattr(lote, "fecha_limite_venta", None),
        saldo=_saldo(tipo, lote),
        estado=vig.estado,
        dia_de_vida=vig.dia_de_vida,
        cuenta=vig.cuenta,
        motivo=vig.motivo,
    )


def _item(tipo: str, item_id: int, codigo: str, nombre: str, unidad: str, lotes: list[LoteLeido]) -> DisponibilidadItem:
    cero = Decimal(0) if tipo == PRODUCTO else Decimal("0.000")
    if not lotes:
        return DisponibilidadItem(tipo, item_id, codigo, nombre, unidad, False, None, cero, cero, False, [])
    disponible = sum((l.saldo for l in lotes if l.cuenta), cero)
    prioridad = sum((l.saldo for l in lotes if l.estado == reglas.PRIORIDAD), cero)
    excluida = sum((l.saldo for l in lotes if not l.cuenta), cero)
    desconocida = any(l.estado == reglas.DESCONOCIDO and l.saldo > 0 for l in lotes)
    orden = sorted(lotes, key=lambda l: (l.fecha_caducidad is None, l.fecha_caducidad or date.max, l.codigo_lote))
    return DisponibilidadItem(tipo, item_id, codigo, nombre, unidad, True, disponible, prioridad, excluida, desconocida, orden)


def consultar_disponibilidad(
    sesion: Session,
    fecha: date,
    *,
    tipo: str | None = None,
    producto_ids: Iterable[int] | None = None,
    ingrediente_ids: Iterable[int] | None = None,
) -> Disponibilidad:
    """Stock elegible por ítem para `fecha`. Solo lee.

    Sin filtros devuelve los ítems que tienen al menos un lote. Si se piden IDs
    concretos, los que no tienen lote vuelven con `stock_conocido=False` y
    `cantidad_disponible=None`: el plan no debe tratarlos como cero.

    `huella` resume lotes, saldos y fechas leídos; el plan la guarda para
    reconocer si el stock cambió entre dos cálculos.
    """
    if tipo is not None:
        _modelo(tipo)
    items: list[DisponibilidadItem] = []

    if tipo in (None, PRODUCTO):
        ids = set(producto_ids) if producto_ids is not None else None
        consulta = select(LoteProducto)
        if ids is not None:
            consulta = consulta.where(LoteProducto.producto_id.in_(ids)) if ids else None
        lotes = list(sesion.scalars(consulta)) if consulta is not None else []
        por_item: dict[int, list] = {}
        for lote in lotes:
            por_item.setdefault(lote.producto_id, []).append(lote)
        buscar = (ids or set()) | set(por_item)
        productos = {p.id: p for p in sesion.scalars(select(Producto).where(Producto.id.in_(buscar)))} if buscar else {}
        for item_id in sorted(buscar):
            if item_id not in productos:
                continue
            producto = productos[item_id]
            leidos = [_lote_leido(PRODUCTO, lote, fecha) for lote in por_item.get(item_id, [])]
            items.append(_item(PRODUCTO, item_id, producto.codigo, producto.nombre, UNIDAD_PRODUCTO, leidos))

    if tipo in (None, INGREDIENTE):
        ids = set(ingrediente_ids) if ingrediente_ids is not None else None
        consulta = select(LoteIngrediente)
        if ids is not None:
            consulta = consulta.where(LoteIngrediente.ingrediente_id.in_(ids)) if ids else None
        lotes = list(sesion.scalars(consulta)) if consulta is not None else []
        por_item = {}
        for lote in lotes:
            por_item.setdefault(lote.ingrediente_id, []).append(lote)
        buscar = (ids or set()) | set(por_item)
        catalogo = ingredientes.obtener_ingredientes(sesion, buscar)
        for item_id in sorted(buscar):
            if item_id not in catalogo:
                continue
            ingrediente = catalogo[item_id]
            leidos = [_lote_leido(INGREDIENTE, lote, fecha) for lote in por_item.get(item_id, [])]
            items.append(
                _item(INGREDIENTE, item_id, ingrediente.codigo, ingrediente.nombre, ingrediente.unidad_base, leidos)
            )

    partes = [fecha.isoformat()]
    for item in items:
        for lote in item.lotes:
            partes.append(
                f"{item.tipo}|{item.item_id}|{lote.lote_id}|{lote.saldo}|{lote.fecha_caducidad}|{lote.fecha_limite_venta}"
            )
    huella = hashlib.sha256("\n".join(partes).encode("utf-8")).hexdigest()
    return Disponibilidad(fecha=fecha, leido_en=datetime.now(timezone.utc), huella=huella, items=items)


# --- Consultas para pantallas y otros módulos -------------------------------------


def contar_lotes_de_ingrediente(sesion: Session, ingrediente_id: int) -> int:
    return int(
        sesion.scalar(select(func.count(LoteIngrediente.id)).where(LoteIngrediente.ingrediente_id == ingrediente_id))
        or 0
    )


@dataclass(frozen=True)
class MovimientoLeido:
    id: int
    tipo_item: str
    lote_id: int
    codigo_lote: str
    item_nombre: str
    tipo_movimiento: str
    delta: Decimal
    saldo_resultante: Decimal
    motivo: str
    clave_operacion: str
    usuario_id: int | None
    efectivo_en_demo: datetime
    creado_en: datetime | None


def listar_movimientos(
    sesion: Session, *, tipo: str | None = None, lote_id: int | None = None, limite: int = 100
) -> list[MovimientoLeido]:
    if lote_id is not None and tipo is None:
        raise ErrorAPI(422, "TIPO_OBLIGATORIO", "Para filtrar por lote indica también el tipo.")
    consulta = select(MovimientoInventario).order_by(MovimientoInventario.id.desc()).limit(limite)
    if tipo == PRODUCTO:
        consulta = consulta.where(MovimientoInventario.lote_producto_id.is_not(None))
        if lote_id is not None:
            consulta = consulta.where(MovimientoInventario.lote_producto_id == lote_id)
    elif tipo == INGREDIENTE:
        consulta = consulta.where(MovimientoInventario.lote_ingrediente_id.is_not(None))
        if lote_id is not None:
            consulta = consulta.where(MovimientoInventario.lote_ingrediente_id == lote_id)
    elif tipo is not None:
        _modelo(tipo)
    movimientos = list(sesion.scalars(consulta))

    ids_lp = {m.lote_producto_id for m in movimientos if m.lote_producto_id}
    ids_li = {m.lote_ingrediente_id for m in movimientos if m.lote_ingrediente_id}
    lotes_p = {l.id: l for l in sesion.scalars(select(LoteProducto).where(LoteProducto.id.in_(ids_lp)))} if ids_lp else {}
    lotes_i = {l.id: l for l in sesion.scalars(select(LoteIngrediente).where(LoteIngrediente.id.in_(ids_li)))} if ids_li else {}
    productos = (
        {p.id: p.nombre for p in sesion.scalars(select(Producto).where(Producto.id.in_({l.producto_id for l in lotes_p.values()})))}
        if lotes_p
        else {}
    )
    catalogo = ingredientes.obtener_ingredientes(sesion, {l.ingrediente_id for l in lotes_i.values()})

    salida = []
    for m in movimientos:
        tipo_item, lote = (PRODUCTO, lotes_p[m.lote_producto_id]) if m.lote_producto_id else (INGREDIENTE, lotes_i[m.lote_ingrediente_id])
        nombre = productos.get(lote.producto_id, "") if tipo_item == PRODUCTO else catalogo[lote.ingrediente_id].nombre
        resultado = _resultado(m, repetido=False)
        salida.append(
            MovimientoLeido(
                id=m.id,
                tipo_item=tipo_item,
                lote_id=lote.id,
                codigo_lote=lote.codigo_lote,
                item_nombre=nombre,
                tipo_movimiento=m.tipo,
                delta=resultado.delta,
                saldo_resultante=resultado.saldo_resultante,
                motivo=m.motivo,
                clave_operacion=m.clave_operacion,
                usuario_id=m.usuario_id,
                efectivo_en_demo=m.efectivo_en_demo,
                creado_en=m.creado_en,
            )
        )
    return salida
