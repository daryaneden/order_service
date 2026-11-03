from typing import Any
from uuid import UUID

from app.application.ports.uow_factory import UnitOfWorkFactory
from app.application.exceptions import InvalidEventTypeException, OrderNotFoundException, InvalidEventPayloadException
from app.application.dtos.outbox_message import EventType

class ProcessShippingEventUseCase:

    def __init__(self, uow_factory: UnitOfWorkFactory):
        self.uow_factory = uow_factory

    async def __call__(self, payload: dict[str, Any], topic: str, partition: int, offset: int) -> None:

        event_type = payload["event_type"]

        if event_type not in (EventType.ORDER_SHIPPED, EventType.ORDER_CANCELLED):
            raise InvalidEventTypeException(event_type)

        async with self.uow_factory() as uow:
            event = await uow.inbox_repository.is_processed(topic, partition, offset)

            if event:
                return 

            try:
                order_id = UUID(payload["order_id"])
            except (ValueError, TypeError, AttributeError) as error:
                raise InvalidEventPayloadException() from error
            order = await uow.order_repository.get_order_by_id(order_id)

            if order is None:
                raise OrderNotFoundException(order_id)

            if event_type == EventType.ORDER_SHIPPED:
                order.ship()
            elif event_type == EventType.ORDER_CANCELLED:
                order.cancel()

            await uow.inbox_repository.add(topic, partition, offset)



            

            