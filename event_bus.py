# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-04-16 13:31:08
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-06-05 20:10:23

import asyncio
from collections import defaultdict

from typing import Dict, List, Callable

from engine import EventHandler
from model import EventType, Event
from log import TaskAdapter, setup_logger

LOG = TaskAdapter(setup_logger(), {})


class EventBus:
    def __init__(self, sample_freq: float = 0.1):
        # topic:
        self.topics: Dict[EventType, List[Callable]] = defaultdict(
            list
        )  # TODO: Could be a priority queue

        self.running_event = asyncio.Event()
        self.events: asyncio.Queue[Event] = asyncio.Queue()

        self.sample_freq = sample_freq
        self.event_handlers: List[EventHandler] = list()

    def subscribe(self, event_handler: EventHandler):
        LOG.info(f"EventBus subscribing {event_handler}")
        self.event_handlers.append(event_handler)

    async def push(self, event: Event):
        await self.events.put(event)

    async def start(self):
        """blocking run"""
        self.running_event.set()  # Set the event, meaning that the task is running.
        try:
            while self.running_event.is_set():
                if self.events.qsize() > 0:
                    event = await self.events.get()
                    for handler in self.event_handlers:
                        await handler.on_event(event)
                await asyncio.sleep(self.sample_freq)
        except asyncio.CancelledError:
            self.stop()

    def stop(self):
        if self.running_event.is_set():
            LOG.info(f"Event Bus process stopping")
            self.running_event.clear()  # Clear the event, which will stop the task.
            LOG.info(f"Event Bus process stopped")
