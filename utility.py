# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-05-22 10:43:01
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-05-23 13:54:34
import inspect

from log import TaskAdapter, setup_logger

LOG = TaskAdapter(setup_logger(), {})


def check_running(func):
    if inspect.iscoroutinefunction(func):

        async def async_wrapper(self, *args, **kwargs):
            if self.running:
                return await func(self, *args, **kwargs)
            else:
                LOG.warning(f"{self} is not running")

        return async_wrapper

    else:

        def wrapper(self, *args, **kwargs):
            if self.running:
                return func(self, *args, **kwargs)
            else:
                LOG.warning(f"{self} is not running")

        return wrapper


def check_async_running(func):
    async def wrapper(self, *args, **kwargs):
        if self.running_event.set():
            return await func(self, *args, **kwargs)
        else:
            LOG.warning(f"{self} is not running")

    return wrapper
