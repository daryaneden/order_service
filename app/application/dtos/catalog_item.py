from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass
class CatalogItemDTO:
    id: UUID
    name: str
    price: Decimal
    available_qty: int
