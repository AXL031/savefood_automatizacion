"""API del asistente de primera carga y del estado de inicialización."""

from datetime import date

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.core.base_datos import obtener_sesion
from app.core.errores import ErrorAPI
from app.core.identidad import identidad_actual, requiere_administrador
from app.modules.autenticacion.modelos import Usuario
from app.modules.inicializacion.modelos import ConfiguracionInicial
from app.modules.inventario.servicio import ServicioInventarioV01
from app.modules.recetas.servicio import ServicioRecetasM01
from app.modules.inicializacion.servicio import (
    VistaPrevia,
    confirmar_carga,
    leer_estado,
    preparar_vista_previa,
    skus_curados,
)

router = APIRouter(prefix="/inicializacion", tags=["inicializacion"])

# Tope por archivo. El CSV del piloto ronda los 12 MB; se deja margen sin admitir
# una subida capaz de agotar la memoria del contenedor local.
LIMITE_BYTES = 64 * 1024 * 1024


def _estado(fila: ConfiguracionInicial) -> dict:
    return {
        "estado": fila.estado,
        "huella_ventas": fila.huella_ventas,
        "huella_catalogo": fila.huella_catalogo,
        "huella_solicitud": fila.huella_solicitud,
        "fecha_objetivo_demo": fila.fecha_objetivo_demo.isoformat() if fila.fecha_objetivo_demo else None,
        "fecha_referencia_stock": (
            fila.fecha_referencia_stock.isoformat() if fila.fecha_referencia_stock else None
        ),
        "iniciada_en": fila.iniciada_en.isoformat() if fila.iniciada_en else None,
        "completada_en": fila.completada_en.isoformat() if fila.completada_en else None,
        "mensaje_error": fila.mensaje_error,
    }


def _vista_previa(vista: VistaPrevia) -> dict:
    resultado = vista.resultado
    primera, ultima = resultado.fechas_ventas
    respuesta = {
        "aceptable": resultado.aceptable,
        "total_errores": resultado.total_errores,
        "errores": [error.como_detalle() for error in resultado.errores],
        "filas_por_hoja": resultado.filas_por_hoja,
        "ventas": {
            "filas": len(resultado.entrada.ventas),
            "skus": resultado.skus_en_ventas,
            "primera_fecha": primera.isoformat() if primera else None,
            "ultima_fecha": ultima.isoformat() if ultima else None,
        },
        "catalogo": {
            "productos": len(resultado.entrada.productos),
            "productos_demo": [
                {"codigo": fila.codigo, "nombre": fila.nombre, "sku_externo": fila.sku_externo}
                for fila in resultado.entrada.productos_demo
            ],
            "ingredientes": len(resultado.entrada.ingredientes),
            "lineas_receta": len(resultado.entrada.recetas),
            "filas_stock": len(resultado.entrada.stock),
        },
        "huellas": {
            "ventas": vista.huella_ventas,
            "catalogo": vista.huella_catalogo,
            "solicitud": vista.huella_solicitud,
        },
    }
    if vista.resumen_bakery is not None:
        resumen = vista.resumen_bakery
        respuesta["adaptador_bakery"] = {
            "lineas_leidas": resumen.lineas_leidas,
            "lineas_negativas_excluidas": resumen.lineas_negativas,
            "lineas_invalidas": resumen.lineas_invalidas,
            "pares_generados": resumen.pares_generados,
            "articulos": resumen.articulos,
        }
    return respuesta


async def _leer_archivos(archivos: list[UploadFile]) -> dict[str, bytes]:
    if not archivos:
        raise ErrorAPI(422, "ENTREGA_VACIA", "Adjunta los archivos de la primera carga.")
    contenidos: dict[str, bytes] = {}
    for archivo in archivos:
        nombre = (archivo.filename or "").strip()
        if not nombre:
            raise ErrorAPI(422, "ARCHIVO_SIN_NOMBRE", "Cada archivo debe llegar con su nombre.")
        contenido = await archivo.read()
        if len(contenido) > LIMITE_BYTES:
            raise ErrorAPI(413, "ARCHIVO_DEMASIADO_GRANDE", f"{nombre} supera el tamaño permitido.")
        if nombre.lower() in contenidos:
            raise ErrorAPI(422, "ARCHIVO_REPETIDO", f"{nombre} llegó dos veces.")
        contenidos[nombre] = contenido
    return contenidos


@router.get("/estado")
def consultar_estado(
    _usuario: Usuario = Depends(identidad_actual),
    sesion: Session = Depends(obtener_sesion),
):
    return {"datos": _estado(leer_estado(sesion))}


@router.post("/vista-previa")
async def validar_entrega_sin_guardar(
    fecha_objetivo_demo: date = Form(...),
    fecha_referencia_stock: date = Form(...),
    archivos: list[UploadFile] = File(...),
    _admin: Usuario = Depends(requiere_administrador),
):
    """Valida la entrega y devuelve la vista previa. No escribe en la base."""
    contenidos = await _leer_archivos(archivos)
    vista = preparar_vista_previa(
        contenidos, fecha_objetivo_demo, fecha_referencia_stock, skus_curados()
    )
    return {"datos": _vista_previa(vista)}


@router.post("/confirmar", status_code=201)
async def confirmar(
    fecha_objetivo_demo: date = Form(...),
    fecha_referencia_stock: date = Form(...),
    clave_importacion: str = Form(...),
    archivos: list[UploadFile] = File(...),
    _admin: Usuario = Depends(requiere_administrador),
    sesion: Session = Depends(obtener_sesion),
):
    """Acepta la carga y la persiste en una sola transacción."""
    contenidos = await _leer_archivos(archivos)
    informe = confirmar_carga(
        sesion,
        contenidos,
        fecha_objetivo_demo,
        fecha_referencia_stock,
        clave_importacion.strip(),
        skus_curados(),
        puerto_recetas=ServicioRecetasM01(),
        puerto_inventario=ServicioInventarioV01(),
    )
    sesion.commit()
    return {
        "datos": {
            "estado": informe.estado,
            "ya_estaba_cargada": informe.ya_estaba_cargada,
            "productos": informe.productos,
            "ventas_diarias": informe.ventas_diarias,
            "importacion_id": informe.importacion_id,
            "ingredientes": informe.ingredientes,
            "lineas_receta": informe.recetas,
            "movimientos_apertura": informe.movimientos_apertura,
            "pendiente_de": informe.pendiente_de,
        }
    }
