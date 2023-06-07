# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-06-06 22:47:18
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-06-06 22:47:21

from engine.EventHandler import EventHandler
from model import Order


from abc import abstractmethod


class Execution(EventHandler):
    @abstractmethod
    def submit_order(self, order: Order) -> int:
        ...

    @abstractmethod
    def cancel_order(self, order_id: int):
        ...

    @abstractmethod
    def modify_order(self, order_id: int, order: Order):
        ...

    @abstractmethod
    def on_order_create(self, order: Order):
        ...
