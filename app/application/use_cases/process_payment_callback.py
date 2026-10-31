from app.application.dtos.payment_dtos import PaymentCallbackDto
from app.application.ports.uow_factory import UnitOfWorkFactory
from app.application.exceptions import OrderNotFoundException, PaymentMismatchException, PaymentAmountMismatchException, PaymentStatusConflictException, InvalidPaymentStatusException
from app.domain.enums.payment_status import PaymentStatus
from app.domain.enums.order_status import OrderStatus

class ProcessPaymentCallbackUseCase:

    def __init__(self, uow_factory: UnitOfWorkFactory):
        self.uow_factory = uow_factory

    async def __call__(self, callback: PaymentCallbackDto):
        async with self.uow_factory() as uow:
            order = await uow.order_repository.get_order_by_id(
                callback.order_id
            )

            if order is None:
                raise OrderNotFoundException()

            if order.payment_id != callback.payment_id:
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

            elif callback.status == PaymentStatus.FAILED:
                order.payment_status = PaymentStatus.FAILED
                order.status = OrderStatus.CANCELLED

            else:
                raise InvalidPaymentStatusException()

            await uow.order_repository.update_order(order)