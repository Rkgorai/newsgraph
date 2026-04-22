from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

celery_app = Celery(
    "newsgraph_workers",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["workers.tasks.ingest"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# This is our cron scheduler (Celery Beat)
celery_app.conf.beat_schedule = {
    "fetch-news-every-15-mins": {
        "task": "workers.tasks.ingest.run_all_scrapers",
        "schedule": crontab(minute="*/15"),
    },
}