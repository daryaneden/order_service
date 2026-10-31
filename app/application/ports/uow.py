from abc import ABC, abstractmethod


from app.application.ports.order_repository import OrderRepository


class UnitOfWork(ABC):

    order_repository: OrderRepository

    async def __aenter__(self):
        return self

    @abstractmethod
    async def __aexit__(self, exc_type, exc_value, traceback):
        pass
