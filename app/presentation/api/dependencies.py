from typing import Annotated

from fastapi import Depends
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.create_order import CreateOrderUseCase
from app.application.use_cases.get_order_by_id import GetOrderUseCase
from app.infrastructure.capashino_clients.catalog_client import CatalogClient
from app.infrastructure.http.capashino_client import create_capashino_client
from app.infrastructure.database.db import get_db_session, AsyncSessionFactory
from app.infrastructure.database.repositories.sqlalchemy_order_repository import SqlAlchemyOrderRepository
from app.infrastructure.uow.sqlalchemy_uow import SqlAlchemyUnitOfWork
from app.infrastructure.uow.sqlalchemy_uow_factory import SqlAlchemyUnitOfWorkFactory
from app.application.use_cases.process_payment_callback import ProcessPaymentCallbackUseCase
from app.config.setting import settings
def get_catalog_client(client: Annotated[AsyncClient, Depends(create_capashino_client)]) -> CatalogClient:
    return CatalogClient(client)

def get_order_repository(session: Annotated[AsyncSession, Depends(get_db_session)]) -> SqlAlchemyOrderRepository:
    return SqlAlchemyOrderRepository(session)

def build_uow(session: Annotated[AsyncSession, Depends(get_db_session)]) -> SqlAlchemyUnitOfWork:

    order_repository = SqlAlchemyOrderRepository(session)

    return SqlAlchemyUnitOfWork(session=session,
        order_repository=order_repository)

def get_uow_factory() -> SqlAlchemyUnitOfWorkFactory:
    return SqlAlchemyUnitOfWorkFactory(session_factory=AsyncSessionFactory,
                                       uow_builder=build_uow)

def get_create_order_use_case(order_repository: Annotated[SqlAlchemyOrderRepository, Depends(get_order_repository)],
                              catalog_port: Annotated[CatalogClient, Depends(get_catalog_client)],
                              uow_factory: Annotated[SqlAlchemyUnitOfWorkFactory, Depends(get_uow_factory)],
                              callback_url=settings.PAYMENT_CALLBACK_URL) -> CreateOrderUseCase:
    
    return CreateOrderUseCase(uow_factory, 
                              catalog_port, 
                              order_repository, 
                              callback_url)

def get_get_order_by_id_use_case(order_repository: Annotated[SqlAlchemyOrderRepository, Depends(get_order_repository)]) -> GetOrderUseCase:
    return GetOrderUseCase(order_repository)


def get_process_payment_callback_use_case(uow_factory: Annotated[SqlAlchemyUnitOfWorkFactory, Depends(get_uow_factory)]) -> ProcessPaymentCallbackUseCase:
    return ProcessPaymentCallbackUseCase(uow_factory=uow_factory)