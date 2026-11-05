from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from app.domain.enums.order_status import OrderStatus
from app.domain.enums.payment_status import PaymentStatus
from app.domain.exceptions import (
    InvalidOrderPriceError,
    InvalidOrderQuantityError,
    InvalidOrderStatusTransitionError,
)


@dataclass
class Order:
    id: UUID
    user_id: str
    quantity: int
    item_id: UUID
    unit_price: Decimal
    status: OrderStatus
    idempotency_key: str
    payment_id: UUID | None = None
    payment_status: PaymentStatus | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise InvalidOrderQuantityError()

        if self.unit_price < 0:
            raise InvalidOrderPriceError()

    def ship(self) -> None:
        if self.status == OrderStatus.SHIPPED:
            return

        if self.status != OrderStatus.PAID:
            raise InvalidOrderStatusTransitionError(self.status, OrderStatus.SHIPPED)

        self.status = OrderStatus.SHIPPED

    def cancel(self) -> None:

        if self.status == OrderStatus.CANCELLED:
            return

        if self.status == OrderStatus.SHIPPED:
            raise InvalidOrderStatusTransitionError(self.status, OrderStatus.CANCELLED)

        self.status = OrderStatus.CANCELLED
