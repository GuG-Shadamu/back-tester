# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-05-16 17:53:28
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-05-22 22:23:17


from abc import abstractmethod


from engine_components import EventHandler
from model import Bar, Order
from log_utility import TaskAdapter, setup_logger

LOG = TaskAdapter(setup_logger(), {})


class View(EventHandler):
    @abstractmethod
    def on_bar(self, bar: Bar):
        ...

    @abstractmethod
    def on_order_create(self, order: Order):
        ...
