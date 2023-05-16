# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-05-16 17:53:28
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-05-16 18:12:59

import asyncio
import json

from abc import ABC, abstractmethod
from collections import defaultdict
from typing import Any
from quart import Quart, websocket

from model import Bar, Order
from event_bus import EventBus
from log_utility import TaskAdapter, setup_logger

LOG = TaskAdapter(setup_logger(), {})

class View(ABC):
    @abstractmethod
    def on_bar(self, bar: Bar):
        ...

    @abstractmethod
    def on_order_create(self, order: Order):
        ...


class LiveChart(View):
    def __init__(self, bus: EventBus, port: int = 5000) -> None:
        self.bus = bus
        self.running_event = asyncio.Event()
        self.port = port
        self.connections = defaultdict(list)
        self.iddle_buffer = list()
        self.app = Quart(__name__)

    def add_connection(self, connection: Any):
        self.connections[connection] = {
            "buffer": [],
            "last_ack": None,
        }  # Add buffer and last_ack for each connection

    def remove_connection(self, connection: Any):
        self.connections.pop(connection)

    async def start(self):
        LOG.info(f"{self} process starting...")
        await self.app.run_task(port=self.port, debug=True)

    async def stop(self):
        # TODO: stop websocket server
        # Currently, Ctrl+C does not work
        LOG.info(f"{self} process stopping...")
        self.running_event.clear()
        await self.app.shutdown()

    async def on_bar(self, bar: Bar):
        bar_send = {
            "time": bar.timestamp.timestamp(),  # milliseconds
            "open": bar.open,
            "high": bar.high,
            "low": bar.low,
            "close": bar.close,
            "volume": bar.volume,
        }
        if not self.connections:
            self.iddle_buffer.append(bar_send)

        for connection in self.connections:
            if self.iddle_buffer:
                self.connections[connection]["buffer"].extend(self.iddle_buffer)
                self.iddle_buffer.clear()
            else:
                self.connections[connection]["buffer"].append(bar_send)

        LOG.info(f"LiveChart buffered {bar}")

    async def on_ack(self, connection, ack: str):
        self.connections[connection]["last_ack"] = ack

        buffer = self.connections[connection]["buffer"]
        if not buffer:
            return  # Nothing to send
        await connection.send(json.dumps(buffer))
        LOG.info(f"LiveChart sent buffer")
        # Clear the buffer
        self.connections[connection]["buffer"].clear()

    async def on_order_create(self, order: Order):
        LOG.info(f"LiveChart reveived {order}")
        LOG.info(f"Plotting order ...")
