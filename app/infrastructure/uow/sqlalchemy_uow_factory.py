from collections.abc import Callable

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.ports.uow_factory import UnitOfWorkFactory
from app.infrastructure.uow.sqlalchemy_uow import SqlAlchemyUnitOfWork


class SqlAlchemyUnitOfWorkFactory(UnitOfWorkFactory):

    def __init__(self, session_factory: async_sessionmaker[AsyncSession],
                 uow_builder: Callable[[AsyncSession], SqlAlchemyUnitOfWork]):
        
        self.session_factory = session_factory
        self.uow_builder = uow_builder

    def __call__(self) -> SqlAlchemyUnitOfWork:
        
        session = self.session_factory()
        return self.uow_builder(session)