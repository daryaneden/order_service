from abc import ABC, abstractmethod
from typing import Any


class EventPublisher(ABC):
    @abstractmethod
    async def publish(
        self, topic: str, message: dict[str, Any], key: str | None = None
    ) -> None:
        pass
