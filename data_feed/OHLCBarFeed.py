from data_feed.DataFeed import DataFeed
from EventBus import EventBus
from log import LOG
from model import Event, EventType


import asyncio
import time


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
                    self.bus.push(
                        Event(type=EventType.END, payload=None, timestamp=None)
                    )
                await asyncio.sleep(self.push_freq)

                event = Event(type=EventType.BAR, payload=bar, timestamp=bar.timestamp)
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
