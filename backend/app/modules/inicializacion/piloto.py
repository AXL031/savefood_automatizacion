"""Carga directa del CSV bakery para la demostración local."""

import hashlib
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.core.base_datos import obtener_sesion
from app.core.errores import ErrorAPI
from app.core.identidad import requiere_administrador
from app.modules.autenticacion.modelos import Usuario
from app.modules.automatizaciones.servicio import crear_o_recuperar_ejecucion
from app.modules.productos.servicio import cargar_catalogo_bakery
from app.modules.ventas.servicio import importar_bakery

router = APIRouter(prefix="/inicializacion", tags=["inicializacion"])
MAX_CSV_BYTES = 25 * 1024 * 1024
CATALOGO = "lista_productos_precios_limpia.md"
# Incrementar al cambiar el entrenamiento en foodsave-ml/artefacto.py.
VERSION_POLITICA_MODELO = "q65v2"


def _catalogo_piloto() -> Path:
    for padre in Path(__file__).resolve().parents:
        candidato = padre / "foodsave-ml" / CATALOGO
        if candidato.is_file():
            return candidato
    raise ErrorAPI(503, "CATALOGO_PILOTO_NO_DISPONIBLE", "No está disponible la lista de productos del piloto.")


@router.post("/piloto-bakery", status_code=202)
def cargar_piloto_bakery(
    archivo: UploadFile = File(...),
    _admin: Usuario = Depends(requiere_administrador),
    sesion: Session = Depends(obtener_sesion),
):
    """Carga catálogo y ventas; agenda el modelo en el mismo commit."""
    if not archivo.filename or Path(archivo.filename).suffix.lower() != ".csv":
        raise ErrorAPI(422, "ARCHIVO_INVALIDO", "Selecciona un archivo CSV del piloto bakery.")

    temporal: Path | None = None
    digest = hashlib.sha256()
    total = 0
    try:
        with tempfile.NamedTemporaryFile(prefix="foodsave-bakery-", suffix=".csv", delete=False) as destino:
            temporal = Path(destino.name)
            while bloque := archivo.file.read(1024 * 1024):
                total += len(bloque)
                if total > MAX_CSV_BYTES:
                    raise ErrorAPI(413, "ARCHIVO_DEMASIADO_GRANDE", "El CSV supera el límite de 25 MB.")
                digest.update(bloque)
                destino.write(bloque)
        if total == 0:
            raise ErrorAPI(422, "ARCHIVO_VACIO", "El CSV está vacío.")

        huella = digest.hexdigest()
        productos = cargar_catalogo_bakery(sesion, _catalogo_piloto())
        resultado = importar_bakery(sesion, temporal, f"piloto-bakery-{huella[:24]}")
        version = f"piloto-{VERSION_POLITICA_MODELO}-{huella[:12]}"
        ejecucion = crear_o_recuperar_ejecucion(
            sesion, "PREPARAR_MODELO", f"modelo-{version}",
            {"version_modelo": version},
        )
        sesion.commit()
        return {"datos": {
            "importacion_id": resultado.importacion_id,
            "repetida": resultado.ventas_diarias == 0,
            "productos": productos,
            "filas_aceptadas": resultado.filas_aceptadas,
            "filas_negativas_excluidas": resultado.filas_negativas_excluidas,
            "ventas_diarias_creadas": resultado.ventas_diarias,
            "version_modelo": version,
            "ejecucion_id": ejecucion.id,
            "estado_ejecucion": ejecucion.estado,
        }}
    except Exception:
        sesion.rollback()
        raise
    finally:
        archivo.file.close()
        if temporal is not None:
            temporal.unlink(missing_ok=True)
