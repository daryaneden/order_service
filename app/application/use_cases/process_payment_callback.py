from app.application.dtos.payment_dtos import PaymentCallbackDto
from app.application.dtos.outbox_message import OutboxMessageDto, EventType
from app.application.dtos.pending_payment_callback_dto import PendingPaymentCallbackDto
from app.application.ports.uow_factory import UnitOfWorkFactory
from app.application.exceptions import OrderNotFoundException, PaymentMismatchException, PaymentAmountMismatchException, PaymentStatusConflictException, InvalidPaymentStatusException, PaymentNotReadyException
from app.domain.enums.payment_status import PaymentStatus
from app.domain.enums.order_status import OrderStatus
from app.application.dtos.notification_message import NotificationMessage
from app.application.ports.notification_port import NotificationPort

import logging
from uuid import uuid4

logger = logging.getLogger(__name__)

class ProcessPaymentCallbackUseCase:

    def __init__(self, uow_factory: UnitOfWorkFactory,
                 notification_port: NotificationPort,):
        self.uow_factory = uow_factory
        self.notification_port = notification_port

    async def __call__(self, callback: PaymentCallbackDto):
        logger.info(
                "Received payment callback: order_id=%s, payment_id=%s, status=%s, amount=%s",
                callback.order_id,
                callback.payment_id,
                callback.status,
                callback.amount,
            )
        async with self.uow_factory() as uow:
            order = await uow.order_repository.get_order_by_id_for_update(callback.order_id)

            if order is None:
                logger.warning(
                "Payment callback references unknown order: order_id=%s",
                callback.order_id,
            )
                raise OrderNotFoundException()

            logger.info(
            "Found order: order_id=%s, stored_payment_id=%s, "
            "callback_payment_id=%s, order_status=%s, payment_status=%s",
            order.id,
            order.payment_id,
            callback.payment_id,
            order.status,
            order.payment_status,
        )
            
            if order.payment_id is None:
                logger.warning(
                    "Payment callback arrived before payment_id was saved: "
                    "order_id=%s, callback_payment_id=%s",
                    order.id,
                    callback.payment_id,
                )
                
                pending_callback = PendingPaymentCallbackDto(id=uuid4(),
                                                            order_id=callback.order_id,
                                                            payment_id=callback.payment_id,
                                                            status=callback.status,
                                                            amount=callback.amount)
            
                await uow.pending_payment_callback_repository.save(pending_callback)

                return

            if order.payment_id != callback.payment_id:
                logger.error(
                    "Payment ID mismatch: order_id=%s, stored_payment_id=%s, "
                    "callback_payment_id=%s",
                    order.id,
                    order.payment_id,
                    callback.payment_id,
                )
                raise PaymentMismatchException()

            expected_amount = order.unit_price * order.quantity

            if expected_amount != callback.amount:
                raise PaymentAmountMismatchException()

            if (
                order.payment_status == PaymentStatus.SUCCEEDED
                and order.status == OrderStatus.PAID
                and callback.status == PaymentStatus.SUCCEEDED
            ):
                return

            if (
                order.payment_status == PaymentStatus.FAILED
                and order.status == OrderStatus.CANCELLED
                and callback.status == PaymentStatus.FAILED
            ):
                return

            if order.payment_status in (
                PaymentStatus.SUCCEEDED,
                PaymentStatus.FAILED,
            ):
                raise PaymentStatusConflictException()

            if order.payment_status != PaymentStatus.PENDING:
                raise PaymentStatusConflictException()

            if callback.status == PaymentStatus.SUCCEEDED:
                order.payment_status = PaymentStatus.SUCCEEDED
                order.status = OrderStatus.PAID

                event = OutboxMessageDto(event_type=EventType.ORDER_PAID,
                                         payload={"event_type": EventType.ORDER_PAID.value,
                                                  "order_id": str(order.id),
                                                  "item_id": str(order.item_id),
                                                  "quantity": int(order.quantity),
                                                  "idempotency_key": str(order.idempotency_key)})

                await uow.outbox_repository.save(event)

            elif callback.status == PaymentStatus.FAILED:
                order.payment_status = PaymentStatus.FAILED
                order.status = OrderStatus.CANCELLED

            else:
                raise InvalidPaymentStatusException()

            await uow.order_repository.update_order(order)

        if callback.status == PaymentStatus.SUCCEEDED:
            notification = NotificationMessage(
                message="Your order has been paid",
                reference_id=order.id,
                idempotency_key=f"order:{order.id}:PAID",
            )
            await self.notification_port.send_notification(notification)

        elif callback.status == PaymentStatus.FAILED:
            notification = NotificationMessage(
                message="Your order has been cancelled because the payment failed",
                reference_id=order.id,
                idempotency_key=f"order:{order.id}:CANCELLED",
            )
            await self.notification_port.send_notification(notification)