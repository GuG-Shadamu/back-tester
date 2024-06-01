from collections import defaultdict
from typing import DefaultDict

from engine.EventHandler import EventHandler
from EventBus import EventBus
from model import Asset, AssetType, Bar, Event, EventType, Order, OrderType
from log import LOG


from strategy.Strategy import Strategy


class DummyStrategy(Strategy):
    def __init__(self, bus: EventBus) -> None:
        super().__init__(bus)
        self.min_price_book: dict[Asset, float] = dict()

    @EventHandler.register(EventType.BAR)
    async def on_bar(self, bar: Bar):
        LOG.debug(f"Strategy reveived {bar} ")
        if bar.asset not in self.min_price_book:
            self.min_price_book[bar.asset] = bar.close
        else:
            self.min_price_book[bar.asset] = min(
                self.min_price_book[bar.asset], bar.close
            )

        if bar.close > self.min_price_book[bar.asset] * 1.001:
            order = Order(
                asset=bar.asset,
                amount=-10000,
                type=OrderType.MARKET,
            )
            await self.create_order(order)

        elif bar.close < self.min_price_book[bar.asset] * 0.999:
            order = Order(
                asset=bar.asset,
                amount=10000,
                type=OrderType.MARKET,
            )
            await self.create_order(order)

    async def create_order(self, order: Order):
        event = Event(EventType.ORDER_CREATE, data=order)
        LOG.debug(f"Strategy create {order = }")
        await self.bus.push(event)
