# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-05-16 17:53:28
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-05-25 22:08:34


from abc import abstractmethod

from engine import EventHandler, EngineService
from model import Bar, Order


class View(EventHandler):
    @abstractmethod
    def on_bar(self, bar: Bar):
        ...

    @abstractmethod
    def on_order_create(self, order: Order):
        ...


class ChartService(EngineService):
    @abstractmethod
    async def on_bar(self, bar: Bar):
        ...

    @abstractmethod
    async def start(self):
        ...

    @abstractmethod
    def stop(self):
        ...
