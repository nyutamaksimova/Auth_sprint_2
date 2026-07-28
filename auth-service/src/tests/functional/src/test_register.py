from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_register(client):
    email = f"{uuid4()}@mail.ru"
    response = await client.post(
        "/auth/register",
        json={
            "username": email,
            "password": "12345678",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["username"] == email

    assert data["role"] == "USER"


@pytest.mark.asyncio
async def test_register_duplicate(client):
    payload = {
        "username": "user@test.ru",
        "password": "12345678",
    }

    await client.post("/auth/register", json=payload)

    response = await client.post(
        "/auth/register",
        json=payload,
    )

    assert response.status_code == 409
