from app.application.dtos.payment_dtos import PaymentCallbackDto
from app.presentation.api.schemas.payment import PaymentCallbackRequest


def to_payment_callback_dto(callback_data: PaymentCallbackRequest) -> PaymentCallbackDto:
    return PaymentCallbackDto(
        payment_id=callback_data.payment_id,
        order_id=callback_data.order_id,
        status=callback_data.status,
        amount=callback_data.amount,
        error_message=callback_data.error_message
    )