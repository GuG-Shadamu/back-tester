# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-05-23 13:36:43
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-06-06 22:15:43


from datetime import datetime, timedelta
from engine import EventHandler
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
from log import TaskAdapter, setup_logger
from .core import Strategy

LOG = TaskAdapter(setup_logger(), {})


class DummyStrategy(Strategy):
    def __init__(self, bus: EventBus) -> None:
        super().__init__(bus)

    @EventHandler.register(EventType.BAR)
    async def on_bar(self, bar: Bar):
        LOG.debug(f"Strategy reveived {bar} ")
        LOG.info(f"Submit Order...")
        order = Order(
            asset=Asset(AssetType.CASH, name="Bitcoin"),
            type=OrderType.MARKET,
            price=-1,
            amount=1.0,
        )
        await self.submit_order(order)

    async def submit_order(self, order: Order):
        event = Event(EventType.ORDER_SUBMIT, payload=order)
        await self.bus.push(event)
