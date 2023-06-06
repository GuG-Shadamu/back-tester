# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-05-22 21:52:44
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-06-05 21:10:18

from __future__ import annotations
from pathlib import Path

import asyncio
import signal


from view import QuartLiveChartService, UpdateChart
from data_feed import OHLCBarFeed
from data import OHLCData

from engine import BackTestEngine as Engine

# from engine import simulate_keyboard_interrupt
from event_bus import EventBus
from execution import DummyExecution
from portfolio import Portfolio

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
    live_chart = QuartLiveChartService()
    view = UpdateChart(bus)

    execution = DummyExecution(bus)
    strategy = DummyStrategy(bus)
    portfolio = Portfolio(bus)

    engine = Engine(bus, [feed], [strategy, execution, view, portfolio])
    # Register the shutdown signal handler
    await engine.start()


if __name__ == "__main__":
    asyncio.run(main())
