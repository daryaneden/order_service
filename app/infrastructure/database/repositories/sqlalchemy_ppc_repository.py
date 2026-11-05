from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.dtos.pending_payment_callback_dto import PendingPaymentCallbackDto
from app.application.ports.repositories.pending_payment_callback_repository import (
    PendingPaymentCallbackRepository,
)
from app.infrastructure.database.models.pending_payment_callback import (
    PendingPaymentCallbackModel,
)


class SqlAlchemyPendingPaymentCallbackRepository(PendingPaymentCallbackRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save(self, callback: PendingPaymentCallbackDto) -> None:
        model = PendingPaymentCallbackModel(
            id=callback.id,
            order_id=callback.order_id,
            payment_id=callback.payment_id,
            status=callback.status,
            amount=callback.amount,
        )

        self.session.add(model)

    async def get_all_by_order_id(
        self, order_id: UUID
    ) -> list[PendingPaymentCallbackDto]:
        stmt = (
            select(PendingPaymentCallbackModel)
            .where(PendingPaymentCallbackModel.order_id == order_id)
            .order_by(PendingPaymentCallbackModel.created_at)
        )

        result = await self.session.execute(stmt)
        models = result.scalars().all()

        return [
            PendingPaymentCallbackDto(
                id=model.id,
                order_id=model.order_id,
                payment_id=model.payment_id,
                status=model.status,
                amount=model.amount,
            )
            for model in models
        ]

    async def delete(self, callback_id: UUID) -> None:
        stmt = delete(PendingPaymentCallbackModel).where(
            PendingPaymentCallbackModel.id == callback_id
        )

        await self.session.execute(stmt)
