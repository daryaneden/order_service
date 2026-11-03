from abc import ABC, abstractmethod


from app.application.ports.order_repository import OrderRepository
from app.application.ports.outbox_repository import OutboxRepository
from app.application.ports.inbox_repository import InboxRepository

class UnitOfWork(ABC):

    order_repository: OrderRepository
    outbox_repository: OutboxRepository
    inbox_repository: InboxRepository


    async def __aenter__(self):
        return self

    @abstractmethod
    async def __aexit__(self, exc_type, exc_value, traceback):
        pass
