# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-04-16 13:31:08
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-06-06 22:22:48


from __future__ import annotations
from abc import ABC, abstractmethod

import inspect

from typing import TYPE_CHECKING
from model import Event, EventType
from log import TaskAdapter, setup_logger

LOG = TaskAdapter(setup_logger(), {})

if TYPE_CHECKING:
    from event_bus import EventBus


class Engine(ABC):
    @abstractmethod
    async def start(self):
        ...

    @abstractmethod
    def stop(self):
        ...


class EngineService(ABC):
    @abstractmethod
    async def start(self):
        ...

    @abstractmethod
    def stop(self):
        ...


class MetaEventHandler(type):
    def __new__(mcs, name, bases, attrs):
        new_class = super().__new__(mcs, name, bases, attrs)
        new_class.to_register = []

        for _, attr_value in attrs.items():
            if callable(attr_value) and hasattr(attr_value, "to_register"):
                key = attr_value.to_register
                new_class.to_register.append((key, attr_value))

        return new_class


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

        if event.timestamp is None:
            event.timestamp = self.bus.get_timestamp()

        if event.type in self.handler_dict:
            _callable = self.handler_dict[event.type]

            if inspect.iscoroutinefunction(_callable):
                await _callable(self, event.payload)
            else:
                _callable(self, event.payload)
