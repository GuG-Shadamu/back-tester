# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-04-16 13:31:08
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-05-23 14:12:02


from __future__ import annotations
from abc import ABC, abstractmethod

import inspect

from typing import Callable
from model import Event, EventType


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


class EventHandler(ABC):
    @abstractmethod
    def start(self):
        ...

    @abstractmethod
    def stop(self):
        ...

    def register(self, event_type: EventType, callable: Callable):
        self.handler_dict[event_type] = callable

    async def on_event(self, event: Event):
        event_type = event.type

        if event_type in self.handler_dict:
            _callable = self.handler_dict[event_type]

            if inspect.iscoroutinefunction(_callable):
                await _callable(event.payload)
            else:
                _callable(event.payload)
