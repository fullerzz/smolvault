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


@pytest.fixture(scope="module")
async def user_jack(client: AsyncClient) -> str:
    """
    Creates a new user 'Jack' and returns the access token for Jack.
    """
    user_data = {
        "username": "jack",
        "password": "testpassword",
        "email": "jack@email.com",
        "full_name": "jack Smith",
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


@pytest.fixture
async def _fully_populated_user_bucket(
    client: AsyncClient, camera_img: bytes, user_jack: str, _test_bucket: None
) -> None:
    img_size = len(camera_img)
    bytes_uploaded = 0
    filenames: list[str] = []
    while bytes_uploaded < 50000:
        # upload file as john
        filename = f"{uuid4().hex[:6]}-camera.png"
        filenames.append(filename)
        await client.post(
            "/file/upload",
            files={"file": (filename, camera_img, "image/png")},
            data={"tags": "camera,photo"},
            headers={"Authorization": f"Bearer {user_jack}"},
        )
        bytes_uploaded += img_size


@pytest.mark.asyncio
@pytest.mark.usefixtures("_fully_populated_user_bucket")
async def test_user_over_daily_upload_limit(client: AsyncClient, camera_img: bytes, user_jack: str) -> None:
    """
    Test that a user is blocked from uploading files if they exceed the daily upload limit.
    """
    # upload file as john that will exceed the daily limit
    filename = f"{uuid4().hex[:6]}-camera.png"
    response = await client.post(
        "/file/upload",
        files={"file": (filename, camera_img, "image/png")},
        data={"tags": "camera,photo"},
        headers={"Authorization": f"Bearer {user_jack}"},
    )
    assert response.status_code == 400
    assert response.json() == {"error": "Upload limit exceeded"}
