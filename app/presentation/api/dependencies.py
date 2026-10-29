from typing import Annotated

from fastapi import Depends
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.use_cases.create_order import CreateOrderUseCase
from app.application.use_cases.get_order_by_id import GetOrderUseCase
from app.infrastructure.capashino_clients.catalog_client import CatalogClient
from app.infrastructure.http.capashino_client import create_capashino_client
from app.infrastructure.database.db import get_db_session
from app.infrastructure.database.repositories.sqlalchemy_order_repository import SqlAlchemyOrderRepository

def get_catalog_client(client: Annotated[AsyncClient, Depends(create_capashino_client)]) -> CatalogClient:
    return CatalogClient(client)

def get_order_repository(session: Annotated[AsyncSession, Depends(get_db_session)]) -> SqlAlchemyOrderRepository:
    return SqlAlchemyOrderRepository(session)

def get_create_order_use_case(order_repository: Annotated[SqlAlchemyOrderRepository, Depends(get_order_repository)],
                              catalog_port: Annotated[CatalogClient, Depends(get_catalog_client)]) -> CreateOrderUseCase:
    return CreateOrderUseCase(order_repository,
                              catalog_port)

def get_get_order_by_id_use_case(order_repository: Annotated[SqlAlchemyOrderRepository, Depends(get_order_repository)]) -> GetOrderUseCase:
    return GetOrderUseCase(order_repository)