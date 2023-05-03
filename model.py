from typing import Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from decimal import Decimal


# Basic Data Types
class EventType(Enum):
    BAR = "BAR"
    ORDER_CREATE = "ORDER_CREATE"
    TRADE = "TRADE"


@dataclass(frozen=True)
class Event:
    type: EventType
    payload: Any


@dataclass(frozen=True)
class Bar:
    open: float
    high: float
    low: float
    close: float
    volume: float
    timestamp: datetime


class AssetType(Enum):
    CASH = "CASH"


class OrderType(Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"


@dataclass
class Asset:
    type: AssetType
    name: str


@dataclass(frozen=True)
class Order:
    id: int
    asset: Asset
    type: OrderType
    price: Decimal
    amount: Decimal


@dataclass(frozen=True)
class Trade:
    order_id: int
    amount: Decimal
    price: Decimal
