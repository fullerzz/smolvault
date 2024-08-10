from collections.abc import Sequence
from typing import Any
from uuid import uuid4

import pytest
from httpx import AsyncClient
from smolvault.clients.database import DatabaseClient, FileMetadataRecord
from smolvault.models import FileMetadata


@pytest.mark.asyncio()
async def test_read_root(client: AsyncClient, access_token: str) -> None:
    response = await client.get("/", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert response.json() == {"email": "test@email.com", "full_name": "John Smith", "username": "testuser"}


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
    response = await client.get("/files")
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
    filename = f"{uuid4().hex[:6]}-camera.png"
    await client.post(
        "/file/upload", files={"file": (filename, camera_img, "image/png")}, data={"tags": "camera,photo"}
    )
    response = await client.get("/file/original", params={"filename": filename})
    assert response.status_code == 200
    assert response.content == camera_img


@pytest.mark.asyncio()
@pytest.mark.usefixtures("_test_bucket")
async def test_get_file_not_found(
    client: AsyncClient,
) -> None:
    response = await client.get("/file/original", params={"filename": "nonexistant-file.png"})
    assert response.status_code == 404
    assert response.json() == {"error": "File not found"}
