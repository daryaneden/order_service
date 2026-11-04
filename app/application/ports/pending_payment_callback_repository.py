from abc import ABC, abstractmethod
from uuid import UUID

from app.application.dtos.pending_payment_callback_dto import PendingPaymentCallbackDto

class PendingPaymentCallbackRepository(ABC):

    @abstractmethod
    async def save(self, callback: PendingPaymentCallbackDto) -> None:
        pass

    @abstractmethod
    async def delete(self, callback_id: UUID) -> None:
        pass

    @abstractmethod
    async def get_all_by_order_id(
            self,
            order_id: UUID,
        ) -> list[PendingPaymentCallbackDto]:
        pass