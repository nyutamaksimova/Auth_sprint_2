import asyncio
import random
import uuid

import aiohttp
import pytest_asyncio
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from redis.asyncio import Redis

from tests.functional.settings import test_settings


@pytest_asyncio.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(name='es_client', scope='session')
async def es_client():
    es_client = AsyncElasticsearch(hosts=test_settings.es_host, verify_certs=False)
    yield es_client
    await es_client.close()


def get_film_for_search():
    return {
        'uuid': str(uuid.uuid4()),
        'imdb_rating': 8.5,
        'genre': [{
            "uuid": '13f92c28-baf8-437b-94bb-d891bd835656',
            "name": "Action"
        },
            {
                "uuid": '13f86c28-baf8-437b-94bb-d891bd835656',
                "name": "Sci-Fi"
            }],
        'title': 'The Star',
        'description': 'New World',
        'directors_names': ['Stan'],
        'actors_names': ['Ann', 'Bob'],
        'writers_names': ['Ben', 'Howard'],
        'actors': [
            {'uuid': 'ef86b8ff-3c82-4d31-ad8e-72b69f4e3f95', 'full_name': 'Ann'},
            {'uuid': 'fb111f22-121e-44a7-b78f-b19191810fbf', 'full_name': 'Bob'}
        ],
        'writers': [
            {'uuid': 'caf76c67-c0fe-477e-8766-3ab3ff2574b5', 'full_name': 'Ben'},
            {'uuid': 'b45bd7bc-2e16-46d5-b125-983d356768c6', 'full_name': 'Howard'}
        ],
        'directors': [
            {'uuid': 'caf76c67-c0fe-477e-8766-3ab3ff2574b5', 'full_name': 'Stan'}
        ]
    }


@pytest_asyncio.fixture(name='movies_data_for_search')
async def movies_data_for_search():
    es_data = [get_film_for_search() for _ in range(60)]

    bulk_query: list[dict] = []
    for row in es_data:
        data = {'_index': 'movies', '_id': row['uuid']}
        data.update({'_source': row})
        bulk_query.append(data)

    return bulk_query


def get_film(genres, i):
    titles = [
        "The Star",
        "Galaxy War",
        "Dark Future",
        "Last Hero",
        "Space Journey",
        "Silent Night",
    ]

    return {
        "uuid": str(uuid.uuid4()),
        "imdb_rating": round(random.uniform(5.0, 9.9), 1),
        "genre": [random.choice(genres)],
        "title": random.choice(titles),
        "description": f"Description {i}",
        "directors_names": [f"Director {i % 5}"],
        "actors_names": [f"Actor {i % 10}", f"Actor {(i + 1) % 10}"],
        "writers_names": [f"Writer {i % 3}"],
        "actors": [
            {
                "uuid": str(uuid.uuid4()),
                "full_name": f"Actor {i % 10}",
            }
        ],
        "writers": [
            {
                "uuid": str(uuid.uuid4()),
                "full_name": f"Writer {i % 3}",
            }
        ],
        "directors": [
            {
                "uuid": str(uuid.uuid4()),
                "full_name": f"Director {i % 5}",
            }
        ],
    }


@pytest_asyncio.fixture(name="movies_data")
async def movies_data():
    bulk_query = []

    genres = [
        {"uuid": str(uuid.uuid4()), "name": "Action"},
        {"uuid": str(uuid.uuid4()), "name": "Sci-Fi"},
        {"uuid": str(uuid.uuid4()), "name": "Drama"},
        {"uuid": str(uuid.uuid4()), "name": "Comedy"},
    ]

    for i in range(60):
        film = get_film(genres, i)

        bulk_query.append({
            "_index": "movies",
            "_id": film["uuid"],
            "_source": film,
        })

    special_uuid = "13f92c28-baf8-437b-94ab-d891bd835656"

    bulk_query.append({
        "_index": "movies",
        "_id": special_uuid,
        "_source": {
            "uuid": special_uuid,
            "imdb_rating": 9.9,
            "genre": [{"uuid": str(uuid.uuid4()), "name": "Action"}],
            "title": "Unique Movie For Tests",
            "description": "Can be found only by this title",
            "directors_names": ["Test Director"],
            "actors_names": ["Test Actor"],
            "writers_names": ["Test Writer"],
            "actors": [
                {
                    "uuid": str(uuid.uuid4()),
                    "full_name": "Test Actor",
                }
            ],
            "writers": [
                {
                    "uuid": str(uuid.uuid4()),
                    "full_name": "Test Writer",
                }
            ],
            "directors": [
                {
                    "uuid": str(uuid.uuid4()),
                    "full_name": "Test Director",
                }
            ],
        },
    })

    return bulk_query


@pytest_asyncio.fixture(name='es_write_data')
def es_write_data(es_client):
    async def inner(data: list[dict]):

        if await es_client.indices.exists(index=test_settings.es_index):
            await es_client.indices.delete(index=test_settings.es_index)
        await es_client.indices.create(index=test_settings.es_index, **test_settings.es_index_mapping)

        updated, errors = await async_bulk(client=es_client, actions=data)

        await es_client.indices.refresh(index=test_settings.es_index)

        if errors:
            raise Exception('Ошибка записи данных в Elasticsearch')

    return inner


@pytest_asyncio.fixture(name="http_session", scope='session')
async def http_session():
    timeout = aiohttp.ClientTimeout(total=10)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        yield session


@pytest_asyncio.fixture(name='make_get_request')
def make_get_request(http_session):
    async def inner(url: str, query_data):
        url = test_settings.service_url + url

        async with http_session.get(url, params=query_data) as response:
            body = await response.json()
            status = response.status
            return status, body

    return inner


@pytest_asyncio.fixture(name="redis_client")
async def redis_client():
    client = Redis.from_url(test_settings.redis_host)
    yield client
    await client.aclose()


@pytest_asyncio.fixture(name="flushdb", autouse=True)
async def flushdb(redis_client):
    await redis_client.flushdb()
    yield
    await redis_client.flushdb()
