from collections.abc import AsyncIterator

from httpx import AsyncClient

from app.config.setting import settings


# def create_capashino_client() -> AsyncClient:
#     return AsyncClient(
#         base_url=settings.CAPASHINO_CLIENT_URL,
#         headers={"x-api-key": settings.CAPASHINO_API_KEY},
#         follow_redirects=True,
#     )

async def create_capashino_client() -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
        base_url=settings.CAPASHINO_CLIENT_URL,
        headers={"x-api-key": settings.CAPASHINO_API_KEY},
        follow_redirects=True,
    ) as client:
        yield client