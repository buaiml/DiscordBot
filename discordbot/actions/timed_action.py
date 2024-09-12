import asyncio
from abc import ABC, abstractmethod

from main import DiscordClient


class TimedAction(ABC):
    def __init__(self, main: DiscordClient, interval: int):
        self.main = main
        self.interval = interval

    @abstractmethod
    async def action(self):
        """
        The action to be performed every `interval` seconds
        """
        pass

    async def start(self):
        """
        Start the timed action
        """
        print(f"Running {self.__class__.__name__}")
        while True:
            print(f"Updating {self.__class__.__name__}")
            await self.action()
            print(f"Done updating {self.__class__.__name__}! Sleeping for {self.interval} seconds")
            await asyncio.sleep(self.interval)

