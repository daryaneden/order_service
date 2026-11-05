from uuid import UUID

from app.application.exceptions import OrderNotFoundException
from app.application.ports.repositories.order_repository import OrderRepository
from app.domain.entities.order import Order


class GetOrderUseCase:

    def __init__(self, order_repository: OrderRepository):
        self.repository = order_repository

    async def __call__(self, order_id: UUID) -> Order:
        order = await self.repository.get_order_by_id(order_id)

        if order is None:
            raise OrderNotFoundException(order_id)

        return order
