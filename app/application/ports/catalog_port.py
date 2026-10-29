from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.catalog_item import CatalogItem


class CatalogPort(ABC):

    @abstractmethod
    async def get_item(self, item_id: UUID) -> CatalogItem:
        pass