from contextlib import asynccontextmanager

from elasticsearch import AsyncElasticsearch, ConnectionError, ConnectionTimeout
from fastapi import FastAPI, Request, status
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from src.api.v1 import films
from src.core.config import settings
from src.core.exceptions import elastic_exception_handler
from fastapi_limiter import FastAPILimiter

from src.core.rate_limiter import rate_limit_identifier


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = Redis(host=settings.redis_host, port=settings.redis_port)
    app.state.es = AsyncElasticsearch(hosts=[f'http://{settings.elastic_host}:{settings.elastic_port}'])
    await FastAPILimiter.init(app.state.redis, identifier=rate_limit_identifier)

    yield

    await app.state.redis.close()
    await app.state.es.close()


app = FastAPI(
    lifespan=lifespan,
    description="Информация о фильмах",
    version="1.0.0",
    title=settings.project_name,
    docs_url='/api/openapi',
    openapi_url='/api/openapi.json',
    default_response_class=ORJSONResponse,
)

app.include_router(films.router, prefix='/api/v1/films', tags=['films'])

app.add_exception_handler(
    ConnectionError,
    elastic_exception_handler,
)

app.add_exception_handler(
    ConnectionTimeout,
    elastic_exception_handler,
)


@app.middleware('http')
async def before_request(request: Request, call_next):
    response = await call_next(request)
    request_id = request.headers.get('X-Request-Id')
    if not request_id:
        return ORJSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={'detail': 'X-Request-Id is required'})
    return response
