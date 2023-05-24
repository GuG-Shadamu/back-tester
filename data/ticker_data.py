# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-05-23 13:29:41
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-05-23 15:52:53

import polars as pl

from datetime import datetime
from dataclasses import dataclass
from typing import Optional
from model import Asset, AssetType

from .core import Serializable


@dataclass(frozen=True)
class TickerData(Serializable):
    """for storing ticker data"""

    data: pl.DataFrame
    type: AssetType

    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    def __post_init__(self):
        """Check if all fields are filled"""
        for field_name, field_type in self.__annotations__.items():
            field_value = getattr(self, field_name, None)
            if field_value is None:
                raise ValueError(f"Field '{field_name}' is required")
            elif isinstance(field_type, pl.DataFrame) and field_value.is_empty():
                raise ValueError(f"DataFrame field '{field_name}' is empty")

    @classmethod
    def from_csv_file(cls, asset: Asset, file_path: str) -> "TickerData":
        """load data from csv file"""
        # TODO implement this
        pass
