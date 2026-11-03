from dataclasses import dataclass
from uuid import UUID
from enum import StrEnum
from typing import Any

class EventType(StrEnum):
    ORDER_PAID = "order.paid"
    ORDER_SHIPPED = "order.shipped"
    ORDER_CANCELLED = "order.cancelled"  

@dataclass
class OutboxMessageDto:
    event_type: EventType
    payload: dict[str, Any]


@dataclass
class PendingOutboxMessage:
    id: UUID
    event_type: EventType
    payload: dict[str, Any]