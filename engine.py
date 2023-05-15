from __future__ import annotations  # the FUTURE of annotation...hah

from typing import List
from abc import ABC, abstractmethod
import asyncio
from event_bus import EventBus
from model import Event, EventType, Bar, Order, OrderType, Asset, AssetType
from data.core import DataFeed, DummyBarFeed

from log_utility import TaskAdapter, setup_logger


LOG = TaskAdapter(setup_logger(), {})


class Engine:
    def __init__(
        self, bus: EventBus, strategy: Strategy, feed: DataFeed, execution: Execution
    ):
        self.bus = bus
        self.strategy = strategy
        self.feed = feed
        self.execution = execution

        self.running = False
        self.loop = asyncio.get_event_loop()
        self.tasks: List[asyncio.Task] = list()

    async def run(self):
        # subs
        self.bus.subscribe(EventType.BAR, self.strategy.on_bar)
        self.bus.subscribe(EventType.ORDER_CREATE, self.execution.on_order_create)

        if not self.running:
            self.running = True
            self.tasks.append(self.loop.create_task(self.bus.start()))
            self.tasks.append(self.loop.create_task(self.feed.start()))

        await asyncio.gather(*self.tasks)


class Execution(ABC):
    @abstractmethod
    def submit_order(self, order: Order) -> int:
        ...

    @abstractmethod
    def cancel_order(self, order_id: int):
        ...

    @abstractmethod
    def modify_order(self, order_id: int, order: Order):
        ...

    @abstractmethod
    def on_order_create(self, order: Order):
        LOG.info(f"Execution recieved {order =  }")
        ...

    @abstractmethod
    def start(self):
        ...


class DummyExecution(Execution):
    def __init__(self, bus: EventBus) -> None:
        self.bus = bus

    def submit_order(self, order: Order) -> int:
        return super().submit_order(order)

    def cancel_order(self, order_id: int):
        return super().cancel_order(order_id)

    def modify_order(self, order_id: int, order: Order):
        return super().modify_order(order_id, order)

    def on_order_create(self, order: Order):
        return super().on_order_create(order)

    def start(self):
        return super().start()


# 2. I write down strategy class
class Strategy:
    def __init__(self, bus: EventBus) -> None:
        self.bus = bus

    async def on_bar(self, bar: Bar):
        LOG.info(f"Strategy reveived {bar}")
        LOG.info(f"Computing some fancy signal ...")
        LOG.info(f"Submit Order...")
        await self.submit_order()

    async def submit_order(self):
        order = Order(
            asset=Asset(AssetType.CASH, name="Bitcoin"),
            type=OrderType.MARKET,
            price=-1,
            amount=1.0,
        )
        event = Event(EventType.ORDER_CREATE, payload=order)
        await self.bus.push(event)


async def main():
    bus = EventBus()
    strategy = Strategy(bus)
    feed = DummyBarFeed(bus)
    execution = DummyExecution(bus)
    engine = Engine(bus, strategy, feed, execution)

    await engine.run()


asyncio.run(main())
