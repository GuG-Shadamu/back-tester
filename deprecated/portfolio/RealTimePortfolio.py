from engine.EventHandler import EventHandler
from EventBus import EventBus
from model import (
    Asset,
    Bar,
    Event,
    EventType,
    Order,
    PortfolioConstituent,
    PortfolioMetrics,
)
from log import LOG


from portfolio.PortfolioAnalyzer import PortfolioAnalyzer


class RealTimePortfolio(EventHandler):
    def __init__(
        self,
        bus: EventBus,
        initial_cash: float = 0.0,
        portfolio_analyzer: bool = False,
    ):
        # TODO: margin account
        super().__init__(bus)
        self.initial_value = initial_cash

        self.asset_book: dict[Asset, PortfolioConstituent] = dict()
        self.metrics: PortfolioMetrics = None
        if portfolio_analyzer:
            self.portfolio_analyzer = PortfolioAnalyzer(bus)
            self.bus.subscribe(self.portfolio_analyzer)
        else:
            self.portfolio_analyzer = None

    def start(self):
        if self.portfolio_analyzer:
            self.portfolio_analyzer.start()
        return super().start()

    def end(self):
        if self.portfolio_analyzer:
            self.portfolio_analyzer.end()
        return super().end()

    @EventHandler.register(EventType.BAR)
    async def on_bar(self, bar: Bar):
        if self.metrics is None:
            self.metrics = PortfolioMetrics(mtm=self.initial_value)

        if bar.asset not in self.asset_book:
            return

        # update metrics
        self.metrics.mtm += (
            bar.close * self.asset_book[bar.asset].amount
            - self.asset_book[bar.asset].mtm
        )

        # update asset book
        self.asset_book[bar.asset].price = bar.close
        self.asset_book[bar.asset].mtm = bar.close * self.asset_book[bar.asset].amount

        await self.update_portfolio_constituent(self.asset_book[bar.asset])
        await self.update_portfolio_metrics()

    @EventHandler.register(EventType.ORDER_FILLED)
    async def on_order_filled(self, order: Order):
        # update metrics
        LOG.debug(f"Portfolio recieved filled {order}")
        self.metrics.mtm -= order.fee
        self.metrics.timestamp = self.bus.get_timestamp()

        # update asset book
        if order.asset not in self.asset_book:
            self.asset_book[order.asset] = PortfolioConstituent(
                asset=order.asset,
                price=order.price,
                amount=order.amount,
                mtm=order.price * order.amount,
            )
        else:
            self.asset_book[order.asset].amount += order.amount
            self.asset_book[order.asset].mtm = (
                self.asset_book[order.asset].price * self.asset_book[order.asset].amount
            )
        await self.update_portfolio_constituent(self.asset_book[order.asset])
        await self.update_portfolio_metrics()

    async def update_portfolio_metrics(self):
        LOG.debug(f"Portfolio updated: {self.metrics}")
        await self.bus.push(
            Event(
                EventType.PORTFOLIO_METRICS_UPDATE,
                data=self.metrics,
            )
        )

    async def update_portfolio_constituent(self, constituent: PortfolioConstituent):
        LOG.debug(f"Portfolio constituent updated: {constituent}")
        await self.bus.push(
            Event(
                EventType.PORTFOLIO_CONSTITUENT_UPDATE,
                data=constituent,
            )
        )
