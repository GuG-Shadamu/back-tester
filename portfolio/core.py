# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-05-27 22:16:07
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-06-06 22:36:28
from collections import defaultdict
import polars as pl
import pandas as pd

from engine import EventHandler
from event_bus import EventBus
from model import Asset, Bar, Event, EventType, PortfolioConstituent, PortfolioMetrics

from log import TaskAdapter, setup_logger

LOG = TaskAdapter(setup_logger(), {})
# maintain two views of your portfolio: a 'real-time' view and a 'lagging' view.
# The real-time view processes events as they come in, ignoring the timestamps,
# while the lagging view processes events sorted by their timestamps.


class PortfolioAnalyzer(EventHandler):
    def __init__(self, bus: EventBus):
        super().__init__(bus)
        self.df_mtm = pl.DataFrame(
            {
                "timestamp": pl.Series([], dtype=pl.Datetime),
                "mtm": pl.Series([], dtype=pl.Float64),
            }
        )

        self.df_constituents: dict[Asset, pl.DataFrame] = defaultdict(
            lambda: pl.DataFrame(
                {
                    "asset": pl.Series([], dtype=pl.Object),
                    "timestamp": pl.Series([], dtype=pl.Datetime),
                    "price": pl.Series([], dtype=pl.Float64),
                    "amount": pl.Series([], dtype=pl.Float64),
                    "mtm": pl.Series([], dtype=pl.Float64),
                }
            )
        )

    @EventHandler.register(EventType.PORTFOLIO_CONSTITUENT_UPDATE)
    def update_df_constituents(self, constituent: PortfolioConstituent):
        LOG.debug(f"Portfolio constituent updated: {constituent.asset.name}")
        asset = constituent.asset
        self.df_constituents[asset] = self.df_constituents[asset].vstack(
            pl.DataFrame(
                {
                    "asset": pl.Series([asset], dtype=pl.Object),
                    "timestamp": pl.Series(
                        [self.bus.get_timestamp()], dtype=pl.Datetime
                    ),
                    "price": pl.Series([constituent.price], dtype=pl.Float64),
                    "amount": pl.Series([constituent.amount], dtype=pl.Float64),
                    "mtm": pl.Series([constituent.mtm], dtype=pl.Float64),
                }
            )
        )

    @EventHandler.register(EventType.PORTFOLIO_METRICS_UPDATE)
    def update_df_mtm(self, metrics: PortfolioMetrics):
        LOG.debug(f"Portfolio updated: {metrics}")
        self.df_mtm = self.df_mtm.vstack(
            pl.DataFrame(
                {
                    "timestamp": pl.Series(
                        [self.bus.get_timestamp()], dtype=pl.Datetime
                    ),
                    "mtm": pl.Series([metrics.mtm], dtype=pl.Float64),
                }
            )
        )


class RealTimePortfolio(EventHandler):
    def __init__(
        self,
        bus: EventBus,
        initial_value: float = 0.0,
        portfolio_analyzer: bool = False,
    ):
        super().__init__(bus)
        self.initial_value = initial_value

        self.asset_book: dict[Asset, PortfolioConstituent] = dict()
        self.metrics: PortfolioMetrics = None
        if portfolio_analyzer:
            self.portfolio_analyzer = PortfolioAnalyzer(bus)
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
    def on_bar(self, bar: Bar):
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

        self.update_portfolio_metrics(self.asset_book[bar.asset])
        self.update_portfolio_metrics()

    @EventHandler.register(EventType.ORDER_FILLED)
    def on_order_filled(self, order):
        # update metrics
        self.metrics.mtm -= order.fee
        self.metrics.timestamp = max(order.timestamp, self.metrics.timestamp)

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
        self.update_portfolio_metrics(self.asset_book[order.asset])
        self.update_portfolio_metrics()

    def update_portfolio_metrics(self):
        LOG.debug(f"Portfolio updated: {self.metrics}")
        self.bus.push(
            Event(
                EventType.PORTFOLIO_METRICS_UPDATE,
                payload=self.metrics,
            )
        )

    def update_portfolio_constituent(self, constituent: PortfolioConstituent):
        LOG.debug(f"Portfolio constituent updated: {constituent.asset.name}")
        self.bus.push(
            Event(
                EventType.PORTFOLIO_CONSTITUENT_UPDATE,
                payload=constituent,
            )
        )
