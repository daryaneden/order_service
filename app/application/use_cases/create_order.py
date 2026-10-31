from uuid import UUID, uuid4

from app.application.ports.uow_factory import UnitOfWorkFactory
from app.application.dtos.order import OrderDto
from app.application.dtos.payment_dtos import CreatePaymentDto
from app.application.ports.catalog_port import CatalogPort
from app.application.ports.payment_port import PaymentPort
from app.application.exceptions import InsufficientQuantityError, ItemOutOfStockError, PaymentCreationException, PaymentCreationUnknownException
from app.domain.entities.order import Order
from app.domain.enums.order_status import OrderStatus

class CreateOrderUseCase():

    def __init__(self, uow_factory: UnitOfWorkFactory,
        catalog_port: CatalogPort,
        payment_port: PaymentPort,
        callback_url: str):
        
        self.uow_factory = uow_factory
        self.catalog_port = catalog_port
        self.payment_port = payment_port
        self.callback_url = callback_url

    async def __call__(self, order_data: OrderDto):
        async with self.uow_factory() as uow:
            existing_order = await uow.order_repository.get_by_idempotency_key(
                order_data.idempotency_key
            )

        if existing_order is not None:
            if existing_order.status in (OrderStatus.PAID,
                                         OrderStatus.CANCELLED):
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
            idempotency_key=order_data.idempotency_key)

        async with self.uow_factory() as uow:
            await uow.order_repository.create_order(order)

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

        except PaymentCreationUnknownException:
            raise

        except PaymentCreationException:
            async with self.uow_factory() as uow:
                order.status = OrderStatus.CANCELLED
                await uow.order_repository.update_order(order)

            raise

        async with self.uow_factory() as uow:
            order.payment_id = payment.id
            order.payment_status = payment.status
            await uow.order_repository.update_order(order)

        return order