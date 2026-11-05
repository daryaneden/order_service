from typing import Any
from uuid import UUID

from app.application.ports.uow_factory import UnitOfWorkFactory
from app.application.exceptions import InvalidEventTypeException, OrderNotFoundException, InvalidEventPayloadException
from app.application.dtos.outbox_message import EventType

import logging

from typing import Any
from uuid import UUID

from app.application.ports.uow_factory import UnitOfWorkFactory
from app.application.exceptions import (
    InvalidEventTypeException,
    OrderNotFoundException,
    InvalidEventPayloadException,
)
from app.application.dtos.outbox_message import EventType
from app.application.dtos.notification_message import NotificationMessage
from app.application.ports.notification_port import NotificationPort

logger = logging.getLogger(__name__)


class ProcessShippingEventUseCase:

    def __init__(self, uow_factory: UnitOfWorkFactory,
                 notification_port: NotificationPort):
        self.uow_factory = uow_factory
        self.notification_port = notification_port

    async def __call__(
        self,
        payload: dict[str, Any],
        topic: str,
        partition: int,
        offset: int,
    ) -> None:

        event_type = payload.get("event_type")

        if event_type not in (
            EventType.ORDER_SHIPPED,
            EventType.ORDER_CANCELLED,
        ):
            raise InvalidEventTypeException(event_type)

        try:
            order_id = UUID(payload["order_id"])
        except (ValueError, TypeError, AttributeError, KeyError) as error:
            raise InvalidEventPayloadException() from error

        logger.info(
            "Received shipping event: event_type=%s, order_id=%s, "
            "topic=%s, partition=%s, offset=%s",
            event_type,
            order_id,
            topic,
            partition,
            offset,
        )

        async with self.uow_factory() as uow:

            # Проверяем, не обрабатывали ли мы уже это сообщение.
            is_processed = await uow.inbox_repository.is_processed(
                topic,
                partition,
                offset,
            )

            if is_processed:
                logger.info(
                    "Shipping event already processed: "
                    "topic=%s, partition=%s, offset=%s",
                    topic,
                    partition,
                    offset,
                )
                return

            # Ищем заказ в собственной БД Order Service.
            order = await uow.order_repository.get_order_by_id(order_id)

            if order is None:
                logger.error(
                    "Order not found in Order Service DB: order_id=%s",
                    order_id,
                )
                raise OrderNotFoundException(order_id)

            # Применяем событие.
            if event_type == EventType.ORDER_SHIPPED:
                order.ship()

            elif event_type == EventType.ORDER_CANCELLED:
                order.cancel()

            # Сохраняем изменённый заказ.
            await uow.order_repository.update_order(order)

            # Регистрируем сообщение в Inbox.
            await uow.inbox_repository.add(
                topic,
                partition,
                offset,
            )

            logger.info(
                "Shipping event processed successfully: "
                "order_id=%s, event_type=%s",
                order_id,
                event_type,
            )
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