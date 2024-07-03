# ruff: noqa: S101
from typing import Any

import pytest
from httpx import AsyncClient
from smolvault.main import app
from smolvault.models import FileUploadDTO


@pytest.fixture(scope="module")
def client() -> AsyncClient:
    return AsyncClient(app=app, base_url="http://testserver")


@pytest.mark.asyncio()
async def test_read_root(client: AsyncClient) -> None:
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


@pytest.mark.asyncio()
@pytest.mark.usefixtures("_test_bucket")
async def test_upload_file(client: AsyncClient, camera_img: bytes) -> None:
    expected_obj = FileUploadDTO(name="camera.png", size=len(camera_img), content=camera_img)
    expected = expected_obj.model_dump(exclude={"content", "upload_timestamp"})
    response = await client.post("/file/upload/", files={"file": ("camera.png", camera_img, "image/png")})
    actual: dict[str, Any] = response.json()
    actual.pop("upload_timestamp")
    assert response.status_code == 200
    assert actual == expected
