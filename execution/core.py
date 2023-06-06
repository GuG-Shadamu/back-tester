# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-05-16 17:50:24
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-06-05 21:31:20

from abc import abstractmethod

from engine import EventHandler
from model import Order


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
