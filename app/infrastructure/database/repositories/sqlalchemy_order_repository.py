from uuid import UUID

from sqlalchemy import select

from app.application.ports.order_repository import OrderRepository
from app.application.dtos.order import OrderDto
from app.infrastructure.database.models.order import OrderModel
from app.domain.entities.order import Order

class SqlAlchemyOrderRepository(OrderRepository):

    def __init__(self, session):
        self.session = session

    async def create_order(self, order: OrderDto) -> Order:
        order_model = OrderModel(
                id=order.id,
                user_id=order.user_id,
                item_id=order.item_id,
                quantity=order.quantity,
                unit_price=order.unit_price,
                status=order.status,
                idempotency_key=order.idempotency_key)
        
        self.session.add(order_model)
        await self.session.flush()
        
        return self._to_entity(order_model)

    async def get_order_by_id(self, order_id: UUID) -> Order | None:
        query = select(OrderModel).where(OrderModel.id == order_id)

        result = await self.session.execute(query)
        order_model = result.scalar_one_or_none()

        if order_model is None:
            return None

        return self._to_entity(order_model)

    async def get_by_idempotency_key(self, idempotency_key: str) -> Order | None:
        result = await self.session.execute(
        select(OrderModel).where(OrderModel.idempotency_key == idempotency_key))
        order_model = result.scalar_one_or_none()

        if order_model is None:
            return None

        return self._to_entity(order_model)

    def _to_entity(self, order_model: OrderModel) -> Order:
        return Order(
            id=order_model.id,
            user_id=order_model.user_id,
            item_id=order_model.item_id,
            quantity=order_model.quantity,
            unit_price=order_model.unit_price,
            status=order_model.status,
            idempotency_key=order_model.idempotency_key,
            created_at=order_model.created_at,
            updated_at=order_model.updated_at)