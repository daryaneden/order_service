from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.domain.enums.order_status import OrderStatus


class OrderResponse(BaseModel):
    id: UUID
    user_id: str
    quantity: int
    item_id: UUID
    status: OrderStatus
    created_at: datetime
    updated_at: datetime