"""Compatibilidad de la frontera local E03 con el servicio conciliado.

La reserva y el bloqueo pertenecen a servicio.py. El argumento legado no
crea una segunda política de reintentos: una preparación activa se reutiliza.
"""
from sqlalchemy.orm import Session
from app.modules.automatizaciones.servicio import obtener_ejecucion
from app.modules.inicializacion.servicio import solicitar_preparacion


def solicitar_preparacion_modelo(sesion: Session, clave_reintento: str | None = None):
    estado = solicitar_preparacion(sesion)
    return obtener_ejecucion(sesion, estado.preparacion_ejecucion_id)
