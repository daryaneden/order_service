import pytest

from app.domain.enums.order_status import OrderStatus
from app.domain.enums.payment_status import PaymentStatus


@pytest.mark.asyncio
async def test_processes_successful_payment_callback(
    process_payment_callback_use_case,
    order_repository,
    order_repository_with_saved_order,
    outbox_repository,
    notification_port,
    pending_order,
    payment_callback,
):
    # Arrange
    order_repository.created_order = pending_order

    # Act
    await process_payment_callback_use_case(payment_callback)

    # Assert
    assert pending_order.payment_status == PaymentStatus.SUCCEEDED
    assert pending_order.status == OrderStatus.PAID

    order_repository.update_order.assert_awaited_once_with(pending_order)
    outbox_repository.save.assert_awaited_once()
    notification_port.send_notification.assert_awaited_once()

    notification = notification_port.send_notification.await_args.args[0]

    assert notification.message == "PAID"
    assert notification.idempotency_key == (
        f"order:{pending_order.id}:PAID"
    )

@pytest.mark.asyncio
async def test_processes_failed_payment_callback(
    process_payment_callback_use_case,
    order_repository,
    order_repository_with_saved_order,
    outbox_repository,
    notification_port,
    pending_order,
    payment_callback,
):
    # Arrange
    order_repository.created_order = pending_order
    payment_callback.status = PaymentStatus.FAILED

    # Act
    await process_payment_callback_use_case(payment_callback)

    # Assert
    assert pending_order.payment_status == PaymentStatus.FAILED
    assert pending_order.status == OrderStatus.CANCELLED

    order_repository.update_order.assert_awaited_once_with(pending_order)
    outbox_repository.save.assert_not_awaited()
    notification_port.send_notification.assert_awaited_once()

    notification = notification_port.send_notification.await_args.args[0]

    assert notification.message == "CANCELLED"
    assert notification.idempotency_key == (
        f"order:{pending_order.id}:CANCELLED"
    )

@pytest.mark.asyncio
async def test_saves_pending_callback_when_payment_id_is_not_saved(
    process_payment_callback_use_case,
    order_repository,
    order_repository_with_saved_order,
    pending_payment_callback_repository,
    notification_port,
    pending_order,
    payment_callback,
):
    # Arrange
    order_repository.created_order = pending_order
    pending_order.payment_id = None

    # Act
    result = await process_payment_callback_use_case(payment_callback)

    # Assert
    assert result is None

    pending_payment_callback_repository.save.assert_awaited_once()

    saved_callback = (
        pending_payment_callback_repository.save.await_args.args[0]
    )

    assert saved_callback.order_id == payment_callback.order_id
    assert saved_callback.payment_id == payment_callback.payment_id

    order_repository.update_order.assert_not_awaited()
    notification_port.send_notification.assert_not_awaited()

@pytest.mark.asyncio
async def test_ignores_duplicate_successful_callback(
    process_payment_callback_use_case,
    order_repository,
    order_repository_with_saved_order,
    outbox_repository,
    notification_port,
    pending_order,
    payment_callback,
):
    # Arrange
    order_repository.created_order = pending_order

    pending_order.payment_status = PaymentStatus.SUCCEEDED
    pending_order.status = OrderStatus.PAID

    # Act
    result = await process_payment_callback_use_case(payment_callback)

    # Assert
    assert result is None

    order_repository.update_order.assert_not_awaited()
    outbox_repository.save.assert_not_awaited()
    notification_port.send_notification.assert_not_awaited()
