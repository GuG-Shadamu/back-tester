# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-04-16 13:31:08
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-05-22 22:24:23


from __future__ import annotations

from typing import List
import asyncio

from event_bus import EventBus
from log_utility import TaskAdapter, setup_logger
from engine_components import EngineService, EventHandler


LOG = TaskAdapter(setup_logger(), {})


# for simulation
# the data feed runs in a separate thread
class Engine:
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

        await asyncio.gather(*self.tasks)

    def stop(self):
        LOG.info("Engine stopping")
        self.running_event.clear()  # Clear the event, which will stop the task.

        for task in self.tasks:
            task.cancel()

        self.tasks.clear()

        self.bus.stop()
        for service in self.engine_services:
            service.stop()
