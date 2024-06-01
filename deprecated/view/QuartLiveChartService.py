# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-05-25 10:49:11
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-06-06 22:48:00


# TODO: #1 still not able to stop this by Ctrl+C

import asyncio
import json
import uuid

from collections import deque, defaultdict
from quart import Quart, websocket
from hypercorn.asyncio import serve
from hypercorn.config import Config
from log.TaskAdapter import TaskAdapter

from model import Bar
from log import LOG

from .ChartService import ChartService


class QuartLiveChartService(ChartService):
    def __init__(self, port: int = 5000, heartbeat_interval: int = 10) -> None:
        self.port = port
        self.heartbeat_interval = heartbeat_interval

        self.app = Quart(__name__)
        self.running_event = asyncio.Event()
        self.connections = {}
        self.data_to_send = list()
        self.message_queues = defaultdict()  # Create a new queue for each client
        self.global_queue = deque()
        # Keep references to the tasks we're going to start
        self.quart_server = None
        self.heartbeat_task = None

        @self.app.websocket("/ws")
        async def websocket_route():
            await self.ws(websocket)

    async def ws(self, websocket):
        # Generate a unique session ID

        session_id = str(uuid.uuid4())
        connection = websocket._get_current_object()
        self.add_connection(session_id, connection)
        try:
            while self.running_event.is_set():
                while self.global_queue:
                    self.message_queues[session_id].append(self.global_queue.popleft())
                recieved = await websocket.receive()
                received_json = json.loads(recieved)
                # If there are any queued messages for this client, send them now
                while self.message_queues[session_id]:
                    msg = self.message_queues[session_id].popleft()
                    await websocket.send(msg)

                    for key, value in received_json.items():
                        LOG.info(f"Received from {session_id}: {key} - {value}")
                await websocket.send(json.dumps("ack"))  # Send acknowledgement
        except json.JSONDecodeError as e:
            LOG.error(f"JSON decoding error: {e}")
        except Exception as e:
            LOG.error(f"Unknown error: {e}")
        finally:
            self.remove_connection(session_id)

    def add_connection(self, session_id, connection):
        self.connections[session_id] = connection
        self.message_queues[session_id] = deque([])

    def remove_connection(self, session_id):
        self.connections.pop(session_id, None)

    async def heartbeat(self):
        while self.running_event.is_set():
            if self.connections:  # Check if there are any connections
                for connection in self.connections.values():
                    await connection.send(json.dumps({"type": "heartbeat"}))
                    LOG.debug(f"Sent heartbeat to {connection}")
            await asyncio.sleep(self.heartbeat_interval)

    async def start(self):
        LOG.info("Starting QuartWebSocketService")
        self.running_event.set()

        # Configure Hypercorn
        config = Config()
        config.bind = [f"localhost:{self.port}"]
        config.use_reloader = False

        # Start the Quart app with Hypercorn
        server_coroutine = serve(self.app, config)
        self.quart_server = asyncio.ensure_future(server_coroutine)

        self.heartbeat_task = asyncio.create_task(self.heartbeat())
        self.quart_server = await self.app.run_task("localhost", self.port)
        await asyncio.gather(self.heartbeat_task)

    async def stop(self):
        for session_id, connection in list(self.connections.items()):
            try:
                await connection.close()
            except Exception as e:
                LOG.error(f"Error while closing connection: {e}")
            finally:
                self.connections.pop(session_id, None)

        if self.quart_server:
            self.quart_server.cancel()
            self.quart_server = None

        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            self.heartbeat_task = None

        self.running_event.clear()
        await self.app.shutdown()  # Quart's clean shutdown

    async def on_bar(
        self,
        bar: Bar,
    ):
        bar_data = json.dumps(
            {
                "type": "bar",
                "time": bar.timestamp.timestamp(),  # milliseconds
                "open": bar.open,
                "high": bar.high,
                "low": bar.low,
                "close": bar.close,
                "volume": bar.volume,
            }
        )
        if not self.connections:
            self.global_queue.append(bar_data)

        for session_id, connection in self.connections.items():
            try:
                await connection.send(bar_data)
            except ConnectionError as e:
                LOG.error(f"Connection error: {e}")
                self.message_queues[session_id].append(bar_data)
            except Exception as e:
                LOG.error(f"Unknown error: {e}")
                self.message_queues[session_id].append(bar_data)
        LOG.debug(f"QuartWebSocketService sent {bar}")
