from __future__ import annotations

from collections import defaultdict
import asyncio
from typing import Dict, List, Callable
import logging
from inspect import iscoroutinefunction

from model import EventType, Event

from util import TaskAdapter, setup_logger

LOG = TaskAdapter(setup_logger(), {})


class EventBus:

    def __init__(self, sample_freq: float = 0.2):

        # topic:
        self.topics: Dict[EventType, List[Callable]] = defaultdict(
            list)   # TODO: Could be a priority queue

        self.events: asyncio.Queue[Event] = asyncio.Queue()
        self.sample_freq = sample_freq

    def subscribe(self, event_type: EventType, callback: Callable):
        LOG.debug(f"Subscribe {event_type} with {callback}")
        # TODO: could be duplicated callbacks.
        self.topics[event_type].append(callback)

    async def push(self, event: Event):
        await self.events.put(event)

    async def start(self):
        """ blocking run """

        while True:

            while self.events:
                if self.events.qsize() > 0:
                    event = await self.events.get()
                    _callables = self.topics[event.type]
                    for _callable in _callables:
                        if iscoroutinefunction(_callable):
                            await _callable(event.payload)
                        else:
                            _callable(event.payload)
                LOG.info("running")  # why is this not working?!!
                await asyncio.sleep(self.sample_freq)
