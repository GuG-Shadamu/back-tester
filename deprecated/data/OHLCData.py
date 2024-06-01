# -*- coding: utf-8 -*-
# @Author: Tairan Gao
# @Date:   2023-05-23 13:30:28
# @Last Modified by:   Tairan Gao
# @Last Modified time: 2023-06-06 23:47:43

import polars as pl

from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional
from model import Asset, Bar
from .Serializable import Serializable


@dataclass(frozen=True)
class OHLCData(Serializable):
    """for storing OHLC data entry"""

    asset: Asset
    data: pl.DataFrame
    time_delta: timedelta  # example M1, M5, M15, M30, H1, H4, D1

    # example file format:
    # 20230402 180000;1.349300;1.350670;1.349060;1.350460;0

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
    def from_csv_file(cls, asset: Asset, file_path: str) -> "OHLCData":
        """load data from csv file"""

        dtypes = {
            "time": pl.Utf8,
            "open": pl.Float64,
            "high": pl.Float64,
            "low": pl.Float64,
            "close": pl.Float64,
            "volume": pl.UInt64,
        }

        df = pl.read_csv(file_path, separator=";", has_header=False, dtypes=dtypes)
        df = df.with_columns(pl.col("time").str.to_datetime("%Y%m%d %H%M%S"))
        time_delta = df[1, "time"] - df[0, "time"]
        start_time = df[0, "time"]
        end_time = df[-1, "time"]
        return cls(asset, df, time_delta, start_time, end_time)

    def get_resample(self, new_delta: timedelta) -> "OHLCData":
        """non-inplace method to get a resampled dataframe"""

        if new_delta <= self.time_delta:
            raise ValueError(
                f"New delta {new_delta} must be greater than current delta {self.time_delta}"
            )

        data = self.data
        # Convert timedelta to seconds for calculations
        delta_seconds = new_delta.total_seconds()

        # Convert 'time' to Unix timestamp in seconds
        data = data.with_columns(
            pl.col("time").apply(lambda x: x.timestamp(), return_dtype=pl.Float64)
        )

        # Calculate the time group, which is integer division of Unix timestamp by delta
        data = data.with_columns(
            (pl.col("time") / delta_seconds).floor().alias("time_group")
        )

        # Group by 'time_group', then calculate OHLC and volume
        resampled = (
            data.lazy()
            .groupby(["time_group"])
            .agg(
                [
                    pl.col("time").first().alias("time"),
                    pl.col("open").first().alias("open"),
                    pl.col("high").max().alias("high"),
                    pl.col("low").min().alias("low"),
                    pl.col("close").last().alias("close"),
                    pl.col("volume").sum().alias("volume"),
                ]
            )
            .collect()
        )

        # Convert 'time_group' back to datetime
        resampled = resampled.with_columns(
            (pl.col("time")).apply(lambda x: datetime.fromtimestamp(x)).alias("time")
        )

        # Drop the 'time_group' column
        resampled = resampled.drop("time_group")
        resampled = resampled.sort("time")

        return OHLCData(
            self.asset, resampled, new_delta, self.start_time, self.end_time
        )

    def get_bars(self):
        """generator for iterating through OHLC data"""
        for row in self.data.rows():
            yield Bar(
                self.asset,
                row[1],  # open
                row[2],  # high
                row[3],  # low
                row[4],  # close
                row[5],  # volume
                row[0],  # time
            )
