import pytest


@pytest.mark.asyncio
async def test_me(client):

    payload = {
        "username": "user@test.ru",
        "password": "12345678",
    }

    await client.post("/auth/register", json=payload)

    login = await client.post(
        "/auth/login",
        data=payload,
    )

    token = login.json()["access_token"]

    response = await client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        },
    )

    assert response.status_code == 200

    assert response.json()["username"] == payload["username"]
