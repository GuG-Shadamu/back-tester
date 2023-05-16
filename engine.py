# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-04-16 13:31:08
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-05-16 04:44:18


from __future__ import annotations  # the FUTURE of annotation...hah
import json

from typing import List
from abc import ABC, abstractmethod
import asyncio
from quart import Quart, websocket

from event_bus import EventBus
from model import Event, EventType, Bar, Order, OrderType, Asset, AssetType
from data.core import DataFeed, OHLCBarFeed
from data_handler import OHLCData

from log_utility import TaskAdapter, setup_logger
from quart_try import register_ws_route, ws
from inspect import iscoroutinefunction

LOG = TaskAdapter(setup_logger(), {})
app = Quart(__name__)


class Engine:
    def __init__(
        self,
        bus: EventBus,
        strategy: Strategy,
        feed: DataFeed,
        execution: Execution,
        view: View = None,
    ):
        self.bus = bus
        self.strategy = strategy
        self.feed = feed
        self.execution = execution
        self.view = view

        self.running_event = asyncio.Event()
        self.loop = asyncio.get_event_loop()
        self.tasks: List[asyncio.Task] = list()
        self.stops: List[callable] = list()

    async def stop(self):
        LOG.info("Engine stopping")
        self.running_event.clear()  # Clear the event, which will stop the task.
        for _callable in self.stops:
            if iscoroutinefunction(_callable):
                await _callable()
            else:
                _callable()
        for task in self.tasks:
            task.cancel()

        LOG.info("Engine stopped")

    async def run(self):
        # subs
        self.bus.subscribe(EventType.BAR, self.strategy.on_bar)
        self.bus.subscribe(EventType.BAR, self.strategy.on_bar)
        self.bus.subscribe(EventType.ORDER_CREATE, self.execution.on_order_create)
        if self.view is not None:
            self.bus.subscribe(EventType.BAR, self.view.on_bar)
            # self.bus.subscribe(EventType.ORDER_CREATE, self.view.on_order_create)

        self.running_event.set()  # Set the event, meaning that the task is running.

        if self.view is not None:
            self.tasks.append(self.loop.create_task(self.view.start()))

        self.tasks.append(self.loop.create_task(self.bus.start()))
        self.stops.append(self.bus.stop)
        self.tasks.append(self.loop.create_task(self.feed.start()))
        self.stops.append(self.feed.stop)
        await self.bus.start()
        while self.running_event.is_set():
            try:
                await asyncio.gather(*self.tasks)
            except (KeyboardInterrupt, asyncio.exceptions.CancelledError):
                print("Engine CancelledError")
            finally:
                await self.stop()


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


class View(ABC):
    @abstractmethod
    def on_bar(self, bar: Bar):
        ...

    @abstractmethod
    def on_order_create(self, order: Order):
        ...


class LiveChart(View):
    def __init__(self, bus: EventBus, port: int = 5000) -> None:
        self.bus = bus
        self.running_event = asyncio.Event()
        self.port = port
        self.connections = set()

    def add_connection(self, connection):
        self.connections.add(connection)

    def remove_connection(self, connection):
        self.connections.remove(connection)

    async def start(self):
        LOG.info(f"{self} process starting...")
        await app.run_task(port=self.port)

    async def stop(self):
        # TODO: stop websocket server
        # Currently, Ctrl+C does not work
        LOG.info(f"{self} process stopping...")
        self.running_event.clear()
        await app.shutdown()

    async def on_bar(self, bar: Bar):
        bar_send = {
            "time": bar.timestamp.isoformat(),
            "open": bar.open,
            "high": bar.high,
            "low": bar.low,
            "close": bar.close,
            "volume": bar.volume,
        }
        for connection in self.connections:
            await connection.send(json.dumps(bar_send))
        LOG.info(f"LiveChart sent {bar}")

    async def on_order_create(self, order: Order):
        LOG.info(f"LiveChart reveived {order}")
        LOG.info(f"Plotting order ...")


async def main():
    bus = EventBus()
    strategy = Strategy(bus)
    data_ohlc = OHLCData.from_csv_file(
        Asset(AssetType.FX, "USDCAD"), "data_example/DAT_ASCII_USDCAD_M1_202304.csv"
    )
    feed = OHLCBarFeed(bus, OHLCData=data_ohlc)
    execution = DummyExecution(bus)
    view = LiveChart(bus)
    register_ws_route(app, "/ws", ws, view)

    engine = Engine(bus, strategy, feed, execution, None)
    await engine.run()


if __name__ == "__main__":
    try:
        asyncio.run(main(), debug=True)
    except KeyboardInterrupt:
        print("Program interrupted. Exiting...")
