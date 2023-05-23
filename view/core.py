# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-05-16 17:53:28
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-05-23 13:55:30


from abc import abstractmethod

from engine import EventHandler
from model import Bar, Order


class View(EventHandler):
    @abstractmethod
    def on_bar(self, bar: Bar):
        ...

    @abstractmethod
    def on_order_create(self, order: Order):
        ...
