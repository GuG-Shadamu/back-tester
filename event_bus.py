from __future__ import annotations

from collections import defaultdict
import asyncio
from typing import Dict, List, Callable
import logging

from model import EventType, Event

LOG = logging.getLogger(__name__)


class EventBus:

    def __init__(self, sample_freq: float = 0.2):

        # topic:
        self.topics: Dict[EventType, List[Callable]] = defaultdict(
            list)   # TODO: Could be a priority queue

        self.events: List[Event] = list()
        self.sample_freq = sample_freq
        self.running = False
        self.loop = asyncio.get_event_loop()
        self.task = None

    def subscribe(self, event_type: EventType, callback: Callable):
        LOG.debug(f"Subscribe {event_type} with {callback}")
        # TODO: could be duplicated callbacks.
        self.topics[event_type].append(callback)

    def push(self, event: Event):
        self.events.append(event)

    async def blocking_run(self):
        """ blocking run """
        while self.running:
            while self.events:
                event = self.events.pop()
                _callables = self.topics[event.type]
                for _callable in _callables:
                    _callable(event.payload)

            # sample frequency to avoid throttling the CPU.
            await asyncio.sleep(self.sample_freq)

    def start(self):
        if not self.running:
            self.running = True
            self.task = self.loop.create_task(self.blocking_run())

    def stop(self):
        if self.running:
            self.running = False
            self.task.cancel()
            self.task = None


async def main():
    a = EventBus()
    a.start()
    await asyncio.sleep(5)
    a.stop()

asyncio.run(main())
