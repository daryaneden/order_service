from dataclasses import dataclass
from uuid import UUID

@dataclass
class OrderDto:
  user_id: str
  quantity: int
  item_id: UUID
  idempotency_key: str