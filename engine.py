# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-04-16 13:31:08
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-05-16 18:13:32


from __future__ import annotations

from typing import List
import asyncio

from event_bus import EventBus
from execution import DummyExecution, Execution
from model import EventType, Asset, AssetType
from data.core import DataFeed, OHLCBarFeed
from data_handler import OHLCData

from log_utility import TaskAdapter, setup_logger
from quart_handle import register_ws_route, ws
from inspect import iscoroutinefunction

from strategy import Strategy
from view import View, LiveChart

LOG = TaskAdapter(setup_logger(), {})



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
        await asyncio.sleep(3)
        await self.bus.start()
        while self.running_event.is_set():
            try:
                await asyncio.gather(*self.tasks)
            except (KeyboardInterrupt, asyncio.exceptions.CancelledError):
                print("Engine CancelledError")
            finally:
                await self.stop()


async def main():
    bus = EventBus()
    strategy = Strategy(bus)
    data_ohlc = OHLCData.from_csv_file(
        Asset(AssetType.FX, "USDCAD"), "data_example/DAT_ASCII_USDCAD_M1_202304.csv"
    )
    feed = OHLCBarFeed(bus, OHLCData=data_ohlc, push_freq=1)
    execution = DummyExecution(bus)
    live_chart = LiveChart(bus)
    register_ws_route(live_chart.app, "/ws", ws, live_chart)

    engine = Engine(bus, strategy, feed, execution, live_chart)
    await engine.run()


if __name__ == "__main__":
    try:
        asyncio.run(main(), debug=True)
    except KeyboardInterrupt:
        print("Program interrupted. Exiting...")
