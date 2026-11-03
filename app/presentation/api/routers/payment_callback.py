from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.presentation.api.schemas.payment import PaymentCallbackRequest
from app.presentation.api.mappers.payment_mapper import to_payment_callback_dto
from app.application.use_cases.process_payment_callback import ProcessPaymentCallbackUseCase
from app.presentation.api.dependencies import get_process_payment_callback_use_case
from app.application.exceptions import PaymentNotReadyException

router = APIRouter(prefix="/api/orders", tags=["Orders"])

@router.post("/payment-callback", status_code=200)
async def payment_callback(callback_data: PaymentCallbackRequest,
    use_case: Annotated[ProcessPaymentCallbackUseCase, Depends(get_process_payment_callback_use_case)]):
    
    try:
        await use_case(callback_data)
    except PaymentNotReadyException as exc:
        raise HTTPException(
            status_code=503,
            detail="Payment is not ready yet",
        ) from exc