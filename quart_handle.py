# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-05-15 02:17:50
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-05-16 12:52:31

import json
from quart import Quart, websocket


def ws(live_chart):
    async def websocket_handler():
        live_chart.add_connection(websocket._get_current_object())

        try:
            while True:
                message = await websocket.receive()
                data = json.loads(message)

                if "ack" in data:
                    await live_chart.on_ack(
                        websocket._get_current_object(), data["ack"]
                    )
        finally:
            live_chart.remove_connection(websocket._get_current_object())

    return websocket_handler


def register_ws_route(app, route, handler, live_chart):
    app.websocket(route)(handler(live_chart))
