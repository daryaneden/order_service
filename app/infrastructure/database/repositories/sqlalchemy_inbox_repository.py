from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.inbox_repository import InboxRepository
from app.infrastructure.database.models.inbox_event import InboxEventModel


class SqlAlchemyInboxRepository(InboxRepository):

    def __init__(self, session: AsyncSession):
            self.session = session

    async def is_processed(self, topic: str, partition: int, offset: int) -> bool:
        stmt = select(exists().where(InboxEventModel.topic == topic,
                                     InboxEventModel.partition == partition,
                                     InboxEventModel.offset == offset))

        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def add(self, topic: str, partition: int, offset: int) -> None:
        event = InboxEventModel(topic=topic,
                                partition=partition,
                                offset=offset)

        self.session.add(event)