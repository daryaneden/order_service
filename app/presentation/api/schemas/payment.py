from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.domain.enums.payment_status import PaymentStatus


class PaymentCallbackRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    payment_id: UUID
    order_id: UUID
    status: PaymentStatus
    amount: Decimal
    error_message: str | None = None