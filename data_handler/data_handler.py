
import pickle
from datetime import datetime, timedelta
from attr import dataclass

import polars as pl


def get_aggregate(data: pl.DataFrame, delta: timedelta) -> pl.DataFrame:
    '''non-inplace method to get an aggregated datafram'''
    pass


def as_aggregate(data: pl.DataFrame, delta: timedelta) -> bool:
    '''inplace method to get an aggregated datafram '''
    pass


class Serializable:

    def __init__(self, data=None) -> None:
        self.data = data

    @classmethod
    def from_pickle_obj(cls, obj: type):
        '''convert from pickle object'''
        data = pickle.loads(obj)
        return cls(data)

    @classmethod
    def from_pickle_file(cls, filename: str):
        '''convert from pickle file'''
        with open(filename, "rb") as file:
            data = pickle.load(file)
        return cls(data)

    def to_pickle_obj(self) -> bytes:
        '''Serialize dataframe into pickle object'''
        return pickle.dumps(self.data)


@dataclass(init=False)
class TickerData(Serializable):
    ticker_data: pl.DataFrame
    start_time: datetime
    end_time: datetime

    def __init__(self, data=None):
        super().__init__(data)

    @classmethod
    def from_csv_file(cls, obj: type):
        '''convert from csv file'''
        data = pickle.loads(obj)
        return cls(data)


@dataclass(init=False)
class OHLCDataEntry(TickerData):
    OHLCData: pl.DataFrame
    time_delta: timedelta

    def __init__(self, time_delta):
        self.time_delta = time_delta

    def aggregate(self):
        pass
