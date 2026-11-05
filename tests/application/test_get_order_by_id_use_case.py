from uuid import uuid4

import pytest

from app.application.exceptions import OrderNotFoundException


@pytest.mark.asyncio
async def test_returns_order_when_found(
    get_order_use_case,
    order_repository,
    pending_order,
):
    order_repository.get_order_by_id.return_value = pending_order

    result = await get_order_use_case(pending_order.id)

    assert result is pending_order
    order_repository.get_order_by_id.assert_awaited_once_with(
        pending_order.id
    )

@pytest.mark.asyncio
async def test_raises_exception_when_order_not_found(
    get_order_use_case,
    order_repository,
):
    order_id = uuid4()
    order_repository.get_order_by_id.return_value = None

    with pytest.raises(OrderNotFoundException):
        await get_order_use_case(order_id)

    order_repository.get_order_by_id.assert_awaited_once_with(order_id)
