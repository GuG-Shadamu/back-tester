from abc import ABC, abstractmethod


class EngineService(ABC):
    @abstractmethod
    async def start(self):
        ...

    @abstractmethod
    def stop(self):
        ...
