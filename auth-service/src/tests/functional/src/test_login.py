import pytest


@pytest.mark.asyncio
async def test_login(client):
    payload = {
        "username": "user@test.ru",
        "password": "12345678",
    }

    await client.post(
        "/auth/register",
        json=payload,
    )

    response = await client.post(
        "/auth/login",
        data=payload,
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data

    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_wrong_password(client):
    await client.post(
        "/auth/register",
        json={
            "username": "user@test.ru",
            "password": "12345678",
        },
    )

    response = await client.post(
        "/auth/login",
        data={
            "username": "user@test.ru",
            "password": "qwerty",
        },
    )

    assert response.status_code == 401
