# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-05-16 17:50:24
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-05-16 17:51:16

from abc import ABC, abstractmethod
from event_bus import EventBus

from model import Order
from log_utility import TaskAdapter, setup_logger
LOG = TaskAdapter(setup_logger(), {})

class Execution(ABC):
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
        LOG.info(f"Execution recieved {order =  }")
        ...

    @abstractmethod
    def start(self):
        ...


class DummyExecution(Execution):
    def __init__(self, bus: EventBus) -> None:
        self.bus = bus

    def submit_order(self, order: Order) -> int:
        return super().submit_order(order)

    def cancel_order(self, order_id: int):
        return super().cancel_order(order_id)

    def modify_order(self, order_id: int, order: Order):
        return super().modify_order(order_id, order)

    def on_order_create(self, order: Order):
        return super().on_order_create(order)

    def start(self):
        return super().start()
