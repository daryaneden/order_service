from collections.abc import AsyncIterator

from httpx import AsyncClient

from app.config.setting import settings


async def create_capashino_client() -> AsyncIterator[AsyncClient]:
    async with AsyncClient(
        base_url=settings.CAPASHINO_CLIENT_URL,
        headers={"x-api-key": settings.CAPASHINO_API_KEY.get_secret_value()},
        follow_redirects=True,
    ) as client:
        yield client
