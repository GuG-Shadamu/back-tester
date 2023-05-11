from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from threading import Thread
from time import sleep
import asyncio
import pandas as pd

from event_bus import EventBus
from model import Bar, Event, EventType

from log_utility import TaskAdapter, setup_logger

LOG = TaskAdapter(setup_logger(), {})


class DataFeed(ABC):

    @abstractmethod
    def start(self):
        ...


class BacktestBarFeed(DataFeed):

    def __init__(self, bus: EventBus, file: str) -> None:
        # TODO: Notice that we are repeating the pattern, need refactor more
        # TODO: We may need a clock to coordinate across different components, including data
        self.bus = bus
        self.thread = Thread(target=self._run)
        self.data = pd.read_parquet(file)  # blocking

    def _run(self):
        for row in self.data.iterrows():
            t, d = row
            bar = Bar(
                open=d['open'],
                high=d.high,
                low=d.low,
                close=d.close,
                volume=d.volume,
                timestamp=d.close_time
            )
            event = Event(
                type=EventType.BAR,
                payload=bar
            )
            LOG.info(f"Pushed {event}")
            self.bus.push(event)

    def start(self):
        self.thread.start()


class DummyBarFeed(DataFeed):
    # Does Bar feed needs to know EventBus?

    def __init__(self, bus: EventBus) -> None:
        self.bus = bus

    async def start(self):
        LOG.info(f"{self} process starting...")
        while True:
            LOG.debug("feeding")
            await asyncio.sleep(2)
            bar = Bar(
                open=100,
                high=200,
                low=100,
                close=100,
                volume=20000,
                timestamp=datetime.now()
            )
            event = Event(
                type=EventType.BAR,
                payload=bar
            )
            LOG.debug(f"DummyBarFeed pushed {event}")
            await self.bus.push(event)
