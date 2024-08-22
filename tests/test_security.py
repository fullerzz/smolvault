from uuid import uuid4

import pytest
from httpx import AsyncClient


@pytest.fixture(scope="module")
async def user_john(client: AsyncClient) -> str:
    """
    Creates a new user 'John' and returns the access token for John.
    """
    user_data = {
        "username": "john",
        "password": "testpassword",
        "email": "john@email.com",
        "full_name": "John Smith",
    }
    response = await client.post(
        "/users/new",
        json=user_data,
    )
    if response.status_code not in {200, 201}:
        raise ValueError(f"Failed to create user: {response.text}")
    # retrieve access token
    response = await client.post(
        "/token",
        data={"username": user_data["username"], "password": user_data["password"]},
    )
    return response.json()["access_token"]


@pytest.fixture(scope="module")
async def user_jane(client: AsyncClient) -> str:
    """
    Creates a new user 'Jane' and returns the access token for Jane.
    """
    user_data = {
        "username": "jane",
        "password": "testpassword",
        "email": "jane@email.com",
        "full_name": "Jane Doe",
    }
    response = await client.post("/users/new", json=user_data)
    if response.status_code not in {200, 201}:
        raise ValueError(f"Failed to create user: {response.text}")
    # retrieve access token
    response = await client.post(
        "/token",
        data={"username": user_data["username"], "password": user_data["password"]},
    )
    return response.json()["access_token"]


@pytest.mark.asyncio
@pytest.mark.usefixtures("_test_bucket")
async def test_get_file(client: AsyncClient, camera_img: bytes, user_john: str, user_jane: str) -> None:
    """
    Test that a user can only download files they have uploaded.
    """
    # upload file as john
    filename = f"{uuid4().hex[:6]}-camera.png"
    await client.post(
        "/file/upload",
        files={"file": (filename, camera_img, "image/png")},
        data={"tags": "camera,photo"},
        headers={"Authorization": f"Bearer {user_john}"},
    )
    # try to download as jane and expect 404
    response = await client.get(
        "/file/original",
        params={"filename": filename},
        headers={"Authorization": f"Bearer {user_jane}"},
    )
    assert response.status_code == 404
    assert response.json() == {"error": "File not found"}
    # download as john and expect success
    response = await client.get(
        "/file/original",
        params={"filename": filename},
        headers={"Authorization": f"Bearer {user_john}"},
    )
    assert response.status_code == 200
    assert response.content == camera_img
