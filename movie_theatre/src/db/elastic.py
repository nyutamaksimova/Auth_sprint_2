from elasticsearch import AsyncElasticsearch
from fastapi import Request


async def get_elastic(request: Request) -> AsyncElasticsearch:
    return request.app.state.es