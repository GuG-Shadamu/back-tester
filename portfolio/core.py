# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-05-27 22:16:07
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-05-28 16:03:15
from engine import EventHandler
from event_bus import EventBus
from model import EventType
import polars as pl


def Portfolio(EventHandler):
    def __init__(self, bus: EventBus) -> None:
        self.bus = bus
        self.running = False
        self.handler_dict: dict[EventType, callable] = dict()

        self.register(EventType.BAR, self.on_bar)
        self.portfolio_mtm = pl.DataFrame()

    def calc_mtm(self):
        ...

    def on_bar(self, bar):
        ...

    def on_order_create(self, order):
        ...
