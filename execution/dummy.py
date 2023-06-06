# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-05-23 13:52:18
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-06-05 21:33:31


from engine import EventHandler
from event_bus import EventBus
from model import EventType, Order
from log import TaskAdapter, setup_logger

from .core import Execution

LOG = TaskAdapter(setup_logger(), {})


class DummyExecution(Execution):
    def __init__(self, bus: EventBus) -> None:
        super().__init__(bus)

    def submit_order(self, order: Order) -> int:
        return super().submit_order(order)

    def cancel_order(self, order_id: int):
        return super().cancel_order(order_id)

    def modify_order(self, order_id: int, order: Order):
        return super().modify_order(order_id, order)

    @EventHandler.register(EventType.ORDER_CREATE)
    def on_order_create(self, order: Order):
        LOG.debug(f"DummyExecution recieved {order =  }")
        return super().on_order_create(order)
