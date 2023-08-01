"""
    Application worker (Celery).

    Used for scheduled tasks (Using celery-beat-schedule)
    and background tasks.

    Currently worker uses Redis as broker && backend,
    there is alternative using AMQP (e.g RabbitMQ),
    but this is currently not planned.
    ?TODO: RabbitMQ?
"""

import os

from celery.utils.log import get_task_logger
from celery.schedules import crontab
from celery import Celery
from app.database.core import SessionLocal

worker_cache_dsn = os.environ.get("CACHE_DSN", "redis://cache:6379/")
worker = Celery(__name__, broker=worker_cache_dsn, backend=worker_cache_dsn)
worker.conf.broker_connection_retry_on_startup = True
logger = get_task_logger(__name__)
worker.conf.beat_schedule = {
    "truncate_oauth_codes": {
        "task": "truncate_oauth_codes",
        "schedule": crontab(minute=0, hour=0),
        "args": (),
    },
}


@worker.task(name="truncate_oauth_codes")
def truncate_oauth_codes():
    """
    Task that will be executed periodically
    and truncate the oauth_codes table that is not required to store long history.
    TODO: Use redis.
    """
    logger.info("[truncate_oauth_codes] Truncating oauth codes database table...")
    with SessionLocal() as db:
        db.execute("TRUNCATE TABLE oauth_codes RESTART IDENTITY;")
    logger.info(
        "[truncate_oauth_codes] Finished truncating oauth codes database table!"
    )
    return True
