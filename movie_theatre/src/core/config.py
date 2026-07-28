from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='allow')

    project_name: str = 'Онлайн-кинотеатр'
    redis_host: str = 'localhost'
    redis_port: int = 6379
    elastic_host: str = 'elasticsearch'
    elastic_port: int = 9200

    log_level: str = 'INFO'

    jwt_secret_key: str
    jwt_algorithm: str


settings = Settings()
