from decimal import Decimal
from uuid import UUID

from httpx import AsyncClient

from app.application.ports.catalog_port import CatalogPort
from app.domain.entities.catalog_item import CatalogItem


class CatalogClient(CatalogPort):
    def __init__(self, client: AsyncClient):
        self.client = client

    async def get_item(self, item_id: UUID) -> CatalogItem:
        response = await self.client.get(f"/api/catalog/items/{item_id}")
        response.raise_for_status()

        data = response.json()

        return CatalogItem(
            id=UUID(data["id"]),
            name=data["name"],
            price=Decimal(data["price"]),
            available_qty=data["available_qty"],
        )
