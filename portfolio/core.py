# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-05-27 22:16:07
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-06-05 22:49:05
from collections import defaultdict
import polars as pl

from engine import EventHandler
from event_bus import EventBus
from model import Asset, Event, EventType, PortfolioConstituent, PortfolioMetrics

from log import TaskAdapter, setup_logger

LOG = TaskAdapter(setup_logger(), {})
# maintain two views of your portfolio: a 'real-time' view and a 'lagging' view.
# The real-time view processes events as they come in, ignoring the timestamps,
# while the lagging view processes events sorted by their timestamps.


class Portfolio(EventHandler):
    def __init__(self, bus: EventBus, initial_value: float = 0.0):
        super().__init__(bus)
        self.initial_value = initial_value
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

        self.asset_book: dict[Asset, PortfolioConstituent] = dict()
        self.metrics: PortfolioMetrics = None

    def update_df_constituents(self, constituent: PortfolioConstituent):
        asset = constituent.asset
        self.df_constituents[asset] = self.df_constituents[asset].vstack(
            pl.DataFrame(
                {
                    "asset": pl.Series([asset], dtype=pl.Object),
                    "timestamp": pl.Series(
                        [constituent.last_updated], dtype=pl.Datetime
                    ),
                    "price": pl.Series([constituent.price], dtype=pl.Float64),
                    "amount": pl.Series([constituent.amount], dtype=pl.Float64),
                    "mtm": pl.Series([constituent.mtm], dtype=pl.Float64),
                }
            )
        )

    def update_df_mtm(self, metrics: PortfolioMetrics):
        self.df_mtm = self.df_mtm.vstack(
            pl.DataFrame(
                {
                    "timestamp": pl.Series([metrics.timestamp], dtype=pl.Datetime),
                    "mtm": pl.Series([metrics.mtm], dtype=pl.Float64),
                }
            )
        )

    @EventHandler.register(EventType.BAR)
    def on_bar(self, bar):
        if self.metrics is None:
            self.metrics = PortfolioMetrics(
                timestamp=bar.timestamp, mtm=self.initial_value
            )

        if bar.asset not in self.asset_book:
            return

        # update metrics
        self.metrics.mtm += (
            bar.close * self.asset_book[bar.asset].amount
            - self.asset_book[bar.asset].mtm
        )
        self.update_df_mtm(self.metrics)

        # update asset book
        self.asset_book[bar.asset].price = bar.close
        self.asset_book[bar.asset].mtm = bar.close * self.asset_book[bar.asset].amount
        self.asset_book[bar.asset].last_updated = bar.timestamp
        self.update_df_constituents(self.asset_book[bar.asset])

        self.publish_update()

    @EventHandler.register(EventType.ORDER_FILLED)
    def on_order_filled(self, order):
        # update metrics
        self.metrics.mtm -= order.fee
        self.metrics.timestamp = order.timestamp
        self.update_df_mtm(self.metrics)

        # update asset book
        if order.asset not in self.asset_book:
            self.asset_book[order.asset] = PortfolioConstituent(
                asset=order.asset,
                price=order.price,
                amount=order.amount,
                mtm=order.price * order.amount,
                last_updated=order.timestamp,
            )
        else:
            self.asset_book[order.asset].amount += order.amount
            self.asset_book[order.asset].last_updated = max(
                order.timestamp, self.asset_book[order.asset].last_updated
            )
            self.asset_book[order.asset].mtm = (
                self.asset_book[order.asset].price * self.asset_book[order.asset].amount
            )
        self.update_df_constituents(self.asset_book[order.asset])
        self.publish_update()

    def publish_update(self):
        LOG.debug(f"Portfolio updated: {self.metrics}")
        self.bus.push(Event(EventType.PORTFOLIO_UPDATE, payload=self.metrics))
