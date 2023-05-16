# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-05-16 17:51:50
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-05-16 17:52:41


from model import EventType, Order, Bar, Asset, AssetType, OrderType, Event
from event_bus import EventBus
from log_utility import TaskAdapter, setup_logger


LOG = TaskAdapter(setup_logger(), {})

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
