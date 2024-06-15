import logging
from .config import get_settings
from logging_loki import LokiQueueHandler
from multiprocessing import Queue
from celery.utils.log import get_task_logger


loki_handler = LokiQueueHandler(
    Queue(-1),
    url=get_settings().logging.loki_endpoint,
    tags={"app": get_settings().api.title},
    version=get_settings().logging.loki_handler_version,
)


def get_logger(name: str) -> logging.Logger:
    logger = get_task_logger(name)
    logger.setLevel(get_settings().logging.log_level)
    logger.addHandler(loki_handler)
    return logger
