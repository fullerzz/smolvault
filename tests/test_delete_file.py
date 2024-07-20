from typing import Any
from uuid import uuid4

import pytest
from httpx import AsyncClient
from smolvault.models import FileUploadDTO


@pytest.mark.asyncio()
@pytest.mark.usefixtures("_test_bucket")
async def test_delete_file(client: AsyncClient, camera_img: bytes) -> None:
    # first upload the file
    filename = f"{uuid4().hex[:6]}-camera.png"
    expected_obj = FileUploadDTO(name=filename, size=len(camera_img), content=camera_img, tags="camera,photo")
    expected = expected_obj.model_dump(exclude={"content", "upload_timestamp", "tags"})
    response = await client.post(
        "/file/upload", files={"file": (filename, camera_img, "image/png")}, data={"tags": "camera,photo"}
    )
    actual: dict[str, Any] = response.json()
    actual.pop("upload_timestamp")
    assert response.status_code == 201
    assert actual == expected

    # now delete the file
    response = await client.delete(f"/file/{filename}")
    actual = response.json()
    assert response.status_code == 200
    assert actual["message"] == "File deleted successfully"
    assert actual["record"]["file_name"] == filename