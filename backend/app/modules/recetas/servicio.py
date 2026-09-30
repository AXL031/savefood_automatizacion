"""Interfaz pública de recetas versionadas (M01).

- `ServicioRecetasM01` implementa el puerto `ServicioRecetas` de la primera
  carga de Edu: recibe la sesión compartida y **no** confirma.
- `crear_version` es el único camino para cambiar una receta: nunca edita una
  versión existente.
- `obtener_receta`, `recetas_activas` y `obtener_receta_activa` son la lectura
  versionada que consume Planificación (M02).
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable, Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.errores import ErrorAPI
from app.modules.ingredientes import servicio as ingredientes
from app.modules.productos.modelos import Producto
from app.modules.recetas.modelos import Receta, RecetaIngrediente

DECIMALES = 3
_CUANTO = Decimal("0.001")


@dataclass(frozen=True)
class LineaLeida:
    ingrediente_id: int
    codigo: str
    nombre: str
    unidad_base: str
    cantidad_por_unidad: Decimal


@dataclass(frozen=True)
class RecetaLeida:
    receta_id: int
    producto_id: int
    version: int
    activo: bool
    motivo: str | None
    creado_en: datetime | None
    lineas: tuple[LineaLeida, ...]


@dataclass(frozen=True)
class LineaNueva:
    ingrediente_id: int
    cantidad_por_unidad: Decimal


def cantidad_valida(valor: Decimal, contexto: str) -> Decimal:
    """Cantidad positiva con hasta tres decimales, sin redondeo silencioso."""
    if not isinstance(valor, Decimal):
        valor = Decimal(str(valor))
    if not valor.is_finite() or valor <= 0:
        raise ErrorAPI(422, "CANTIDAD_INVALIDA", f"{contexto}: la cantidad debe ser mayor que cero.")
    if -valor.as_tuple().exponent > DECIMALES:
        raise ErrorAPI(
            422, "CANTIDAD_INVALIDA", f"{contexto}: se admiten hasta {DECIMALES} decimales en la unidad base."
        )
    if valor >= Decimal("100000000000"):
        raise ErrorAPI(422, "CANTIDAD_INVALIDA", f"{contexto}: la cantidad es demasiado grande.")
    return valor.quantize(_CUANTO, rounding=ROUND_HALF_UP)


def _leer(sesion: Session, receta: Receta) -> RecetaLeida:
    catalogo = ingredientes.obtener_ingredientes(sesion, (linea.ingrediente_id for linea in receta.lineas))
    return RecetaLeida(
        receta_id=receta.id,
        producto_id=receta.producto_id,
        version=receta.version,
        activo=receta.activo,
        motivo=receta.motivo,
        creado_en=receta.creado_en,
        lineas=tuple(
            LineaLeida(
                ingrediente_id=linea.ingrediente_id,
                codigo=catalogo[linea.ingrediente_id].codigo,
                nombre=catalogo[linea.ingrediente_id].nombre,
                unidad_base=catalogo[linea.ingrediente_id].unidad_base,
                cantidad_por_unidad=Decimal(linea.cantidad_por_unidad).quantize(_CUANTO),
            )
            for linea in receta.lineas
        ),
    )


# --- Lectura versionada (Planificación, M02) -------------------------------------


def obtener_receta(sesion: Session, receta_id: int) -> RecetaLeida:
    """Una versión concreta, activa o no. El plan guarda este ID."""
    receta = sesion.get(Receta, receta_id)
    if receta is None:
        raise ErrorAPI(404, "RECETA_NO_ENCONTRADA", f"No existe la receta {receta_id}.")
    return _leer(sesion, receta)


def recetas_activas(sesion: Session, producto_ids: Iterable[int] | None = None) -> dict[int, RecetaLeida]:
    """Receta activa por producto. Un producto sin receta no aparece en el dict."""
    consulta = select(Receta).where(Receta.activo.is_(True))
    if producto_ids is not None:
        ids = set(producto_ids)
        if not ids:
            return {}
        consulta = consulta.where(Receta.producto_id.in_(ids))
    return {receta.producto_id: _leer(sesion, receta) for receta in sesion.scalars(consulta)}


def obtener_receta_activa(sesion: Session, producto_id: int) -> RecetaLeida | None:
    return recetas_activas(sesion, [producto_id]).get(producto_id)


def historial_de_producto(sesion: Session, producto_id: int) -> list[RecetaLeida]:
    consulta = select(Receta).where(Receta.producto_id == producto_id).order_by(Receta.version.desc())
    return [_leer(sesion, receta) for receta in sesion.scalars(consulta)]


def contar_lineas_de_ingrediente(sesion: Session, ingrediente_id: int) -> tuple[int, int]:
    """`(líneas en cualquier versión, líneas en versiones activas)` del ingrediente."""
    total = sesion.scalar(
        select(func.count(RecetaIngrediente.id)).where(RecetaIngrediente.ingrediente_id == ingrediente_id)
    )
    activas = sesion.scalar(
        select(func.count(RecetaIngrediente.id))
        .join(Receta, Receta.id == RecetaIngrediente.receta_id)
        .where(RecetaIngrediente.ingrediente_id == ingrediente_id, Receta.activo.is_(True))
    )
    return int(total or 0), int(activas or 0)


# --- Escritura -------------------------------------------------------------------


def _validar_lineas(sesion: Session, producto_id: int, lineas: Sequence[LineaNueva]) -> list[LineaNueva]:
    if not lineas:
        raise ErrorAPI(422, "RECETA_VACIA", "La receta necesita al menos un ingrediente.")
    vistos: set[int] = set()
    limpias: list[LineaNueva] = []
    for linea in lineas:
        if linea.ingrediente_id in vistos:
            raise ErrorAPI(
                422, "INGREDIENTE_REPETIDO", f"El ingrediente {linea.ingrediente_id} aparece dos veces en la receta."
            )
        vistos.add(linea.ingrediente_id)
        limpias.append(
            LineaNueva(
                ingrediente_id=linea.ingrediente_id,
                cantidad_por_unidad=cantidad_valida(
                    linea.cantidad_por_unidad, f"Ingrediente {linea.ingrediente_id}"
                ),
            )
        )
    catalogo = ingredientes.obtener_ingredientes(sesion, vistos)
    faltantes = sorted(vistos - set(catalogo))
    if faltantes:
        raise ErrorAPI(422, "REFERENCIA_ROTA", f"No existen los ingredientes {faltantes}.")
    inactivos = sorted(catalogo[i].codigo for i in vistos if not catalogo[i].activo)
    if inactivos:
        raise ErrorAPI(422, "INGREDIENTE_INACTIVO", f"Ingredientes inactivos en la receta: {', '.join(inactivos)}.")
    return limpias


def _misma_composicion(receta: Receta, lineas: Sequence[LineaNueva]) -> bool:
    actual = {linea.ingrediente_id: Decimal(linea.cantidad_por_unidad).quantize(_CUANTO) for linea in receta.lineas}
    nueva = {linea.ingrediente_id: linea.cantidad_por_unidad for linea in lineas}
    return actual == nueva


def _insertar_version(
    sesion: Session,
    producto_id: int,
    version: int,
    lineas: Sequence[LineaNueva],
    motivo: str | None,
    usuario_id: int | None,
) -> Receta:
    receta = Receta(producto_id=producto_id, version=version, activo=True, motivo=motivo, creado_por=usuario_id)
    sesion.add(receta)
    sesion.flush()
    for linea in lineas:
        sesion.add(
            RecetaIngrediente(
                receta_id=receta.id,
                ingrediente_id=linea.ingrediente_id,
                cantidad_por_unidad=linea.cantidad_por_unidad,
            )
        )
    sesion.flush()
    sesion.refresh(receta)
    return receta


@dataclass(frozen=True)
class ResultadoVersion:
    receta: RecetaLeida
    creada: bool


def crear_version(
    sesion: Session,
    producto_id: int,
    lineas: Sequence[LineaNueva],
    motivo: str,
    usuario_id: int | None = None,
) -> ResultadoVersion:
    """Crea la versión siguiente de la receta y desactiva la anterior. No confirma.

    Toda edición crea versión nueva (acuerdo del equipo): no hace falta saber si
    la anterior ya la usó un plan, porque ninguna versión se modifica en sitio.
    Enviar la misma composición que la versión activa no crea otra versión.
    """
    motivo = (motivo or "").strip()
    if len(motivo) < 3:
        raise ErrorAPI(422, "MOTIVO_OBLIGATORIO", "Indica el motivo del cambio de receta (mínimo 3 caracteres).")
    producto = sesion.get(Producto, producto_id, with_for_update=True)
    if producto is None:
        raise ErrorAPI(404, "PRODUCTO_NO_ENCONTRADO", f"No existe el producto {producto_id}.")
    if not producto.activo:
        raise ErrorAPI(422, "PRODUCTO_INACTIVO", f"El producto {producto.nombre!r} está inactivo.")

    limpias = _validar_lineas(sesion, producto_id, lineas)
    activa = sesion.scalar(select(Receta).where(Receta.producto_id == producto_id, Receta.activo.is_(True)))
    if activa is not None and _misma_composicion(activa, limpias):
        return ResultadoVersion(receta=_leer(sesion, activa), creada=False)

    ultima = sesion.scalar(select(func.max(Receta.version)).where(Receta.producto_id == producto_id)) or 0
    if activa is not None:
        activa.activo = False
        # El índice único parcial exige desactivar antes de insertar la nueva.
        sesion.flush()
    receta = _insertar_version(sesion, producto_id, ultima + 1, limpias, motivo[:300], usuario_id)
    return ResultadoVersion(receta=_leer(sesion, receta), creada=True)


class ServicioRecetasM01:
    """Implementación del puerto `ServicioRecetas` de la primera carga."""

    def registrar_ingredientes(self, sesion: Session, filas) -> dict[str, int]:
        return ingredientes.registrar_ingredientes(sesion, filas)

    def registrar_recetas(
        self,
        sesion: Session,
        filas,
        producto_por_codigo: dict[str, int],
        ingrediente_por_codigo: dict[str, int],
    ) -> int:
        """Crea la versión 1 de cada receta y devuelve cuántas líneas guardó.

        Referencia rota o pareja duplicada rechazan toda la carga. Si el
        producto ya tiene una receta activa idéntica (reintento de la misma
        carga) se reutiliza; si es distinta es conflicto, no una sustitución.
        """
        por_producto: dict[int, list[LineaNueva]] = defaultdict(list)
        parejas: set[tuple[str, str]] = set()
        for fila in filas:
            pareja = (fila.codigo_producto, fila.codigo_ingrediente)
            if pareja in parejas:
                raise ErrorAPI(
                    422,
                    "PAREJA_DUPLICADA",
                    f"La receta de {fila.codigo_producto!r} repite el ingrediente {fila.codigo_ingrediente!r}.",
                )
            parejas.add(pareja)
            if fila.codigo_producto not in producto_por_codigo:
                raise ErrorAPI(422, "REFERENCIA_ROTA", f"No existe el producto {fila.codigo_producto!r}.")
            if fila.codigo_ingrediente not in ingrediente_por_codigo:
                raise ErrorAPI(422, "REFERENCIA_ROTA", f"No existe el ingrediente {fila.codigo_ingrediente!r}.")
            por_producto[producto_por_codigo[fila.codigo_producto]].append(
                LineaNueva(
                    ingrediente_id=ingrediente_por_codigo[fila.codigo_ingrediente],
                    cantidad_por_unidad=fila.cantidad_por_unidad,
                )
            )

        guardadas = 0
        for producto_id, lineas in por_producto.items():
            limpias = _validar_lineas(sesion, producto_id, lineas)
            existentes = sesion.scalar(select(func.count(Receta.id)).where(Receta.producto_id == producto_id))
            if existentes:
                activa = sesion.scalar(
                    select(Receta).where(Receta.producto_id == producto_id, Receta.activo.is_(True))
                )
                if activa is not None and _misma_composicion(activa, limpias):
                    guardadas += len(limpias)
                    continue
                raise ErrorAPI(
                    409,
                    "RECETA_DIFERENTE",
                    f"El producto {producto_id} ya tiene receta distinta; cámbiala creando una versión nueva.",
                )
            _insertar_version(sesion, producto_id, 1, limpias, "Primera carga", None)
            guardadas += len(limpias)
        return guardadas
