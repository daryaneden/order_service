import pytest

from app.application.dtos.outbox_message import EventType
from app.domain.enums.order_status import OrderStatus


@pytest.mark.asyncio
async def test_processes_order_shipped_event(
    process_shipping_event_use_case,
    order_repository,
    inbox_repository,
    notification_port,
    shipping_order,
    shipping_event_payload,
):
    # Arrange
    order_repository.get_order_by_id.return_value = shipping_order

    # Act
    await process_shipping_event_use_case(
        shipping_event_payload,
        topic="test-topic",
        partition=0,
        offset=1,
    )

    # Assert
    assert shipping_order.status == OrderStatus.SHIPPED

    order_repository.update_order.assert_awaited_once_with(shipping_order)
    inbox_repository.add.assert_awaited_once_with("test-topic", 0, 1)

    notification_port.send_notification.assert_awaited_once()

    notification = notification_port.send_notification.await_args.args[0]

    assert notification.message == "SHIPPED"
    assert notification.reference_id == shipping_order.id
    assert notification.idempotency_key == (
        f"order:{shipping_order.id}:SHIPPED"
    )

@pytest.mark.asyncio
async def test_processes_order_cancelled_event(
    process_shipping_event_use_case,
    order_repository,
    inbox_repository,
    notification_port,
    shipping_order,
    shipping_event_payload,
):
    # Arrange
    order_repository.get_order_by_id.return_value = shipping_order
    shipping_event_payload["event_type"] = EventType.ORDER_CANCELLED

    # Act
    await process_shipping_event_use_case(
        shipping_event_payload,
        topic="test-topic",
        partition=0,
        offset=2,
    )

    # Assert
    assert shipping_order.status == OrderStatus.CANCELLED

    order_repository.update_order.assert_awaited_once_with(shipping_order)
    inbox_repository.add.assert_awaited_once_with("test-topic", 0, 2)

    notification_port.send_notification.assert_awaited_once()

    notification = notification_port.send_notification.await_args.args[0]

    assert notification.message == "CANCELLED"
    assert notification.reference_id == shipping_order.id
    assert notification.idempotency_key == (
        f"order:{shipping_order.id}:CANCELLED"
    )

@pytest.mark.asyncio
async def test_ignores_already_processed_shipping_event(
    process_shipping_event_use_case,
    order_repository,
    inbox_repository,
    notification_port,
    shipping_event_payload,
):
    # Arrange
    inbox_repository.is_processed.return_value = True

    # Act
    await process_shipping_event_use_case(
        shipping_event_payload,
        topic="test-topic",
        partition=0,
        offset=1,
    )

    # Assert
    inbox_repository.is_processed.assert_awaited_once_with(
        "test-topic", 0, 1
    )

    order_repository.get_order_by_id.assert_not_awaited()
    order_repository.update_order.assert_not_awaited()
    inbox_repository.add.assert_not_awaited()
    notification_port.send_notification.assert_not_awaited()
