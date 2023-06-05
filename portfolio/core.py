# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-05-27 22:16:07
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-06-04 23:20:20
from collections import defaultdict
from typing import Dict
import polars as pl
from datetime import datetime, timedelta


from engine import EventHandler
from event_bus import EventBus
from model import Asset, EventType, Order


# maintain two views of your portfolio: a 'real-time' view and a 'lagging' view.
# The real-time view processes events as they come in, ignoring the timestamps,
# while the lagging view processes events sorted by their timestamps.


def Portfolio(EventHandler):
    def __init__(self, bus: EventBus) -> None:
        self.bus = bus
        self.running = False
        self.handler_dict: dict[EventType, callable] = dict()

        self.mtm = pl.DataFrame(
            {
                "timestamp": pl.Series([], dtype=pl.Datetime),
                "mtm": pl.Series([], dtype=pl.Float64),
            }
        )
        self.assets: Dict[Asset : pl.DataFrame] = defaultdict(
            lambda: pl.DataFrame(
                {
                    "timestamp": pl.Series([], dtype=pl.Datetime),
                    "price": pl.Series([], dtype=pl.Float64),
                    "amount": pl.Series([], dtype=pl.Float64),
                    "mtm": pl.Series([], dtype=pl.Float64),
                }
            )
        )

    def calc_current_mtm(self):
        ...

    def on_order_create(self, order: Order):
        ...

    def on_bar(self, bar):
        # Update the real-time view immediately
        self.update_real_time(bar)

        # Insert the bar into the correct position in the lagging view
        self.mtm = self.insert_sorted(
            self.mtm, {"timestamp": bar.timestamp, "mtm": self.calc_current_mtm()}
        )
        # update assets
        for asset, value in bar.assets.items():
            df = self.assets[asset]
            df = self.insert_sorted(
                df,
                {
                    "timestamp": bar.timestamp,
                    "price": value.price,
                    "amount": value.amount,
                },
            )
            self.assets[asset] = df

    def on_order_create(self, order: Order):
        # similar to on_bar
        self.update_real_time(order)

    def insert_sorted(self, df, item):
        # Append the item to the DataFrame and sort by timestamp
        df = df.append(item, ignore_index=True)
        df = df.sort_values(by="timestamp")
        df.reset_index(drop=True, inplace=True)
        return df

    def update_real_time(self, event):
        # This is where you'd update your real-time view based on the event.
        # This could involve calculating the current MTM or updating the quantity of an asset.
        self.real_time_events.append(event)
        while len(self.real_time_events) > 100:  # adjust this value as needed
            self.real_time_events.popleft()
        # TODO: Calculate real-time mtm and asset values here
