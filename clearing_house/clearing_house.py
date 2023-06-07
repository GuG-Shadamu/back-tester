# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-06-06 16:28:24
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-06-06 22:54:27


# -*- coding: utf-8 -*-
# build a fake clearing house for back-testing and testing purpose

# from engine import EngineService
from collections import defaultdict
from datetime import datetime
from typing import DefaultDict

from engine.EventHandler import EventHandler
from EventBus import EventBus
from model import Asset, Event, EventType, Order


class FakeClearingHouse(EventHandler):
    def __init__(self, bus: EventBus, transaction_fee: float = 0.0):
        super().__init__(bus)
        price_book: DefaultDict[Asset, float] = defaultdict(float)
        current_time: datetime = None

    @EventHandler.register(EventType.BAR)
    def on_bar(self, bar, timestamp):
        # assume bar always provides the latest price
        self.current_time = bar.timestamp
        self.price_book[bar.asset] = bar.close

    @EventHandler.register(EventType.ORDER_SUBMIT)
    def on_order(self, order, timestamp):
        if order.type == "MARKET":
            price = self.price_book[order.asset]
            fee = price * order.amount * self.transaction_fee

            filled_order = Order(
                asset=order.asset,
                timestamp=self.current_time,
                type=order.type,
                price=price,
                amount=order.amount,
                fee=fee,
                filled=True,
            )

            event = Event(
                EventType.ORDER_EXECUTED,
                payload=filled_order,
            )
            self.bus.push(event)
