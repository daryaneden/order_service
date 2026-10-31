from typing import Annotated

from fastapi import APIRouter,status, Depends, HTTPException

from app.presentation.api.schemas.order_response import OrderResponse
from app.presentation.api.schemas.create_order_request import CreateOrderRequest
from app.application.use_cases.create_order import CreateOrderUseCase
from app.presentation.api.dependencies import get_create_order_use_case
from app.presentation.api.mappers.to_order_response import to_order_response
from app.application.exceptions import InsufficientQuantityError, ItemOutOfStockError

router = APIRouter(prefix="/api/orders", tags=["Orders"])


@router.post("",response_model=OrderResponse,
             status_code=status.HTTP_201_CREATED)
async def create_order(data: CreateOrderRequest,
                       use_case: Annotated[CreateOrderUseCase, Depends(get_create_order_use_case)]) -> OrderResponse:

    try:
        order = await use_case(data)
    except InsufficientQuantityError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.detail) from exc
    except ItemOutOfStockError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail=exc.detail) from exc

    return to_order_response(order)