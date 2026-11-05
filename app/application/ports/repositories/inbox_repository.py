from abc import ABC, abstractmethod


class InboxRepository(ABC):

    @abstractmethod
    async def is_processed(self, topic: str, partition: int, offset: int) -> bool:
        pass

    @abstractmethod
    async def add(self, topic: str, partition: int, offset: int) -> None:
        pass
