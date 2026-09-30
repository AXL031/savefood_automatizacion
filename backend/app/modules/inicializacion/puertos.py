"""Puertos que la primera carga necesita de otros dominios.

El importador coordina **una sola sesión**: los servicios participantes reciben
la sesión abierta, hacen `flush` si necesitan IDs y **no** confirman por su
cuenta. Así un error en recetas o en stock revierte también el catálogo y las
ventas.

Max implementa `ServicioRecetas` (ingredientes y recetas) y Vera implementa
`ServicioInventario` (apertura de lotes). Mientras no existan, la carga persiste
lo que pertenece a Edu y deja constancia de qué falta, sin declarar la
instalación inicializada.
"""

from __future__ import annotations

from datetime import date
from typing import Protocol

from sqlalchemy.orm import Session

from app.modules.inicializacion.validacion import FilaIngrediente, FilaReceta, FilaStock


class ServicioRecetas(Protocol):
    """Frontera con el bloque de Max (M01)."""

    def registrar_ingredientes(self, sesion: Session, filas: list[FilaIngrediente]) -> dict[str, int]:
        """Crea los ingredientes y devuelve `codigo -> ingrediente_id`."""

    def registrar_recetas(
        self,
        sesion: Session,
        filas: list[FilaReceta],
        producto_por_codigo: dict[str, int],
        ingrediente_por_codigo: dict[str, int],
    ) -> int:
        """Crea la versión 1 de cada receta y devuelve cuántas líneas guardó."""


class ServicioInventario(Protocol):
    """Frontera con el bloque de Vera (V01)."""

    def registrar_apertura(
        self,
        sesion: Session,
        filas: list[FilaStock],
        producto_por_codigo: dict[str, int],
        ingrediente_por_codigo: dict[str, int],
        efectivo_en_demo: date,
        clave_operacion_base: str,
    ) -> int:
        """Crea lotes y movimientos `APERTURA` idempotentes.

        Una cantidad explícita de cero registra el lote con saldo cero y **sin**
        movimiento de delta cero. Devuelve cuántos movimientos insertó.
        """
