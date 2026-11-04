from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from app.domain.enums.payment_status import PaymentStatus

@dataclass
class PendingPaymentCallbackDto:
    id: UUID
    order_id: UUID
    payment_id: UUID
    status: PaymentStatus
    amount: Decimal