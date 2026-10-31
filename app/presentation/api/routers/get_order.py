from typing import Annotated
from uuid import UUID

from fastapi import APIRouter,status, Depends, HTTPException

from app.presentation.api.dependencies import get_get_order_by_id_use_case
from app.presentation.api.schemas.order_response import OrderResponse
from app.application.use_cases.get_order_by_id import GetOrderUseCase
from app.application.exceptions import OrderNotFoundException
router = APIRouter(prefix="/api/orders", tags=["Orders"])

@router.get("/{order_id}",response_model=OrderResponse, status_code=200)
async def get_order(order_id: UUID,
    use_case: Annotated[GetOrderUseCase, Depends(get_get_order_by_id_use_case)]) -> OrderResponse:
    try:
        use_case(order_id)
    except OrderNotFoundException as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                    detail=exc.detail) from exc