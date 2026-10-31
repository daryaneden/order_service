from typing import Annotated

from fastapi import APIRouter, Depends

from app.presentation.api.schemas.payment import PaymentCallbackRequest
from app.presentation.api.mappers.payment_mapper import to_payment_callback_dto
from app.application.use_cases.process_payment_callback import ProcessPaymentCallbackUseCase
from app.presentation.api.dependencies import get_process_payment_callback_use_case

router = APIRouter(prefix="/api/orders", tags=["Orders"])

@router.post("/payment-callback", status_code=200)
async def payment_callback(callback_data: PaymentCallbackRequest,
    use_case: Annotated[ProcessPaymentCallbackUseCase, Depends(get_process_payment_callback_use_case)]):
    
    callback = to_payment_callback_dto(callback_data)

    await use_case(callback)

    return {"message": "Payment callback processed"}
