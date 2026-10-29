from uuid import UUID

from app.application.ports.order_repository import OrderRepository
from app.domain.entities.order import Order
from app.application.exceptions import OrderNotFoundException

class GetOrderUseCase():

    def __init__(self, order_repository: OrderRepository):
        self.repository = order_repository

    async def execute(self, order_id: UUID) -> Order:
        order = await self.repository.get_order_by_id(order_id)

        if order is None:
            raise OrderNotFoundException(order_id)

        return order