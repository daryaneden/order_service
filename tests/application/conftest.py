from decimal import Decimal
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from app.application.dtos.outbox_message import EventType
from app.application.use_cases.create_order import CreateOrderUseCase
from app.application.use_cases.get_order_by_id import GetOrderUseCase
from app.application.use_cases.process_outbox import ProcessOutboxUseCase
from app.application.use_cases.process_payment_callback import (
    ProcessPaymentCallbackUseCase,
)
from app.application.use_cases.process_shipping_event import ProcessShippingEventUseCase
from app.domain.enums.order_status import OrderStatus
from app.domain.enums.payment_status import PaymentStatus


@pytest.fixture
def uow(order_repository,
                 outbox_repository,
                 inbox_repository,
                 pending_payment_callback_repository):
    uow = AsyncMock()
    uow.order_repository = order_repository
    uow.outbox_repository = outbox_repository
    uow.inbox_repository = inbox_repository
    uow.pending_payment_callback_repository = pending_payment_callback_repository
    uow.__aenter__.return_value = uow
    uow.__aexit__.return_value = None
    return uow

@pytest.fixture
def uow_factory(uow):
    factory = Mock(return_value=uow)
    return factory

@pytest.fixture
def order_repository():

    repository = Mock()
    repository.get_by_idempotency_key = AsyncMock()
    repository.create_order = AsyncMock()
    repository.get_order_by_id = AsyncMock()
    repository.get_order_by_id_for_update = AsyncMock()
    repository.update_order = AsyncMock()
    return repository

@pytest.fixture
def outbox_repository():
    repository = Mock()
    repository.save = AsyncMock()
    repository.get_pending = AsyncMock()
    repository.mark_as_published = AsyncMock()
    return repository

@pytest.fixture
def inbox_repository():
    repository = Mock()
    repository.is_processed = AsyncMock(return_value=False)
    repository.add = AsyncMock()
    return repository

@pytest.fixture
def pending_payment_callback_repository():
    repository = AsyncMock()
    repository.get_all_by_order_id = AsyncMock()
    repository.delete = AsyncMock()
    return repository

@pytest.fixture
def catalog_port():
    port = Mock()
    port.get_item = AsyncMock()
    return port


@pytest.fixture
def payment_port():
    port = Mock()
    port.create_payment = AsyncMock()
    return port


@pytest.fixture
def notification_port():
    port = Mock()
    port.send_notification = AsyncMock()
    return port

@pytest.fixture
def order_data():
    data = Mock()
    data.idempotency_key = "test-idempotency-key"
    data.user_id = uuid4()
    data.item_id = uuid4()
    data.quantity = 2
    return data

@pytest.fixture
def existing_paid_order():
    order = Mock()
    order.status = OrderStatus.PAID
    return order


@pytest.fixture
def item():
    item = Mock()
    item = Mock()
    item.available_qty = 10
    item.price = Decimal("100.00")
    return item

@pytest.fixture
def payment():
    payment = Mock()
    payment.id = uuid4()
    payment.status = PaymentStatus.SUCCEEDED
    return payment

@pytest.fixture
def create_order_use_case(uow_factory,
                          catalog_port,
                          payment_port,
                          notification_port):
    return CreateOrderUseCase(
        uow_factory=uow_factory,
        catalog_port=catalog_port,
        payment_port=payment_port,
        notification_port=notification_port,
        callback_url="https://example.com/callback",
    )

@pytest.fixture
def order_repository_with_saved_order(order_repository):
    async def create_order_side_effect(order):
        order_repository.created_order = order

    async def get_order_side_effect(order_id):
        return order_repository.created_order

    order_repository.create_order.side_effect = create_order_side_effect
    order_repository.get_order_by_id_for_update.side_effect = (
        get_order_side_effect
    )

    return order_repository

@pytest.fixture
def pending_order():
    order = Mock()
    order.id = uuid4()
    order.user_id = uuid4()
    order.item_id = uuid4()
    order.idempotency_key = "test-idempotency-key"
    order.quantity = 2
    order.unit_price = Decimal("100.00")
    order.payment_id = uuid4()
    order.status = OrderStatus.NEW
    order.payment_status = PaymentStatus.PENDING
    return order


@pytest.fixture
def payment_callback(pending_order):
    callback = Mock()
    callback.order_id = pending_order.id
    callback.payment_id = pending_order.payment_id
    callback.status = PaymentStatus.SUCCEEDED
    callback.amount = Decimal("200.00")
    return callback


@pytest.fixture
def process_payment_callback_use_case(
    uow_factory,
    notification_port,
):
    return ProcessPaymentCallbackUseCase(
        uow_factory=uow_factory,
        notification_port=notification_port,
    )

@pytest.fixture
def shipping_order():
    order = Mock()
    order.id = uuid4()
    order.status = OrderStatus.PAID

    def ship():
        order.status = OrderStatus.SHIPPED

    def cancel():
        order.status = OrderStatus.CANCELLED

    order.ship.side_effect = ship
    order.cancel.side_effect = cancel

    return order


@pytest.fixture
def shipping_event_payload(shipping_order):
    return {
        "event_type": EventType.ORDER_SHIPPED,
        "order_id": str(shipping_order.id),
    }

@pytest.fixture
def process_shipping_event_use_case(
    uow_factory,
    notification_port,
):
    return ProcessShippingEventUseCase(
        uow_factory=uow_factory,
        notification_port=notification_port,
    )

@pytest.fixture
def event_publisher():
    publisher = Mock()
    publisher.publish = AsyncMock()
    return publisher

@pytest.fixture
def process_outbox_use_case(uow_factory, event_publisher):
    return ProcessOutboxUseCase(
        uow_factory=uow_factory,
        event_publisher=event_publisher,
    )

@pytest.fixture
def outbox_message():
    message = Mock()
    message.id = uuid4()
    message.payload = {
        "event_type": "order.paid",
        "order_id": str(uuid4()),
    }
    return message


@pytest.fixture
def outbox_messages(outbox_message):
    second_message = Mock()
    second_message.id = uuid4()
    second_message.payload = {
        "event_type": "order.paid",
        "order_id": str(uuid4()),
    }

    return [outbox_message, second_message]

@pytest.fixture
def get_order_use_case(order_repository):
    return GetOrderUseCase(order_repository)
