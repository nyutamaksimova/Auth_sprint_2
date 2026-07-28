from uuid import uuid4

import pytest


@pytest.mark.asyncio
async def test_assign_role(admin_client, registered_user):
    response = await admin_client.patch(
        f'/roles/users/{registered_user["id"]}/role',
        json={
            "role": "ADMIN",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == registered_user["id"]
    assert body["username"] == registered_user["username"]
    assert body["role"] == "ADMIN"


@pytest.mark.asyncio
async def test_assign_role_forbidden(auth_client, registered_user):
    response = await auth_client.patch(
        f'/roles/users/{registered_user["id"]}/role',
        json={
            "role": "ADMIN",
        },
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_assign_role_user_not_found(admin_client):
    response = await admin_client.patch(
        f"/roles/users/{uuid4()}/role",
        json={
            "role": "ADMIN",
        },
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_assign_role_invalid_role(admin_client, registered_user):
    response = await admin_client.patch(
        f'/roles/users/{registered_user["id"]}/role',
        json={
            "role": "INVALID_ROLE",
        },
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_reset_role(admin_client, registered_user):
    await admin_client.patch(
        f'/roles/users/{registered_user["id"]}/role',
        json={
            "role": "ADMIN",
        },
    )

    response = await admin_client.patch(
        f'/roles/users/{registered_user["id"]}/role/reset',
    )

    assert response.status_code == 200

    body = response.json()

    assert body["role"] == "USER"


@pytest.mark.asyncio
async def test_reset_role_forbidden(auth_client, registered_user):
    response = await auth_client.patch(
        f'/roles/users/{registered_user["id"]}/role/reset',
    )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_reset_role_user_not_found(admin_client):
    response = await admin_client.patch(
        f"/roles/users/{uuid4()}/role/reset",
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_check_permission_granted(admin_client):
    response = await admin_client.get(
        "/roles/permissions/assign_roles",
    )

    assert response.status_code == 200

    body = response.json()

    assert body["permission"] == "assign_roles"
    assert body["granted"] is True


@pytest.mark.asyncio
async def test_check_permission_denied(auth_client):
    response = await auth_client.get(
        "/roles/permissions/assign_roles",
    )

    assert response.status_code == 200

    body = response.json()

    assert body["permission"] == "assign_roles"
    assert body["granted"] is False


@pytest.mark.asyncio
async def test_check_permission_unauthorized(client):
    response = await client.get(
        "/roles/permissions/assign_roles",
    )

    assert response.status_code == 401
