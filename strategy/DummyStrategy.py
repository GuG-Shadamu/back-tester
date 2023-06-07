from engine.EventHandler import EventHandler
from EventBus import EventBus
from model import Asset, AssetType, Bar, Event, EventType, Order, OrderType
from log import LOG


from strategy.Strategy import Strategy


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
