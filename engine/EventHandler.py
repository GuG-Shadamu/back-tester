from engine.MetaEventHandler import MetaEventHandler
from EventBus import EventBus
from log import LOG
from model import Event, EventType


import inspect


class EventHandler(metaclass=MetaEventHandler):
    def __init__(self, bus: EventBus):
        self.running = False
        self.handler_dict: dict[EventType, callable] = dict()
        self.bus = bus
        for keys, func in self.to_register:
            for key in keys:
                self._register(key, func)
            LOG.debug(f"Register {func} to {key}")

    def _register(self, key, func):
        if not isinstance(key, EventType):
            raise ValueError(f"Key {key} is not an Event")
        self.handler_dict[key] = func

    @classmethod
    def register(cls, *keys):
        def decorator(func):
            func.to_register = list(keys)
            return func

        return decorator

    def start(self):
        self.running = True

    def stop(self):
        LOG.DEBUG(f"{self} process stopped")
        self.running = False

    async def on_event(self, event: Event):
        if not self.running:
            LOG.debug(f"EventHandler {self} is not running, skip event {event}")
            return

        if event.type in self.handler_dict:
            if event.timestamp is None:
                event.timestamp = self.bus.get_timestamp()

            _callable = self.handler_dict[event.type]

            if inspect.iscoroutinefunction(_callable):
                await _callable(self, event.data)
            else:
                _callable(self, event.data)
