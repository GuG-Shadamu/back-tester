# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-05-23 13:52:18
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-05-23 13:54:08


from event_bus import EventBus
from model import EventType, Order
from log import TaskAdapter, setup_logger
from utility import check_running

from .core import Execution

LOG = TaskAdapter(setup_logger(), {})


class DummyExecution(Execution):
    def __init__(self, bus: EventBus) -> None:
        self.bus = bus
        self.running = False
        self.handler_dict: dict[EventType, callable] = dict()
        self.register(EventType.ORDER_CREATE, self.on_order_create)

    def start(self):
        self.running = True

    def stop(self):
        self.running = False
        ...

    @check_running
    def submit_order(self, order: Order) -> int:
        return super().submit_order(order)

    @check_running
    def cancel_order(self, order_id: int):
        return super().cancel_order(order_id)

    @check_running
    def modify_order(self, order_id: int, order: Order):
        return super().modify_order(order_id, order)

    @check_running
    def on_order_create(self, order: Order):
        LOG.debug(f"DummyExecution recieved {order =  }")
        return super().on_order_create(order)
