import pytest


@pytest.mark.asyncio
async def test_logout(client):

    payload = {
        "username": "user@test.ru",
        "password": "12345678",
    }

    await client.post("/auth/register", json=payload)

    login = await client.post(
        "/auth/login",
        data=payload,
    )
    assert login.status_code == 200
    access = login.json()["access_token"]

    response = await client.post(
        "/auth/logout",
        headers={
            "Authorization": f"Bearer {access}"
        },
    )

    assert response.status_code == 200