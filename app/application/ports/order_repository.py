from abc import ABC, abstractmethod
from uuid import UUID

from app.application.dtos.order import OrderDto
from app.domain.entities.order import Order

class OrderRepository(ABC):

    @abstractmethod
    async def create_order(order: OrderDto) -> Order:
        pass

    @abstractmethod
    async def get_order_by_id(self, order_id: UUID) -> Order:
        pass

    @abstractmethod
    async def get_by_idempotency_key(self, idempotency_key: str) -> Order | None:
            pass

    @abstractmethod
    async def update_order(self, order: Order) -> Order:
        pass