from abc import ABC, abstractmethod

from app.application.ports.uow import UnitOfWork


class UnitOfWorkFactory(ABC):

    @abstractmethod
    def __call__(self) -> UnitOfWork:
        pass