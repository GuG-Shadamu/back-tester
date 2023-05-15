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


class OHLCBarFeed(DataFeed):
    def __init__(self, bus: EventBus, OHLCData: object) -> None:
        self.bus = bus
        self.OHLCData = OHLCData

    async def start(self):
        LOG.info(f"{self} process starting...")
        while True:
            LOG.debug("feeding")
            await asyncio.sleep(2)
            bar = next(self.OHLCData.get_bars())
            if bar is None:
                break
            event = Event(type=EventType.BAR, payload=bar)
            LOG.debug(f"OHLCBarFeed pushed {event}")
            await self.bus.push(event)
