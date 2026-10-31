from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.order_repository import OrderRepository
from app.application.ports.uow import UnitOfWork

class SqlAlchemyUnitOfWork(UnitOfWork):

    def __init__(self, session: AsyncSession, 
                 order_repository: OrderRepository):
        
        self.session = session
        self.order_repository = order_repository

    async def __aenter__(self):

        await self.session.begin()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        
        try:
            if exc_type is not None:
                await self.session.rollback()
            else:
                await self.session.commit()
        finally:
            await self.session.close()