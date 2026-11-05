import logging
from uuid import uuid4

from app.application.dtos.notification_message import NotificationMessage
from app.application.dtos.order import OrderDto
from app.application.dtos.outbox_message import EventType, OutboxMessageDto
from app.application.dtos.payment_dtos import CreatePaymentDto
from app.application.exceptions import (
    InsufficientQuantityError,
    InvalidPaymentStatusException,
    ItemOutOfStockError,
    OrderNotFoundException,
    PaymentAmountMismatchException,
    PaymentCreationUnknownException,
    PaymentMismatchException,
    PaymentStatusConflictException,
)
from app.application.ports.catalog_port import CatalogPort
from app.application.ports.notification_port import NotificationPort
from app.application.ports.payment_port import PaymentPort
from app.application.ports.uow.uow import UnitOfWork
from app.application.ports.uow.uow_factory import UnitOfWorkFactory
from app.domain.entities.order import Order
from app.domain.enums.order_status import OrderStatus
from app.domain.enums.payment_status import PaymentStatus

logger = logging.getLogger(__name__)


class CreateOrderUseCase:
    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        catalog_port: CatalogPort,
        payment_port: PaymentPort,
        notification_port: NotificationPort,
        callback_url: str,
    ):

        self.uow_factory = uow_factory
        self.catalog_port = catalog_port
        self.payment_port = payment_port
        self.callback_url = callback_url
        self.notification_port = notification_port

    async def __call__(self, order_data: OrderDto) -> Order:

        async with self.uow_factory() as uow:
            existing_order = await uow.order_repository.get_by_idempotency_key(
                order_data.idempotency_key
            )

        if existing_order is not None:
            if existing_order.status in (OrderStatus.PAID, OrderStatus.CANCELLED):
                return existing_order

            if existing_order.payment_id is not None:
                return existing_order

            return await self._create_payment(existing_order)

        item = await self.catalog_port.get_item(order_data.item_id)

        if item.available_qty <= 0:
            raise ItemOutOfStockError()

        if item.available_qty < order_data.quantity:
            raise InsufficientQuantityError()

        order = Order(
            id=uuid4(),
            user_id=order_data.user_id,
            item_id=order_data.item_id,
            quantity=order_data.quantity,
            unit_price=item.price,
            status=OrderStatus.NEW,
            idempotency_key=order_data.idempotency_key,
        )

        async with self.uow_factory() as uow:
            await uow.order_repository.create_order(order)

        notification = NotificationMessage(
            message="NEW",
            reference_id=order.id,
            idempotency_key=f"order:{order.id}:NEW",
        )

        await self.notification_port.send_notification(notification)

        return await self._create_payment(order)

    async def _create_payment(self, order: Order) -> Order:

        payment_data = CreatePaymentDto(
            order_id=order.id,
            amount=order.unit_price * order.quantity,
            callback_url=self.callback_url,
            idempotency_key=order.idempotency_key,
        )

        try:
            payment = await self.payment_port.create_payment(payment_data)

            logger.info(
                "Payment creation response received: order_id=%s, "
                "payment_id=%s, payment_status=%s",
                order.id,
                payment.id,
                payment.status,
            )

        except PaymentCreationUnknownException:
            raise

        async with self.uow_factory() as uow:
            locked_order = await uow.order_repository.get_order_by_id_for_update(
                order.id
            )

            if locked_order is None:
                raise OrderNotFoundException()

            locked_order.payment_id = payment.id

            await self._apply_payment_status(
                uow=uow, order=locked_order, payment_status=payment.status
            )

            pending_callbacks = (
                await uow.pending_payment_callback_repository.get_all_by_order_id(
                    locked_order.id
                )
            )

            for callback in pending_callbacks:
                if callback.payment_id != locked_order.payment_id:
                    raise PaymentMismatchException()

                expected_amount = locked_order.unit_price * locked_order.quantity

                if callback.amount != expected_amount:
                    raise PaymentAmountMismatchException()

                await self._apply_payment_status(
                    uow=uow, order=locked_order, payment_status=callback.status
                )

                await uow.pending_payment_callback_repository.delete(callback.id)

            await uow.order_repository.update_order(locked_order)

        if locked_order.payment_status == PaymentStatus.SUCCEEDED:
            notification = NotificationMessage(
                message="PAID",
                reference_id=locked_order.id,
                idempotency_key=f"order:{locked_order.id}:PAID",
            )

            await self.notification_port.send_notification(notification)

        if locked_order.payment_status == PaymentStatus.FAILED:
            notification = NotificationMessage(
                message="CANCELLED",
                reference_id=locked_order.id,
                idempotency_key=f"order:{locked_order.id}:CANCELLED",
            )

            await self.notification_port.send_notification(notification)

        return locked_order

    async def _apply_payment_status(
        self, uow: UnitOfWork, order: Order, payment_status: PaymentStatus
    ) -> None:

        if order.payment_status in (PaymentStatus.SUCCEEDED, PaymentStatus.FAILED):
            if order.payment_status == payment_status:
                return

            raise PaymentStatusConflictException()

        if payment_status == PaymentStatus.PENDING:
            order.payment_status = PaymentStatus.PENDING
            order.status = OrderStatus.NEW
            return

        if payment_status == PaymentStatus.SUCCEEDED:
            order.payment_status = PaymentStatus.SUCCEEDED
            order.status = OrderStatus.PAID

            event = OutboxMessageDto(
                event_type=EventType.ORDER_PAID,
                payload={
                    "event_type": EventType.ORDER_PAID.value,
                    "order_id": str(order.id),
                    "item_id": str(order.item_id),
                    "quantity": int(order.quantity),
                    "idempotency_key": str(order.idempotency_key),
                },
            )

            await uow.outbox_repository.save(event)

            logger.info("ORDER_PAID event added to outbox: order_id=%s", order.id)

            return

        if payment_status == PaymentStatus.FAILED:
            order.payment_status = PaymentStatus.FAILED
            order.status = OrderStatus.CANCELLED

            logger.info("Payment failed: order_id=%s", order.id)

            return

        raise InvalidPaymentStatusException()
