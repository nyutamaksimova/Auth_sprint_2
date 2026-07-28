from pydantic import Field
from pydantic_settings import BaseSettings

from tests.functional.testdata.es_mapping import MOVIES_MAPPING


class TestSettings(BaseSettings):
    es_host: str = Field('http://elasticsearch:9200')
    es_index: str = 'movies'
    es_id_field: str = 'uuid'
    es_index_mapping: dict = MOVIES_MAPPING

    redis_host: str = Field(default='redis://redis:6379')

    service_url: str = Field(default='http://api:8000')


test_settings = TestSettings()
