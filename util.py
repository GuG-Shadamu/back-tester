import asyncio
from collections.abc import Mapping
import logging
from typing import Any


class TaskAdapter(logging.LoggerAdapter):
    task_count = 1

    def __init__(self, logger, task_num):
        super().__init__(logger, {})
        self.task_id = self.__class__.task_count
        self.__class__.task_count += 1

    def process(self, msg, kwargs):
        return f"[task {self.task_id}] {msg}", kwargs


def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    logFormatter = logging.Formatter(
        "%(asctime)s [%(levelname)-5.5s]  %(message)s")

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)

    logger.addHandler(consoleHandler)
    return logger
