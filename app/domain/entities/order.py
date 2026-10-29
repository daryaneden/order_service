from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from decimal import Decimal

from app.domain.enums.order_status import OrderStatus
from app.domain.exceptions.order_exceptions import InvalidOrderQuantityError, InvalidOrderPriceError

@dataclass
class Order:
    id: UUID
    user_id: str
    quantity: int
    item_id: UUID
    unit_price: Decimal
    status: OrderStatus
    idempotency_key: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise InvalidOrderQuantityError()

        if self.unit_price < 0:
            raise InvalidOrderPriceError()