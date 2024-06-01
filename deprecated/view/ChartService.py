from engine.EngineService import EngineService
from model import Bar


from abc import abstractmethod


class ChartService(EngineService):
    @abstractmethod
    async def on_bar(self, bar: Bar):
        ...
