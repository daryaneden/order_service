from dataclasses import dataclass
from uuid import UUID

@dataclass
class NotificationMessage:
    message: str
    reference_id: UUID
    idempotency_key: str