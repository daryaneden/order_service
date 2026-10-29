from dataclasses import dataclass
from uuid import UUID

@dataclass
class OrderDto:
  user_id: UUID
  quantity: int
  item_id: UUID
  idempotency_key: str