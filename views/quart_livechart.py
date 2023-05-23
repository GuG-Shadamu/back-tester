# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-05-22 15:03:17
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-05-22 22:23:36

from __future__ import annotations

import asyncio
import json

from collections import defaultdict
from typing import Any

from quart import Quart

from engine_components import EngineService
from model import Bar, Order
from log_utility import TaskAdapter, setup_logger
from views.core import View

LOG = TaskAdapter(setup_logger(), {})


class LiveChart(EngineService):
    name = "QuartLiveChart"

    def __init__(self, port: int = 5000) -> None:
        self.app = Quart(__name__)

        self.running_event = asyncio.Event()
        self.port = port
        self.connections = defaultdict(list)
        # self.buffer_table: defaultdict[View, List[str]] = defaultdict(list)
        self.iddle_buffler = list()

    def add_connection(self, connection: Any):
        self.connections[connection] = {
            "buffer": [],
            "last_ack": None,
        }  # Add buffer and last_ack for each connection

    def remove_connection(self, connection: Any):
        self.connections.pop(connection)

    async def start(self):
        LOG.info(f"Quart LiveChart process starting...")
        self.running_event.set()  # Set the event, meaning that the task is running.
        await self.app.run_task(port=self.port, debug=True)

    async def stop(self):
        # TODO: stop websocket server
        # Currently, Ctrl+C does not work
        LOG.info(f"Quart LiveChart process stopping...")
        self.running_event.clear()
        await self.app.shutdown()

    def on_bar(self, bar: Bar):  # when new bar pushed in
        bar_send = {
            "time": bar.timestamp.timestamp(),  # milliseconds
            "open": bar.open,
            "high": bar.high,
            "low": bar.low,
            "close": bar.close,
            "volume": bar.volume,
        }

        if not self.connections:
            self.iddle_buffler.append(bar_send)

        for connection in self.connections:
            if self.iddle_buffler:
                self.connections[connection]["buffer"].extend(self.iddle_buffler)
                self.iddle_buffler.clear()
            else:
                self.connections[connection]["buffer"].append(bar_send)

        LOG.debug(f"LiveChart updated {bar}")

    async def on_ack(self, connection, ack: str):
        self.connections[connection]["last_ack"] = ack

        buffer = self.connections[connection]["buffer"]
        if not buffer:
            return  # Nothing to send
        await connection.send(json.dumps(buffer))
        # Clear the buffer
        self.connections[connection]["buffer"].clear()

    async def on_order_create(self, order: Order):
        ...

    def add_view(self, view: View):
        self.views.append(view)

    def remove_view(self, view: View):
        self.views.remove(view)
