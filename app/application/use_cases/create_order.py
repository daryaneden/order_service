from uuid import UUID, uuid4

from app.application.ports.order_repository import OrderRepository
from app.application.dtos.order import OrderDto
from app.application.ports.catalog_port import CatalogPort
from app.application.exceptions import InsufficientQuantityError, ItemOutOfStockError
from app.domain.entities.order import Order
from app.domain.enums.order_status import OrderStatus

class CreateOrderUseCase():

    def __init__(self, order_repository: OrderRepository,
                 catalog_port: CatalogPort):
        self.repository = order_repository
        self.catalog_port = catalog_port

    async def execute(self, order: OrderDto):

        existing_order = (await self.repository.get_by_idempotency_key(order.idempotency_key))

        if existing_order is not None:
            return existing_order

        item = await self.catalog_port.get_item(order.item_id)

        if item.available_qty <= 0:
            raise ItemOutOfStockError()

        if item.available_qty < order.quantity:
            raise InsufficientQuantityError()

        order = Order(
            id=uuid4(),
            user_id=order.user_id,
            item_id=order.item_id,
            quantity=order.quantity,
            unit_price=item.price,
            status=OrderStatus.NEW,
            idempotency_key=order.idempotency_key)

        
        return await self.repository.create_order(order)

