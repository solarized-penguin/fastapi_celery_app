from celery import Celery

from core import get_logger
from core import get_settings

logger = get_logger(__name__)

worker = Celery(
    main=get_settings().workers.mail.name,
    broker=get_settings().mongo_db.mongo_dsn,
    backend=get_settings().mongo_db.mongo_dsn,
)


@worker.task(name="send", bind=True)
def send(self, msg): ...
