# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-05-22 21:52:44
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-05-23 15:38:30

from __future__ import annotations
from pathlib import Path

import asyncio

from view import register_ws_route, ws, LiveChart, LiveChartView
from data_feed import OHLCBarFeed
from data import OHLCData

from engine import BackTestEngine as Engine
from event_bus import EventBus
from execution import DummyExecution

from model import Asset, AssetType
from strategy import DummyStrategy


async def main():
    bus = EventBus()

    base_dir = Path(__file__).resolve().parent
    file_path = base_dir / "data_example" / "DAT_ASCII_USDCAD_M1_202304.csv"
    data_ohlc = OHLCData.from_csv_file(
        Asset(AssetType.FX, "USDCAD"),
        file_path,
    )
    feed = OHLCBarFeed(bus, OHLCData=data_ohlc, push_freq=1)
    live_chart = LiveChart()
    register_ws_route(live_chart.app, "/ws", ws, live_chart)

    view = LiveChartView(bus, live_chart)

    execution = DummyExecution(bus)
    strategy = DummyStrategy(bus)
    engine = Engine(bus, [feed, live_chart], [strategy, execution, view])
    await engine.start()


if __name__ == "__main__":
    try:
        asyncio.run(main(), debug=True)
    except KeyboardInterrupt:
        print("Program interrupted. Exiting...")