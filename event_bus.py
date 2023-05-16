# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-04-16 13:31:08
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-05-16 04:46:46

from __future__ import annotations

from collections import defaultdict
import asyncio
from typing import Dict, List, Callable
from inspect import iscoroutinefunction

from model import EventType, Event

from log_utility import TaskAdapter, setup_logger

LOG = TaskAdapter(setup_logger(), {})


class EventBus:
    def __init__(self, sample_freq: float = 0.1):
        # topic:
        self.topics: Dict[EventType, List[Callable]] = defaultdict(
            list
        )  # TODO: Could be a priority queue

        self.events: asyncio.Queue[Event] = asyncio.Queue()
        self.sample_freq = sample_freq
        self.running_event = asyncio.Event()

    def subscribe(self, event_type: EventType, callback: Callable):
        LOG.debug(f"Subscribe {event_type} with {callback}")
        # TODO: could be duplicated callbacks.
        self.topics[event_type].append(callback)

    async def push(self, event: Event):
        await self.events.put(event)

    async def start(self):
        """blocking run"""
        self.running_event.set()  # Set the event, meaning that the task is running.

        while self.running_event.is_set():
            while True:
                if self.events.qsize() > 0:
                    event = await self.events.get()
                    _callables = self.topics[event.type]
                    for _callable in _callables:
                        if iscoroutinefunction(_callable):
                            await _callable(event.payload)
                        else:
                            _callable(event.payload)
                await asyncio.sleep(self.sample_freq)

    def stop(self):
        self.running_event.clear()  # Clear the event, which will stop the task.
        LOG.info(f"{self} process stopped")
