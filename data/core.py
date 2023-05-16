# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-04-16 13:31:08
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-05-16 04:33:55


from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from threading import Thread
from time import sleep
import asyncio

from event_bus import EventBus
from model import Bar, Event, EventType

from log_utility import TaskAdapter, setup_logger

LOG = TaskAdapter(setup_logger(), {})


class DataFeed(ABC):
    @abstractmethod
    def start(self):
        ...


class OHLCBarFeed(DataFeed):
    def __init__(self, bus: EventBus, OHLCData: object, sample_freq: float = 5) -> None:
        self.bus = bus
        self.OHLCData = OHLCData
        self.sample_freq = sample_freq
        self.running_event = asyncio.Event()

    async def start(self):
        LOG.info(f"{self} process starting...")
        if self.bus.sample_freq < self.sample_freq:
            self.sample_freq = self.bus.sample_freq

        bars = self.OHLCData.get_bars()
        self.running_event.set()  # Set the event, meaning that the task is running.
        while self.running_event.is_set():
            bar = next(bars)
            if not bar:
                break
            await asyncio.sleep(self.sample_freq)

            event = Event(type=EventType.BAR, payload=bar)
            LOG.debug(f"OHLCBarFeed pushed {event}")
            await self.bus.push(event)

    def stop(self):
        self.running_event.clear()  # Clear the event, which will stop the task.
        LOG.info(f"{self} process stopped")
