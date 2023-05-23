"""
    Application worker (Celery).

    Used for scheduled tasks (Using celery-beat-schedule)
    and background tasks.

    Currently worker uses Redis as broker && backend,
    there is alternative using AMQP (e.g RabbitMQ),
    but this is currently not planned.
"""
import os

from app.database.core import SessionLocal
from celery import Celery
from celery.schedules import crontab
from celery.utils.log import get_task_logger

worker_cache_dsn = os.environ.get("CACHE_DSN", "redis://cache:6379/")
worker = Celery(__name__, broker=worker_cache_dsn, backend=worker_cache_dsn)
logger = get_task_logger(__name__)
worker.conf.beat_schedule = {
    "truncate_oauth_codes": {
        "task": "truncate_oauth_codes",
        "schedule": crontab(minute=0, hour=0),
        "args": (),
    },
    "refresh_subscriptions": {
        "task": "truncate_oauth_codes",
        "schedule": crontab(minute=0, hour=0),
        "args": (),
    },
}


@worker.task(name="truncate_oauth_codes")
def truncate_oauth_codes():
    logger.info("Truncating oauth codes database table...")
    with SessionLocal() as db:
        db.execute("TRUNCATE TABLE oauth_codes RESTART IDENTITY;")
    logger.info("Finished truncating oauth codes database table!")
    return True


@worker.task(name="refresh_subscriptions")
def refresh_subscriptions():
    return True
