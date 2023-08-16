# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-06-06 16:28:24
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-08-15 17:36:53


# build a fake clearing house for back-testing and testing purpose

# from engine import EngineService
from collections import defaultdict
from datetime import datetime
from typing import DefaultDict

from engine.EventHandler import EventHandler
from EventBus import EventBus
from log import LOG
from model import Asset, Event, EventType, Order, OrderType


class SimpleClearingHouse(EventHandler):
    def __init__(self, bus: EventBus, transaction_fee: float = 0.0):
        super().__init__(bus)
        self.price_book: DefaultDict[Asset, float] = defaultdict(float)
        self.transaction_fee = transaction_fee

    @EventHandler.register(EventType.BAR)
    def on_bar(self, bar):
        # assume bar always provides the latest price
        self.price_book[bar.asset] = bar.close

    @EventHandler.register(EventType.ORDER_SUBMIT)
    async def on_order_submit(self, order):
        LOG.debug(f"SimpleClearingHouse recieved {order = }")
        filled = False
        if order.type == OrderType.MARKET:
            price = self.price_book[order.asset]
            fee = price * order.amount * self.transaction_fee
            filled = True

        elif order.type == OrderType.LIMIT:
            if order.price is None:
                LOG.error("LIMIT order must have a price")
                return

            if order.amount > 0 and order.price >= self.price_book[order.asset]:
                price = self.price_book[order.asset]
                fee = price * order.amount * self.transaction_fee
                filled = True

            elif order.amount < 0 and order.price <= self.price_book[order.asset]:
                price = self.price_book[order.asset]
                fee = price * order.amount * self.transaction_fee
                filled = True

        if filled:
            order.filled = True
            order.price = price
            order.fee = fee

            event = Event(
                EventType.ORDER_FILLED,
                payload=order,
            )
            LOG.debug(f"FakeClearingHouse filled {order = }")
            await self.bus.push(event)
