from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from app.domain.enums.payment_status import PaymentStatus


@dataclass
class CreatePaymentDto:
    order_id: UUID
    amount: Decimal
    callback_url: str
    idempotency_key: str

@dataclass
class PaymentDto:
    id: UUID
    order_id: UUID
    amount: Decimal
    status: PaymentStatus
    idempotency_key: str

@dataclass
class PaymentCallbackDto:
    payment_id: UUID
    order_id: UUID
    status: PaymentStatus
    amount: Decimal
    error_message: str | None = None