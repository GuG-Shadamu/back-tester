# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-05-22 21:52:44
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-08-15 17:04:26

from __future__ import annotations
from pathlib import Path

import asyncio


from clearing_house import SimpleClearingHouse
from view import QuartLiveChartService, UpdateChart
from data_feed.OHLCBarFeed import OHLCBarFeed
from data import OHLCData

from engine import BackTestEngine as Engine

# from engine import simulate_keyboard_interrupt
from EventBus import EventBus
from execution import DummyExecution
from portfolio import RealTimePortfolio as Portfolio
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
    feed = OHLCBarFeed(bus, OHLCData=data_ohlc, push_freq=0.1)
    live_chart = QuartLiveChartService()
    view = UpdateChart(bus)

    execution = DummyExecution(bus)
    strategy = DummyStrategy(bus)
    portfolio = Portfolio(bus, initial_cash=1000000, portfolio_analyzer=True)

    fake_clearing_house = SimpleClearingHouse(bus, transaction_fee=0.01)

    engine = Engine(
        bus=bus,
        services=[feed],
        event_handlers=[strategy, execution, view, portfolio, fake_clearing_house],
    )
    # Register the shutdown signal handler
    await engine.start()


if __name__ == "__main__":
    asyncio.run(main())
