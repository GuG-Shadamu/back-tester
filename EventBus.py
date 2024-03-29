from engine import EventHandler
from log import LOG
from model import Event

import zmq
import asyncio
from datetime import datetime
from typing import List


class EventBus:
    def __init__(self, sample_freq: float = 0.1):
        self.sample_freq = sample_freq

        self.running_event = asyncio.Event()
        self.events: asyncio.Queue[Event] = asyncio.Queue()

        context = zmq.Context()
        self.socket = context.socket(zmq.ROUTER)
        self.socket.bind("ipc:///tmp/master")

        self.event_handlers: List[EventHandler] = list()

        self.timestamp_diff = None

    def subscribe(self, event_handler: EventHandler):
        LOG.info(f"EventBus subscribing {event_handler}")
        self.event_handlers.append(event_handler)

    def update_timestamp(self, timestamp: datetime):
        if self.timestamp_diff is None:
            self.timestamp_diff = datetime.now() - timestamp
            return

        if self.get_timestamp() < timestamp:
            self.timestamp_diff = datetime.now() - timestamp
            return

    def get_timestamp(self):
        if self.timestamp_diff is None:
            LOG.warning(f"EventBus timestamp is None")
        return datetime.now() - self.timestamp_diff

    async def push(self, event: Event):
        if event.timestamp is not None:
            self.update_timestamp(event.timestamp)

        await self.events.put(event)

    async def start_simulation(self):
        """blocking run"""
        self.running_event.set()  # Set the event, meaning that the task is running.
        try:
            while self.running_event.is_set():
                identity, message = self.socket.recv_multipart()
                event = Event.from_json(message)
                
                if self.events.qsize() > 0:
                    event = await self.events.get()
                    # TODO: Handle END event
                    for handler in self.event_handlers:
                        await handler.on_event(event)
                await asyncio.sleep(self.sample_freq)
        except asyncio.CancelledError:
            self.stop()

    async def start_real_time(self):
        # TODO: implement
        pass

    def stop(self):
        if self.running_event.is_set():
            LOG.info(f"Event Bus process stopping")
            self.running_event.clear()  # Clear the event, which will stop the task.
            LOG.info(f"Event Bus process stopped")
