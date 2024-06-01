import logging


class TaskAdapter(logging.LoggerAdapter):
    task_count = 1

    def __init__(self, logger, task_num):
        super().__init__(logger, {})
        self.task_id = self.__class__.task_count
        self.__class__.task_count += 1

    def process(self, msg, kwargs):
        return f"[task {self.task_id}] {msg}", kwargs
