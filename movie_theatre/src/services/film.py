import json
from abc import ABC, abstractmethod
from uuid import UUID

from elasticsearch import AsyncElasticsearch
from elasticsearch import NotFoundError
from fastapi import HTTPException, Depends
from redis.asyncio import Redis

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.film import Film


class FilmRepository(ABC):

    @abstractmethod
    async def get_by_id(self, film_id: UUID) -> Film | None:
        pass

    @abstractmethod
    async def get_list(self, sort: str, page_size: int, page_number: int, ) -> list[Film]:
        pass

    @abstractmethod
    async def search(self, query: str, page_size: int, page_number: int, ) -> list[Film]:
        pass

    @abstractmethod
    async def get_similar(self, film_id: UUID, page_size: int, page_number: int, ) -> list[Film] | None:
        pass


class CacheRepository(ABC):

    @abstractmethod
    async def get(self, key: str):
        pass

    @abstractmethod
    async def set(self, key: str, value, expire: int, ):
        pass


ALLOWED_SORT_FIELDS = {
    'imdb_rating',
}


class InvalidSortFieldError(ValueError):
    pass


class ElasticFilmRepository(FilmRepository):
    INDEX = "movies"

    def __init__(self, elastic: AsyncElasticsearch, ):
        self._elastic = elastic

    async def get_by_id(self, film_id, ) -> Film | None:

        try:
            doc = await self._elastic.get(
                index=self.INDEX,
                id=str(film_id),
            )
        except NotFoundError:
            return None

        return Film.model_validate(
            doc["_source"],
        )

    async def get_list(self, sort: str, page_size: int, page_number: int, ) -> list[Film]:

        sort_field = sort.removeprefix("-")

        if sort_field not in ALLOWED_SORT_FIELDS:
            raise InvalidSortFieldError(sort_field)

        sort_order = (
            "desc"
            if sort.startswith("-")
            else "asc"
        )

        response = await self._elastic.search(
            index=self.INDEX,
            sort=[{sort_field: {'order': sort_order}}],
            from_=(page_number - 1) * page_size,
            size=page_size,
        )

        return [
            Film.model_validate(hit["_source"])
            for hit in response["hits"]["hits"]
        ]

    async def search(self, query: str, page_size: int, page_number: int) -> list[Film]:

        query = {
            "multi_match": {
                "query": query,
                "fields": [
                    "title^3",
                    "description",
                    "actors_names",
                    "writers_names",
                    "directors_names",
                ],
                "fuzziness": "auto"
            }
        }

        response = await self._elastic.search(index=self.INDEX,
                                              query=query,
                                              from_=(page_number - 1) * page_size,
                                              size=page_size)

        return [Film.model_validate(hit["_source"]) for hit in response["hits"]["hits"]]

    async def get_similar(self, film_id: UUID, page_size: int, page_number: int) -> list[Film] | None:

        film = await self.get_by_id(film_id)
        if not film:
            return None

        genre_ids = [g.uuid for g in film.genre]
        query = {
            "bool": {
                "must": [
                    {
                        "nested": {
                            "path": "genre",
                            "query": {
                                "terms": {
                                    "genre.uuid": genre_ids
                                }
                            }
                        }
                    }
                ],
                "must_not": [
                    {"term": {"uuid": str(film_id)}}
                ]
            }
        }

        response = await self._elastic.search(index=self.INDEX,
                                              query=query,
                                              from_=(page_number - 1) * page_size,
                                              size=page_size,
                                              sort=[{"imdb_rating": {"order": "desc"}}])

        return [Film.model_validate(hit["_source"]) for hit in response["hits"]["hits"]]


class RedisCacheRepository(CacheRepository):

    def __init__(self, redis: Redis, ):
        self._redis = redis

    async def get(self, key: str):
        data = await self._redis.get(key)

        if data is None:
            return None

        return json.loads(data)

    async def set(self, key: str, value, expire: int, ):
        await self._redis.set(key, json.dumps(value), ex=expire, )


class FilmService:
    CACHE_TTL = 300

    def __init__(self, film_repository: FilmRepository, cache_repository: CacheRepository, ):
        self._films = film_repository
        self._cache = cache_repository

    async def get_by_id(self, film_id: UUID, ) -> Film | None:

        cache_key = f"film:{film_id}"

        cached = await self._cache.get(cache_key)

        if cached:
            return Film.model_validate(cached)

        film = await self._films.get_by_id(film_id)

        if film is None:
            return None

        await self._cache.set(
            cache_key,
            film.model_dump(),
            self.CACHE_TTL,
        )

        return film

    async def get_list(self, sort: str, page_size: int, page_number: int) -> list[Film]:

        cache_key = f"films:list:{sort}:{page_size}:{page_number}"

        cached = await self._cache.get(cache_key)
        if cached:
            return [Film.model_validate(item) for item in cached]

        films = await self._films.get_list(sort, page_size, page_number)

        await self._cache.set(
            cache_key,
            [film.model_dump(mode="json") for film in films],
            self.CACHE_TTL,
        )

        return films

    async def search(self, query: str, page_size: int, page_number: int) -> list[Film]:
        cache_key = f"films:search:{query}:{page_size}:{page_number}"

        cached = await self._cache.get(cache_key)

        if cached:
            return [Film.model_validate(item) for item in cached]

        films = await self._films.search(query, page_size, page_number)

        await self._cache.set(
            cache_key,
            [film.model_dump(mode="json") for film in films],
            self.CACHE_TTL,
        )

        return films

    async def get_similar(self, film_id: UUID, page_size: int, page_number: int) -> list[Film] | None:
        cache_key = f"films:similar:{film_id}:{page_size}:{page_number}"

        cached = await self._cache.get(cache_key)
        if cached:
            return [Film.model_validate(item) for item in cached]

        films = await self._films.get_similar(film_id, page_size, page_number)

        if films is None:
            return None

        await self._cache.set(
            cache_key,
            [film.model_dump(mode="json") for film in films],
            self.CACHE_TTL,
        )

        return films

def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    film_repository = ElasticFilmRepository(
        elastic,
    )

    cache_repository = RedisCacheRepository(
        redis,
    )

    return FilmService(
        film_repository=film_repository,
        cache_repository=cache_repository,
    )
