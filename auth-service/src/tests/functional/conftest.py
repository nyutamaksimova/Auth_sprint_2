import uuid

import pytest_asyncio
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import text
from src.core.config import settings
from src.db.postgres import AsyncSessionLocal

BASE_URL = "http://auth-service:8000"


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(base_url=BASE_URL) as client:
        yield client


@pytest_asyncio.fixture
async def auth_client(client: AsyncClient):
    email = f"{uuid.uuid4()}@test.ru"
    password = "12345678"

    response = await client.post(
        "/auth/register",
        json={
            "username": email,
            "password": password,
        },
    )

    assert response.status_code == 201

    response = await client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password,
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    client.headers["Authorization"] = f"Bearer {token}"

    return client


@pytest_asyncio.fixture
async def admin_client(client: AsyncClient):
    response = await client.post(
        "/auth/login",
        data={
            "username": settings.ADMIN_EMAIL,
            "password": settings.ADMIN_PASSWORD,
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    client.headers["Authorization"] = f"Bearer {token}"

    return client


@pytest_asyncio.fixture
async def registered_user(client: AsyncClient):
    email = f"{uuid.uuid4()}@test.ru"
    password = "12345678"

    response = await client.post(
        "/auth/register",
        json={
            "username": email,
            "password": password,
        },
    )

    assert response.status_code == 201
    return response.json()
