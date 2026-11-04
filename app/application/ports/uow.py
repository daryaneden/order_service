from abc import ABC, abstractmethod


from app.application.ports.order_repository import OrderRepository
from app.application.ports.outbox_repository import OutboxRepository
from app.application.ports.inbox_repository import InboxRepository
from app.application.ports.pending_payment_callback_repository import PendingPaymentCallbackRepository

class UnitOfWork(ABC):

    order_repository: OrderRepository
    outbox_repository: OutboxRepository
    inbox_repository: InboxRepository
    pending_payment_callback_repository: PendingPaymentCallbackRepository


    async def __aenter__(self):
        return self

    @abstractmethod
    async def __aexit__(self, exc_type, exc_value, traceback):
        pass
