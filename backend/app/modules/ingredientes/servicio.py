"""Interfaz pública del catálogo de ingredientes (M01).

Las funciones reciben la sesión del llamador y **no** confirman: la ruta HTTP o
el importador de Edu deciden el commit. Recetas, inventario y compras leen el
catálogo por aquí, sin importar el modelo.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Protocol

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errores import ErrorAPI
from app.modules.ingredientes.modelos import UNIDADES_BASE, Ingrediente


class _FilaIngrediente(Protocol):
    codigo: str
    nombre: str
    unidad_base: str


@dataclass(frozen=True)
class IngredienteLeido:
    id: int
    codigo: str
    nombre: str
    unidad_base: str
    activo: bool


@dataclass(frozen=True)
class UsoIngrediente:
    """Referencias que impiden cambiar la unidad base sin romper cifras previas."""

    lineas_receta: int
    lineas_receta_activa: int
    lotes: int

    @property
    def en_uso(self) -> bool:
        return self.lineas_receta > 0 or self.lotes > 0


def _leido(ingrediente: Ingrediente) -> IngredienteLeido:
    return IngredienteLeido(
        id=ingrediente.id,
        codigo=ingrediente.codigo,
        nombre=ingrediente.nombre,
        unidad_base=ingrediente.unidad_base,
        activo=ingrediente.activo,
    )


def _texto(valor: str, campo: str) -> str:
    limpio = (valor or "").strip()
    if not limpio:
        raise ErrorAPI(422, "DATO_OBLIGATORIO", f"El campo {campo} no puede estar vacío.")
    if len(limpio) > 160:
        raise ErrorAPI(422, "DATO_DEMASIADO_LARGO", f"El campo {campo} admite hasta 160 caracteres.")
    return limpio


def _unidad(valor: str) -> str:
    unidad = (valor or "").strip().lower()
    if unidad not in UNIDADES_BASE:
        raise ErrorAPI(
            422,
            "UNIDAD_NO_PERMITIDA",
            f"Unidad {valor!r} no permitida. Usa una de: {', '.join(UNIDADES_BASE)}.",
        )
    return unidad


def uso_ingrediente(sesion: Session, ingrediente_id: int) -> UsoIngrediente:
    # Importaciones locales: recetas e inventario importan este módulo.
    from app.modules.inventario.servicio import contar_lotes_de_ingrediente
    from app.modules.recetas.servicio import contar_lineas_de_ingrediente

    total, activas = contar_lineas_de_ingrediente(sesion, ingrediente_id)
    return UsoIngrediente(
        lineas_receta=total,
        lineas_receta_activa=activas,
        lotes=contar_lotes_de_ingrediente(sesion, ingrediente_id),
    )


def listar_ingredientes(sesion: Session, solo_activos: bool = False) -> list[tuple[IngredienteLeido, UsoIngrediente]]:
    consulta = select(Ingrediente).order_by(Ingrediente.nombre)
    if solo_activos:
        consulta = consulta.where(Ingrediente.activo.is_(True))
    return [(_leido(fila), uso_ingrediente(sesion, fila.id)) for fila in sesion.scalars(consulta)]


def obtener_ingredientes(sesion: Session, ids: Iterable[int]) -> dict[int, IngredienteLeido]:
    """Lectura por ID para recetas, inventario y compras."""
    ids = set(ids)
    if not ids:
        return {}
    filas = sesion.scalars(select(Ingrediente).where(Ingrediente.id.in_(ids)))
    return {fila.id: _leido(fila) for fila in filas}


def obtener_ingrediente(sesion: Session, ingrediente_id: int) -> IngredienteLeido:
    fila = sesion.get(Ingrediente, ingrediente_id)
    if fila is None:
        raise ErrorAPI(404, "INGREDIENTE_NO_ENCONTRADO", f"No existe el ingrediente {ingrediente_id}.")
    return _leido(fila)


def crear_ingrediente(sesion: Session, codigo: str, nombre: str, unidad_base: str) -> IngredienteLeido:
    codigo = _texto(codigo, "codigo")
    nombre = _texto(nombre, "nombre")
    unidad = _unidad(unidad_base)
    if sesion.scalar(select(Ingrediente.id).where(Ingrediente.codigo == codigo)) is not None:
        raise ErrorAPI(409, "CODIGO_DUPLICADO", f"Ya existe un ingrediente con código {codigo!r}.")
    ingrediente = Ingrediente(codigo=codigo, nombre=nombre, unidad_base=unidad, activo=True)
    sesion.add(ingrediente)
    sesion.flush()
    return _leido(ingrediente)


def actualizar_ingrediente(
    sesion: Session,
    ingrediente_id: int,
    *,
    nombre: str | None = None,
    unidad_base: str | None = None,
    activo: bool | None = None,
) -> IngredienteLeido:
    """Edita nombre, unidad o estado.

    La unidad base no cambia si alguna receta o lote la usa: las cantidades
    guardadas quedarían expresadas en otra unidad sin conversión. El código no
    se edita porque identifica el ingrediente en la primera carga.
    """
    ingrediente = sesion.get(Ingrediente, ingrediente_id, with_for_update=True)
    if ingrediente is None:
        raise ErrorAPI(404, "INGREDIENTE_NO_ENCONTRADO", f"No existe el ingrediente {ingrediente_id}.")

    if nombre is not None:
        ingrediente.nombre = _texto(nombre, "nombre")

    if unidad_base is not None:
        unidad = _unidad(unidad_base)
        if unidad != ingrediente.unidad_base:
            uso = uso_ingrediente(sesion, ingrediente_id)
            if uso.en_uso:
                raise ErrorAPI(
                    409,
                    "UNIDAD_EN_USO",
                    f"No se puede cambiar la unidad de {ingrediente.nombre!r}: la usan "
                    f"{uso.lineas_receta} líneas de receta y {uso.lotes} lotes. "
                    "Crea un ingrediente nuevo si la unidad real es otra.",
                )
            ingrediente.unidad_base = unidad

    if activo is not None and activo != ingrediente.activo:
        if not activo and uso_ingrediente(sesion, ingrediente_id).lineas_receta_activa > 0:
            raise ErrorAPI(
                409,
                "INGREDIENTE_EN_RECETA_ACTIVA",
                f"{ingrediente.nombre!r} forma parte de una receta activa. "
                "Crea antes una versión de receta sin este ingrediente.",
            )
        ingrediente.activo = activo

    sesion.flush()
    return _leido(ingrediente)


def registrar_ingredientes(sesion: Session, filas: Iterable[_FilaIngrediente]) -> dict[str, int]:
    """Primera carga: crea los ingredientes y devuelve `codigo -> id`. No confirma.

    Si el código ya existe con la misma unidad se reutiliza (reintento de la
    misma carga). Si existe con otra unidad es conflicto: no se fusiona en
    silencio.
    """
    resultado: dict[str, int] = {}
    for fila in filas:
        codigo = _texto(fila.codigo, "codigo")
        nombre = _texto(fila.nombre, "nombre")
        unidad = _unidad(fila.unidad_base)
        if codigo in resultado:
            raise ErrorAPI(422, "CODIGO_DUPLICADO", f"El ingrediente {codigo!r} aparece dos veces.")
        existente = sesion.scalar(select(Ingrediente).where(Ingrediente.codigo == codigo))
        if existente is not None:
            if existente.unidad_base != unidad:
                raise ErrorAPI(
                    409,
                    "INGREDIENTE_DIFERENTE",
                    f"El ingrediente {codigo!r} ya existe con unidad {existente.unidad_base!r}.",
                )
            resultado[codigo] = existente.id
            continue
        ingrediente = Ingrediente(codigo=codigo, nombre=nombre, unidad_base=unidad, activo=True)
        sesion.add(ingrediente)
        sesion.flush()
        resultado[codigo] = ingrediente.id
    return resultado
