import os

from celery import Celery

redis_url = os.environ["REDIS_URL"]
celery_app = Celery("foodsave", broker=redis_url, backend=redis_url)
celery_app.conf.update(
    task_track_started=True,
    timezone="UTC",
    enable_utc=True,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
    broker_connection_timeout=5,
    broker_transport_options={"socket_connect_timeout": 5, "socket_timeout": 5},
    task_publish_retry=False,  # El lease durable gobierna las publicaciones inciertas.
    beat_schedule={
        "despachar-programaciones-demo": {
            "task": "foodsave.despachar_pendientes",
            "schedule": 30.0,
            "options": {"expires": 30},
        },
    },
)


@celery_app.task(name="foodsave.despachar_pendientes", ignore_result=True)
def despachar_programaciones_demo():
    from app.workers.motor import despachar_pendientes

    return despachar_pendientes(lambda ejecucion_id, token: ejecutar_automatizacion.delay(ejecucion_id, token))


@celery_app.task(name="foodsave.ejecutar_automatizacion", ignore_result=True)
def ejecutar_automatizacion(ejecucion_id: int, token: str):
    from app.workers.motor import ejecutar

    return ejecutar(ejecucion_id, token)


@celery_app.task(name="foodsave.prueba")
def tarea_prueba(valor: str) -> dict[str, str]:
    return {"resultado": valor}
