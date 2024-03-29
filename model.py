# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-04-16 13:31:08
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-09-13 12:37:33

from typing import Any, Type
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import json


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
    END = "END"

    # Order
    ORDER_CREATE = "ORDER_CREATE"
    ORDER_SUBMIT = "ORDER_SUBMIT"
    ORDER_FILLED = "ORDER_FILLED"

    ## Portfolio
    PORTFOLIO_METRICS_UPDATE = "PORTFOLIO_METRICS_UPDATE"
    PORTFOLIO_CONSTITUENT_UPDATE = "PORTFOLIO_CONSTITUENT_UPDATE"


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
    type = AssetType.FX
    name: str


@dataclass
class PortfolioMetrics:
    mtm: float
    # can add potential risk metrics here


@dataclass
class PortfolioConstituent:
    asset: Asset
    price: float
    amount: float
    mtm: float


@dataclass
class EventData:
    def to_json(self) -> str:
        return json.dumps(asdict(self), default=str)

    @classmethod
    def from_json(cls: Type["EventData"], json_str: str) -> "EventData":
        data = json.loads(json_str)
        return cls(**data)


@dataclass
class Event:
    type: EventType
    data: EventData
    timestamp: datetime = None

    def to_json(self) -> str:
        return json.dumps(asdict(self), default=str)

    @classmethod
    def from_json(cls: Type["Event"], json_str: str) -> "Event":
        data = json.loads(json_str)
        return cls(
            type=EventType(data["type"]),
            data=EventData.from_json(data["data"]),
            timestamp=datetime(data["timestamp"]),
        )


@dataclass
class Order(EventData):
    asset: Asset
    type: OrderType
    amount: float
    price: float = None
    fee: float = 0.0  # in percentage e.g. 0.01 = 1%
    filled: bool = False


@dataclass(frozen=True)
class Trade(EventData):
    order_id: int
    amount: float
    price: float


@dataclass(frozen=True)
class Bar(EventData):
    asset: Asset
    open: float
    high: float
    low: float
    close: float
    volume: float
    timestamp: datetime
