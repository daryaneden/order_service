from app.presentation.api.schemas.order_response import OrderResponse
from app.domain.entities.order import Order


def to_order_response(order: Order) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        user_id=order.user_id,
        quantity=order.quantity,
        item_id=order.item_id,
        status=order.status,
        created_at=order.created_at,
        updated_at=order.updated_at)