# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-05-16 17:51:50
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-05-22 22:25:20


from engine_components import EventHandler
from model import (
    EventType,
    Order,
    Bar,
    Asset,
    AssetType,
    OrderType,
    Event,
)
from event_bus import EventBus
from log_utility import TaskAdapter, setup_logger
from utility import check_running


LOG = TaskAdapter(setup_logger(), {})


class Strategy(EventHandler):
    pass


class DummyStrategy(Strategy):
    name = "DummyStrategy"

    def __init__(self, bus: EventBus) -> None:
        self.bus = bus
        self.running = False
        self.handler_dict: dict[EventType, callable] = dict()
        self.register(EventType.BAR, self.on_bar)

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    @check_running
    async def on_bar(self, bar: Bar):
        LOG.debug(f"Strategy reveived {bar}")
        LOG.info(f"Submit Order...")
        await self.submit_order()

    @check_running
    async def submit_order(self):
        order = Order(
            asset=Asset(AssetType.CASH, name="Bitcoin"),
            type=OrderType.MARKET,
            price=-1,
            amount=1.0,
        )
        event = Event(EventType.ORDER_CREATE, payload=order)
        await self.bus.push(event)
