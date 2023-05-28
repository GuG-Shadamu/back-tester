# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-04-16 13:31:08
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-05-27 18:07:39


from __future__ import annotations

from abc import abstractmethod
import asyncio
import time

from engine import EngineService
from event_bus import EventBus
from model import Event, EventType
from log import TaskAdapter, setup_logger

LOG = TaskAdapter(setup_logger(), {})


class DataFeed(EngineService):
    @abstractmethod
    def start(self):
        ...

    @abstractmethod
    def stop(self):
        ...


class OHLCBarFeed(DataFeed):
    def __init__(self, bus: EventBus, OHLCData: object, push_freq: float = 5) -> None:
        self.bus = bus
        self.OHLCData = OHLCData
        self.push_freq = push_freq
        self.running_event = asyncio.Event()

    async def start(self):
        LOG.info(f"{self} process starting...")

        bars = self.OHLCData.get_bars()
        self.running_event.set()  # Set the event, meaning that the task is running.
        try:
            while self.running_event.is_set():
                bar = next(bars)
                if not bar:
                    break
                await asyncio.sleep(self.push_freq)

                event = Event(type=EventType.BAR, payload=bar)
                LOG.debug(f"OHLCBarFeed pushed {event}")
                await self.bus.push(event)

        except (asyncio.CancelledError, KeyboardInterrupt):
            pass
        finally:
            self.stop()

    def stop(self):
        if self.running_event.is_set():
            self.running_event.clear()  # Clear the event, which will stop the task.
            time.sleep(0.1)
            LOG.info(f"OHLCBarFeed process stopped")
