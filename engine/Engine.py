from abc import ABC, abstractmethod


class Engine(ABC):
    @abstractmethod
    async def start(self):
        ...

    @abstractmethod
    def stop(self):
        ...
