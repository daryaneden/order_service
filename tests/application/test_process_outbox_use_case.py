from unittest.mock import Mock
from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_does_not_publish_when_no_pending_messages(
    process_outbox_use_case,
    outbox_repository,
    event_publisher,
):
    outbox_repository.get_pending.return_value = []

    await process_outbox_use_case(topic="test-topic")

    outbox_repository.get_pending.assert_awaited_once()
    event_publisher.publish.assert_not_awaited()
    outbox_repository.mark_as_published.assert_not_awaited()

@pytest.mark.asyncio
async def test_publishes_pending_messages_successfully(
    process_outbox_use_case,
    outbox_repository,
    event_publisher,
):
    message_1 = Mock()
    message_1.id = uuid4()
    message_1.payload = {
        "event_type": "order.paid",
        "order_id": str(uuid4()),
    }

    message_2 = Mock()
    message_2.id = uuid4()
    message_2.payload = {
        "event_type": "order.paid",
        "order_id": str(uuid4()),
    }

    outbox_repository.get_pending.return_value = [
        message_1,
        message_2,
    ]

    await process_outbox_use_case(topic="test-topic")

    assert event_publisher.publish.await_count == 2

    event_publisher.publish.assert_any_await(
        topic="test-topic",
        message=message_1.payload,
        key=message_1.payload["order_id"],
    )
    event_publisher.publish.assert_any_await(
        topic="test-topic",
        message=message_2.payload,
        key=message_2.payload["order_id"],
    )

    assert outbox_repository.mark_as_published.await_count == 2
    outbox_repository.mark_as_published.assert_any_await(message_1.id)
    outbox_repository.mark_as_published.assert_any_await(message_2.id)
