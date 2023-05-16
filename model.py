# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-04-16 13:31:08
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-05-16 02:26:29

from typing import Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


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


@dataclass(frozen=True)
class Order:
    asset: Asset
    type: OrderType
    price: float
    amount: float


@dataclass(frozen=True)
class Trade:
    order_id: int
    amount: float
    price: float
