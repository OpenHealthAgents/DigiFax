"""
celery_app.py
Celery application bootstrap loader linking broker and result backends.
"""

from celery import Celery
from src.infrastructure.config import settings

# Initialize Celery app instance
app = Celery(
    "medingest",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["src.infrastructure.messaging.tasks"]
)

# Optional configuration settings overrides
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,
)

if __name__ == "__main__":
    app.start()
