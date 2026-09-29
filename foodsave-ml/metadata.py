"""Construcción y validación de metadata.json del artefacto ML.

Define los campos exigidos por CONTRATO_ARTEFACTO_INFERENCIA.md y las
reglas de validación para aceptar o rechazar un artefacto antes de usarlo
en inferencia.

Estados válidos del artefacto:
  experimental_pendiente_de_aceptacion — notebook/experimento; no se usa en backend
  listo_demo                           — aprobado para la simulación histórica local
  aprobado                             — uso operativo futuro (requiere evaluación externa)

Solo 'listo_demo' y 'aprobado' son aceptados por el backend de inferencia.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Literal

ESTADOS_VALIDOS = frozenset(
    {"experimental_pendiente_de_aceptacion", "listo_demo", "aprobado"}
)
ESTADOS_ACEPTABLES_BACKEND = frozenset({"listo_demo", "aprobado"})

CAMPOS_REQUERIDOS = [
    "estado",
    "version_modelo",
    "comercio_id",
    "sucursal_id",
    "artefacto",
    "sha256_artefacto",
    "fecha_corte_entrenamiento",
    "particion",
    "features",
    "cat_features",
    "productos_entrenados",
    "min_observaciones_previas_28_dias",
    "horizonte",
    "politica_ausencias",
]

CAMPOS_PARTICION_REQUERIDOS = [
    "version_politica",
    "inicio_entrenamiento",
    "fin_entrenamiento",
    "inicio_validacion",
    "fin_validacion",
    "inicio_prueba",
    "fin_prueba",
    "meses_validos",
    "meses_validacion",
    "meses_prueba",
]

# Features contractuales en orden exacto
FEATURES_CONTRATO = [
    "article",
    "dia_semana",
    "mes",
    "dia_mes",
    "fin_semana",
    "ventas_ayer",
    "ventas_hace_7_dias",
    "promedio_7_dias",
    "promedio_14_dias",
    "promedio_28_dias",
    "conteo_7_dias",
    "conteo_14_dias",
    "conteo_28_dias",
]


class ErrorArtefacto(Exception):
    """El artefacto no cumple el contrato y no puede usarse en inferencia."""


def cargar_metadata(directorio: Path) -> dict:
    """Lee metadata.json desde `directorio` y devuelve el diccionario.

    Raises:
        ErrorArtefacto: si el archivo no existe o no es JSON válido.
    """
    ruta = directorio / "metadata.json"
    if not ruta.exists():
        raise ErrorArtefacto(
            f"No se encontró metadata.json en {directorio}. "
            "El artefacto no ha sido entrenado o el directorio es incorrecto."
        )
    try:
        return json.loads(ruta.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ErrorArtefacto(f"metadata.json no es JSON válido: {exc}") from exc


def validar_metadata(meta: dict) -> None:
    """Verifica que la metadata contenga todos los campos requeridos y sus tipos.

    Raises:
        ErrorArtefacto: con descripción del primer campo que falla.
    """
    for campo in CAMPOS_REQUERIDOS:
        if campo not in meta:
            raise ErrorArtefacto(f"Campo requerido faltante en metadata.json: '{campo}'")

    if meta["estado"] not in ESTADOS_VALIDOS:
        raise ErrorArtefacto(
            f"Estado desconocido: '{meta['estado']}'. "
            f"Valores válidos: {sorted(ESTADOS_VALIDOS)}"
        )

    if not meta["version_modelo"] or not isinstance(meta["version_modelo"], str):
        raise ErrorArtefacto("'version_modelo' debe ser una cadena no vacía")

    if not isinstance(meta["features"], list) or meta["features"] != FEATURES_CONTRATO:
        raise ErrorArtefacto(
            f"'features' no coincide con el contrato.\n"
            f"  Metadata: {meta['features']}\n"
            f"Contrato:  {FEATURES_CONTRATO}"
        )

    particion = meta.get("particion", {})
    for campo_p in CAMPOS_PARTICION_REQUERIDOS:
        if campo_p not in particion:
            raise ErrorArtefacto(
                f"Campo de partición faltante en metadata.json: 'particion.{campo_p}'"
            )

    if not isinstance(meta["productos_entrenados"], list) or not meta["productos_entrenados"]:
        raise ErrorArtefacto("'productos_entrenados' debe ser una lista no vacía de SKUs")

    if not isinstance(meta["min_observaciones_previas_28_dias"], int) or \
            meta["min_observaciones_previas_28_dias"] < 1:
        raise ErrorArtefacto(
            "'min_observaciones_previas_28_dias' debe ser un entero positivo"
        )


def validar_aceptable_backend(meta: dict) -> None:
    """Verifica que el estado del artefacto permita su uso en inferencia.

    Raises:
        ErrorArtefacto: si el estado no es 'listo_demo' ni 'aprobado'.
    """
    if meta["estado"] not in ESTADOS_ACEPTABLES_BACKEND:
        raise ErrorArtefacto(
            f"El artefacto tiene estado '{meta['estado']}' y no puede usarse en inferencia. "
            f"Se requiere uno de: {sorted(ESTADOS_ACEPTABLES_BACKEND)}"
        )


def validar_huella(directorio: Path, meta: dict) -> None:
    """Verifica que el SHA-256 del CBM coincida con el registrado en metadata.

    Raises:
        ErrorArtefacto: si el CBM no existe o la huella no coincide.
    """
    nombre_cbm = meta.get("artefacto", "catboost_model.cbm")
    ruta_cbm = directorio / nombre_cbm

    if not ruta_cbm.exists():
        raise ErrorArtefacto(
            f"No se encontró el artefacto CBM: {ruta_cbm}. "
            "El archivo puede haber sido borrado o movido."
        )

    h = hashlib.sha256()
    with open(ruta_cbm, "rb") as f:
        for bloque in iter(lambda: f.read(65536), b""):
            h.update(bloque)
    sha256_real = h.hexdigest()

    sha256_esperado = meta.get("sha256_artefacto", "")
    if sha256_real != sha256_esperado:
        raise ErrorArtefacto(
            f"La huella SHA-256 del CBM no coincide con metadata.json.\n"
            f"  Calculado: {sha256_real}\n"
            f"  Esperado:  {sha256_esperado}\n"
            "El archivo puede estar corrupto o fue reemplazado sin actualizar metadata."
        )


def validar_identidad(meta: dict, comercio_id: str, sucursal_id: str) -> None:
    """Verifica que el artefacto corresponda al comercio/sucursal en uso.

    Raises:
        ErrorArtefacto: si el par comercio/sucursal no coincide.
    """
    if meta.get("comercio_id") != comercio_id or meta.get("sucursal_id") != sucursal_id:
        raise ErrorArtefacto(
            f"El artefacto fue entrenado para "
            f"comercio='{meta.get('comercio_id')}' / sucursal='{meta.get('sucursal_id')}' "
            f"pero se solicitó inferencia para "
            f"comercio='{comercio_id}' / sucursal='{sucursal_id}'."
        )


def verificar_artefacto_completo(
    directorio: Path,
    comercio_id: str | None = None,
    sucursal_id: str | None = None,
) -> dict:
    """Carga y verifica el artefacto completo (metadata + CBM + huella + identidad).

    Args:
        directorio: Directorio que contiene catboost_model.cbm y metadata.json.
        comercio_id: Si se indica, verifica que el artefacto coincida con este comercio.
        sucursal_id: Si se indica, verifica que el artefacto coincida con esta sucursal.

    Returns:
        Diccionario de metadata validado.

    Raises:
        ErrorArtefacto: si cualquier verificación falla.
    """
    meta = cargar_metadata(directorio)
    validar_metadata(meta)
    validar_aceptable_backend(meta)
    validar_huella(directorio, meta)
    if comercio_id is not None and sucursal_id is not None:
        validar_identidad(meta, comercio_id, sucursal_id)
    return meta
