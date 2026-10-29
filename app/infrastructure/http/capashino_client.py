from httpx import AsyncClient

from app.config.setting import settings

def create_capashino_client() -> AsyncClient:
    print(f"CAPASHINO_CLIENT_URL: {settings.CAPASHINO_CLIENT_URL!r}")
    return AsyncClient(base_url=settings.CAPASHINO_CLIENT_URL,
                       headers={'x-api-key': settings.CAPASHINO_API_KEY},
                       follow_redirects=True)