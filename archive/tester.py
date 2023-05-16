import polars as pl
from typing import BinaryIO
from functools import singledispatch
import io
import os
import pickle

from pathlib import Path


class Serializable:
    def __init__(self) -> None:
        self.data = None

    @classmethod
    def __init__(self, arg) -> None:
        raise NotImplementedError(
            f"Cannot format value of type {type(arg)}, only support Pickle obj or file"
        )

    @__init__.register(bytes)
    def _(self, obj):
        # convert from pickle object
        self.data = pickle.loads(obj)


a = Serializable()
