# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-04-16 13:31:08
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-06-06 22:34:53

from typing import Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


# run along with the main thread
class EventHandlerType(Enum):
    STRATEGY = "STRATEGY"
    EXECUTION = "EXECUTION"


# run asynchronizely in a separate thread
class EngineServiceType(Enum):
    VIEW = "VIEW"
    FEED = "FEED"


# Basic Data Types
class EventType(Enum):
    BAR = "BAR"

    # Order
    ORDER_SUBMIT = "ORDER_SUBMIT"
    ORDER_FILLED = "ORDER_FILLED"

    ## Portfolio
    PORTFOLIO_METRICS_UPDATE = "PORTFOLIO_METRICS_UPDATE"
    PORTFOLIO_CONSTITUENT_UPDATE = "PORTFOLIO_CONSTITUENT_UPDATE"


@dataclass
class Event:
    type: EventType
    payload: Any
    timestamp: datetime = None


class AssetType(Enum):
    CASH = "CASH"
    FX = "FX"


class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"


@dataclass(frozen=True)
class Asset:
    type: AssetType
    name: str


@dataclass(frozen=True)
class Forex(Asset):
    type = AssetType
    name: str


@dataclass
class Order:
    asset: Asset
    type: OrderType
    price: float
    amount: float
    fee: float = 0.0  # in percentage e.g. 0.01 = 1%
    filled: bool = False


@dataclass(frozen=True)
class Trade:
    order_id: int
    amount: float
    price: float


@dataclass(frozen=True)
class Bar:
    asset: Asset
    open: float
    high: float
    low: float
    close: float
    volume: float
    timestamp: datetime


@dataclass(frozen=True)
class PortfolioMetrics:
    mtm: float
    # can add potential risk metrics here


@dataclass(frozen=True)
class PortfolioConstituent:
    asset: Asset
    price: float
    amount: float
    mtm: float
