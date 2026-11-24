"""Aviso en la bandeja administrativa cuando una tarea en segundo plano falla definitivamente.

Solo se avisa el estado FALLIDA: agotó sus reintentos o tuvo un error que no se
reintenta. Un intento que pasa a REINTENTANDO no genera aviso. El aviso usa una
clave por ejecución, así que repetir la notificación no lo duplica.
"""
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.automatizaciones.modelos import EjecucionAutomatizacion, IntentoAutomatizacion
# Registra la tabla de avisos en los metadatos del worker, que no importa toda la aplicación.
from app.modules.operaciones.modelos import AvisoOperacion  # noqa: F401

TITULOS = {
    "GENERAR_PROPUESTA": "Falló la creación del plan y las compras",
    "PREPARAR_MODELO": "Falló el entrenamiento del modelo",
    "EVALUAR_MODELO": "Falló la evaluación del modelo",
    "EVALUAR_PRONOSTICO": "Falló la evaluación del pronóstico",
    "EVALUAR_PROMOCION": "Falló la evaluación de promociones",
}


def avisar_fallo_definitivo(sesion: Session, ejecucion: EjecucionAutomatizacion):
    """Registra el aviso en la misma transacción que cierra la ejecución; no hace commit."""
    if ejecucion.estado != "FALLIDA":
        return None
    from app.modules.operaciones.servicio import aviso

    intentos = sesion.scalar(select(func.count()).select_from(IntentoAutomatizacion)
                             .where(IntentoAutomatizacion.ejecucion_id == ejecucion.id)) or 0
    motivo = (ejecucion.mensaje_error or "Sin detalle del error.").strip()
    return aviso(sesion, f"tarea-fallida:{ejecucion.id}", TITULOS.get(ejecucion.tipo, "Falló una tarea automática"), {
        "ejecucion_id": ejecucion.id,
        "tipo": ejecucion.tipo,
        "descripcion": f"Tarea #{ejecucion.id} · {intentos} intento(s). {motivo[:600]}",
    })
