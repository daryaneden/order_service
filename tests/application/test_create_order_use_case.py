
import pytest

from app.application.exceptions import (
    InsufficientQuantityError,
    ItemOutOfStockError,
)
from app.domain.enums.order_status import OrderStatus
from app.domain.enums.payment_status import PaymentStatus


@pytest.mark.asyncio
async def test_creates_order_and_payment_successfully(
    create_order_use_case,
    uow,
    order_repository,
    outbox_repository,
    catalog_port,
    payment_port,
    notification_port,
    order_data,
    item,
    payment,
):
    catalog_port.get_item.return_value = item
    payment_port.create_payment.return_value = payment

    order_repository.get_by_idempotency_key.return_value = None

    result = await create_order_use_case(order_data)

    assert result.status == OrderStatus.PAID
    assert result.payment_status == PaymentStatus.SUCCEEDED

    catalog_port.get_item.assert_awaited_once_with(order_data.item_id)
    payment_port.create_payment.assert_awaited_once()

    order_repository.create_order.assert_awaited_once()
    order_repository.update_order.assert_awaited_once()

    outbox_repository.save.assert_awaited_once()

    assert notification_port.send_notification.await_count == 2

@pytest.mark.asyncio
async def test_returns_existing_order_without_creating_duplicate(
    create_order_use_case,
    order_repository,
    catalog_port,
    payment_port,
    notification_port,
    order_data,
    existing_paid_order,
):
    order_repository.get_by_idempotency_key.return_value = existing_paid_order

    result = await create_order_use_case(order_data)

    assert result is existing_paid_order

    order_repository.create_order.assert_not_awaited()
    catalog_port.get_item.assert_not_awaited()
    payment_port.create_payment.assert_not_awaited()
    notification_port.send_notification.assert_not_awaited()

@pytest.mark.asyncio
async def test_raises_when_item_is_out_of_stock(
    create_order_use_case,
    order_repository,
    catalog_port,
    payment_port,
    notification_port,
    order_data,
    item,
):
    order_repository.get_by_idempotency_key.return_value = None

    item.available_qty = 0
    catalog_port.get_item.return_value = item

    with pytest.raises(ItemOutOfStockError):
        await create_order_use_case(order_data)

    order_repository.create_order.assert_not_awaited()
    payment_port.create_payment.assert_not_awaited()
    notification_port.send_notification.assert_not_awaited()

@pytest.mark.asyncio
async def test_raises_when_requested_quantity_exceeds_available(
    create_order_use_case,
    order_repository,
    catalog_port,
    payment_port,
    notification_port,
    order_data,
    item,
):
    order_repository.get_by_idempotency_key.return_value = None

    item.available_qty = 1
    order_data.quantity = 2

    catalog_port.get_item.return_value = item

    with pytest.raises(InsufficientQuantityError):
        await create_order_use_case(order_data)

    order_repository.create_order.assert_not_awaited()
    payment_port.create_payment.assert_not_awaited()
    notification_port.send_notification.assert_not_awaited()

@pytest.mark.asyncio
async def test_failed_payment_cancels_order(
    create_order_use_case,
    order_repository,
    outbox_repository,
    catalog_port,
    payment_port,
    notification_port,
    order_data,
    item,
    payment,
    order_repository_with_saved_order,
):
    order_repository.get_by_idempotency_key.return_value = None

    item.available_qty = 10
    catalog_port.get_item.return_value = item

    payment.status = PaymentStatus.FAILED
    payment_port.create_payment.return_value = payment

    result = await create_order_use_case(order_data)

    assert result.status == OrderStatus.CANCELLED
    assert result.payment_status == PaymentStatus.FAILED

    order_repository.create_order.assert_awaited_once()
    order_repository.update_order.assert_awaited_once()

    outbox_repository.save.assert_not_awaited()

    notifications = [
        call.args[0]
        for call in notification_port.send_notification.await_args_list
    ]

    assert [notification.message for notification in notifications] == [
        "NEW",
        "CANCELLED",
    ]
