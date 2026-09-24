import os

from celery import Celery

redis_url = os.environ["REDIS_URL"]
celery_app = Celery("foodsave", broker=redis_url, backend=redis_url)
celery_app.conf.update(task_track_started=True, timezone="UTC")


@celery_app.task(name="foodsave.prueba")
def tarea_prueba(valor: str) -> dict[str, str]:
    return {"resultado": valor}
