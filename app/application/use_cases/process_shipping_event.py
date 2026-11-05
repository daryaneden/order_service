import logging
from typing import Any
from uuid import UUID

from app.application.dtos.notification_message import NotificationMessage
from app.application.dtos.outbox_message import EventType
from app.application.exceptions import (
    InvalidEventPayloadException,
    InvalidEventTypeException,
    OrderNotFoundException,
)
from app.application.ports.notification_port import NotificationPort
from app.application.ports.uow.uow_factory import UnitOfWorkFactory

logger = logging.getLogger(__name__)


class ProcessShippingEventUseCase:
    def __init__(
        self, uow_factory: UnitOfWorkFactory, notification_port: NotificationPort
    ):
        self.uow_factory = uow_factory
        self.notification_port = notification_port

    async def __call__(
        self, payload: dict[str, Any], topic: str, partition: int, offset: int
    ) -> None:

        event_type = payload.get("event_type")

        if event_type not in (EventType.ORDER_SHIPPED, EventType.ORDER_CANCELLED):
            raise InvalidEventTypeException(event_type)

        try:
            order_id = UUID(payload["order_id"])
        except (ValueError, TypeError, AttributeError, KeyError) as error:
            raise InvalidEventPayloadException() from error

        async with self.uow_factory() as uow:
            is_processed = await uow.inbox_repository.is_processed(
                topic, partition, offset
            )

            if is_processed:
                return

            order = await uow.order_repository.get_order_by_id(order_id)

            if order is None:
                logger.error(
                    "Order not found in Order Service DB: order_id=%s", order_id
                )
                raise OrderNotFoundException(order_id)

            if event_type == EventType.ORDER_SHIPPED:
                order.ship()

            elif event_type == EventType.ORDER_CANCELLED:
                order.cancel()

            await uow.order_repository.update_order(order)

            await uow.inbox_repository.add(topic, partition, offset)

        if event_type == EventType.ORDER_SHIPPED:
            notification = NotificationMessage(
                message="SHIPPED",
                reference_id=order.id,
                idempotency_key=f"order:{order.id}:SHIPPED",
            )

            await self.notification_port.send_notification(notification)

        elif event_type == EventType.ORDER_CANCELLED:
            notification = NotificationMessage(
                message="CANCELLED",
                reference_id=order.id,
                idempotency_key=f"order:{order.id}:CANCELLED",
            )

            await self.notification_port.send_notification(notification)
