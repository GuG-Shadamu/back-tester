# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-05-15 02:17:50
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-05-15 22:51:03

from quart import Quart, websocket


def ws(live_chart):
    async def websocket_handler():
        live_chart.add_connection(websocket._get_current_object())

        try:
            while True:
                message = await websocket.receive()
                # Process incoming messages if needed
                # For example, you can handle control messages here
        finally:
            live_chart.remove_connection(websocket._get_current_object())

    return websocket_handler


def register_ws_route(app, route, handler, live_chart):
    app.websocket(route)(handler(live_chart))
