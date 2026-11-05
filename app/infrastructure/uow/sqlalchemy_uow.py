from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.repositories.inbox_repository import InboxRepository
from app.application.ports.repositories.order_repository import OrderRepository
from app.application.ports.repositories.outbox_repository import OutboxRepository
from app.application.ports.repositories.pending_payment_callback_repository import (
    PendingPaymentCallbackRepository,
)
from app.application.ports.uow.uow import UnitOfWork


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(
        self,
        session: AsyncSession,
        order_repository: OrderRepository,
        outbox_repository: OutboxRepository,
        inbox_repository: InboxRepository,
        pending_payment_callback_repository: PendingPaymentCallbackRepository,
    ):

        self.session = session
        self.order_repository = order_repository
        self.outbox_repository = outbox_repository
        self.inbox_repository = inbox_repository
        self.pending_payment_callback_repository = pending_payment_callback_repository

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
