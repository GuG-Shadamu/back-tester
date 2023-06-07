# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-06-06 22:49:06
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-06-06 22:49:09

from EventBus import EventBus
from engine.EngineService import EngineService
from engine.EventHandler import EventHandler
from log import LOG


import asyncio
from typing import List


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
        asyncio.create_task(self.bus.start_simulation())

        for event_handler in self.event_handlers:
            event_handler.start()

        self.tasks.append(asyncio.create_task(self.bus.start_simulation()))

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
