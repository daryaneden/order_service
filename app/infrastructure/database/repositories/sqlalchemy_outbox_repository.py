from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.outbox_message import OutboxMessageDto, PendingOutboxMessage
from app.application.ports.repositories.outbox_repository import OutboxRepository
from app.infrastructure.database.models.outbox_event import OutboxEventModel


class SqlAlchemyOutboxRepository(OutboxRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, message: OutboxMessageDto) -> None:
        outbox_event = OutboxEventModel(
            id=uuid4(),
            event_type=message.event_type,
            payload=message.payload,
            status="pending",
            created_at=datetime.now(UTC),
        )

        self.session.add(outbox_event)

    async def get_pending(self) -> list[PendingOutboxMessage]:
        result = await self.session.execute(
            select(OutboxEventModel)
            .where(OutboxEventModel.status == "pending").with_for_update(skip_locked=True)
            .order_by(OutboxEventModel.created_at))

        events = result.scalars().all()

        return [
            PendingOutboxMessage(
                id=event.id, event_type=event.event_type, payload=event.payload
            )
            for event in events
        ]

    async def mark_as_published(self, event_id: UUID) -> None:
        await self.session.execute(
            update(OutboxEventModel)
            .where(OutboxEventModel.id == event_id)
            .values(status="published")
        )
