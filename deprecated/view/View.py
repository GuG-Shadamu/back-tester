from engine.EventHandler import EventHandler
from model import Bar, Order


from abc import abstractmethod


class View(EventHandler):
    @abstractmethod
    def on_bar(self, bar: Bar):
        ...

    @abstractmethod
    def on_order_create(self, order: Order):
        ...
