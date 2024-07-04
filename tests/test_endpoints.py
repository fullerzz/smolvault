# ruff: noqa: S101
from collections.abc import Sequence
from typing import Any

import pytest
from httpx import AsyncClient
from smolvault.clients.database import DatabaseClient, FileMetadataRecord
from smolvault.main import app
from smolvault.models import FileMetadata, FileUploadDTO


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
    assert response.status_code == 201
    assert actual == expected


@pytest.mark.asyncio()
@pytest.mark.usefixtures("_test_bucket")
async def test_list_files(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    file_metadata_record: FileMetadataRecord,
    file_metadata: FileMetadata,
) -> None:
    def mock_get_all_files(*args: Any, **kwargs: Any) -> Sequence[FileMetadataRecord]:
        return [file_metadata_record]

    monkeypatch.setattr(DatabaseClient, "get_all_metadata", mock_get_all_files)
    response = await client.get("/files/")
    assert response.status_code == 200
    assert response.json() == [file_metadata.model_dump(by_alias=True)]


@pytest.mark.asyncio()
@pytest.mark.usefixtures("_bucket_w_camera_img")
async def test_get_file(
    client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
    file_metadata_record: FileMetadataRecord,
    camera_img: bytes,
) -> None:
    def mock_get_metadata(*args: Any, **kwargs: Any) -> FileMetadataRecord | None:
        return file_metadata_record

    monkeypatch.setattr(DatabaseClient, "get_all_metadata", mock_get_metadata)
    response = await client.get("/file/camera.png")
    assert response.content == camera_img


@pytest.mark.asyncio()
@pytest.mark.usefixtures("_test_bucket")
async def test_get_file_not_found(
    client: AsyncClient,
) -> None:
    response = await client.get("/file/nonexistant-file.png")
    assert response.status_code == 404
    assert response.json() == {"error": "File not found"}
