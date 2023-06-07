from engine.EventHandler import EventHandler
from EventBus import EventBus
from execution.Execution import Execution
from log import LOG
from model import EventType, Order


class DummyExecution(Execution):
    def __init__(self, bus: EventBus) -> None:
        super().__init__(bus)

    def submit_order(self, order: Order) -> int:
        return super().submit_order(order)

    def cancel_order(self, order_id: int):
        return super().cancel_order(order_id)

    def modify_order(self, order_id: int, order: Order):
        return super().modify_order(order_id, order)

    @EventHandler.register(EventType.ORDER_SUBMIT)
    def on_order_create(self, order: Order):
        LOG.debug(f"DummyExecution recieved {order =  }")
        return super().on_order_create(order)
