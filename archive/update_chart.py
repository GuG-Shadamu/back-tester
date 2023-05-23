# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-05-15 02:17:50
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-05-23 14:00:39

from datetime import timedelta
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

import time

from data import OHLCData
from model import AssetType, Asset


app = Flask(__name__)
CORS(app)  # Enable CORS
socketio = SocketIO(
    app, cors_allowed_origins="*"
)  # Enable WebSocket and allow all origins
thread = None


@app.route("/")
def index():
    return "Hello, World!\n"


@socketio.on_error_default  # handles all namespaces without an explicit error handler
def default_error_handler(e):
    print("An error has occurred: " + str(e))


def background_thread():
    """Send a message every 1-6 seconds."""
    a = OHLCData.from_csv_file(
        Asset(AssetType.FX, "USDCAD"), "data_example/DAT_ASCII_USDCAD_M1_202304.csv"
    )

    b = a.get_resample(timedelta(minutes=30))
    while True:
        for bar in b.get_bars():
            bar_send = {
                "time": bar.timestamp.isoformat(),
                "open": bar.open,
                "high": bar.high,
                "low": bar.low,
                "close": bar.close,
                "volume": bar.volume,
            }
            socketio.emit("data", bar_send)  # Send the new bar to the client
            time.sleep(0.1)  # Wait for 5 seconds
            print("sent")


@socketio.on("connect")
def handle_connect():
    print("Client connected")
    global thread
    if thread is None:
        thread = socketio.start_background_task(background_thread)


if __name__ == "__main__":
    socketio.run(app, port=4000, debug=True)
