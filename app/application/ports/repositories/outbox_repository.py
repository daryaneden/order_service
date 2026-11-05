from abc import ABC, abstractmethod
from uuid import UUID

from app.application.dtos.outbox_message import OutboxMessageDto, PendingOutboxMessage


class OutboxRepository(ABC):

    async def save(self, message: OutboxMessageDto) -> None:
        pass

    @abstractmethod
    async def get_pending(self) -> list[PendingOutboxMessage]:
        pass

    @abstractmethod
    async def mark_as_published(self, event_id: UUID) -> None:
        pass
