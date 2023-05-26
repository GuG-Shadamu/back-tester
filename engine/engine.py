# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-05-23 14:09:26
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-05-26 03:28:43

# for simulation
# the data feed runs in a separate thread

from __future__ import annotations

import asyncio

from typing import List

from event_bus import EventBus
from log import TaskAdapter, setup_logger
from .core import EngineService, EventHandler

LOG = TaskAdapter(setup_logger(), {})


class BackTestEngine:
    def __init__(
        self,
        bus: EventBus,
        services: List[EngineService],
        event_handlers: List[EventHandler],
    ):
        self.bus = bus
        self.event_handlers: List[EventHandler] = event_handlers
        self.engine_services: List[EngineService] = services

        self.running_event = asyncio.Event()
        self.loop = asyncio.get_event_loop()
        self.tasks: List[asyncio.Task] = list()

        for handler in self.event_handlers:
            self.bus.subscribe(handler)

    async def start(self):
        # subs
        self.running_event.set()  # Set the event, meaning that the task is running.
        asyncio.create_task(self.bus.start())

        for event_handler in self.event_handlers:
            event_handler.start()

        self.tasks.append(asyncio.create_task(self.bus.start()))

        for service in self.engine_services:
            self.tasks.append(asyncio.create_task(service.start()))

        try:
            await asyncio.gather(*self.tasks)
        except asyncio.CancelledError:
            self.stop()

    def stop(self):
        LOG.info("Engine stopping")
        self.running_event.clear()  # Clear the event, which will stop the task.

        for task in self.tasks:
            task.cancel()

        self.tasks.clear()

        self.bus.stop()
        for service in self.engine_services:
            service.stop()
        LOG.info("Engine stopped")
