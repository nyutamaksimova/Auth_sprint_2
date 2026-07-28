import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    redis_host: str = 'localhost'
    redis_port: int = 6379

    DB_HOST: str
    DB_PORT: int

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_ECHO: bool

    REDIS_HOST: str
    REDIS_PORT: int

    JWT_SECRET: str
    JWT_ALGORITHM: str

    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    ADMIN_EMAIL: str | None = None
    ADMIN_PASSWORD: str | None = None

    YANDEX_CLIENT_ID : str
    YANDEX_CLIENT_SECRET : str

    YANDEX_REDIRECT_URI : str

    YANDEX_AUTHORIZE_URL : str = "https://oauth.yandex.ru/authorize"
    YANDEX_TOKEN_URL : str = "https://oauth.yandex.ru/token"
    YANDEX_USERINFO_URL : str = "https://login.yandex.ru/info"

    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        extra="ignore",
    )


settings = Settings()
