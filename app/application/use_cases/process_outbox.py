import logging

from app.application.ports.messaging.event_publisher import EventPublisher
from app.application.ports.uow.uow_factory import UnitOfWorkFactory

logger = logging.getLogger(__name__)


class ProcessOutboxUseCase:
    def __init__(self, uow_factory: UnitOfWorkFactory, event_publisher: EventPublisher):

        self.uow_factory = uow_factory
        self.event_publisher = event_publisher

    async def __call__(self, topic: str) -> None:

        async with self.uow_factory() as uow:
            messages = await uow.outbox_repository.get_pending()

            logger.info("Found %s pending outbox messages", len(messages))

        for message in messages:
            message_to_publish = message.payload
            order_id = message.payload["order_id"]

            await self.event_publisher.publish(
                topic=topic, message=message_to_publish, key=order_id
            )

            async with self.uow_factory() as uow:
                await uow.outbox_repository.mark_as_published(message.id)
