from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    model_config = SettingsConfigDict(env_file='.env',
                                      env_file_encoding='utf-8')
     
    CAPASHINO_CLIENT_URL: str
    CAPASHINO_API_KEY: str

    POSTGRES_HOST: str = 'db'
    POSTGRES_PORT: int = 5432
    POSTGRES_USERNAME: str = 'postgres'
    POSTGRES_PASSWORD: str = 'password'
    DB_DRIVER: str = 'postgresql+asyncpg'
    POSTGRES_DB: str = 'order_service'


    @property
    def db_url(self):
        return f'{self.DB_DRIVER}://{self.POSTGRES_USERNAME}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'

settings = Settings()


