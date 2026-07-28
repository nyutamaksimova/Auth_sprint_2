import pytest


@pytest.mark.asyncio
async def test_refresh(client):
    payload = {
        "username": "user@test.ru",
        "password": "12345678",
    }

    await client.post("/auth/register", json=payload)

    login = await client.post(
        "/auth/login",
        data=payload,
    )

    refresh = login.json()["refresh_token"]

    response = await client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh,
        },
    )

    assert response.status_code == 200

    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_old_refresh_revoked(client):
    payload = {
        "username": "user@test.ru",
        "password": "12345678",
    }

    await client.post("/auth/register", json=payload)

    login = await client.post(
        "/auth/login",
        data=payload,
    )

    refresh = login.json()["refresh_token"]

    await client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh,
        },
    )

    response = await client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh,
        },
    )

    assert response.status_code == 401
