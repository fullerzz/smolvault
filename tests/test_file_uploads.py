from typing import Any
from uuid import uuid4

import pytest
from httpx import AsyncClient

from smolvault.models import FileUploadDTO


@pytest.mark.anyio
@pytest.mark.usefixtures("_test_bucket")
async def test_upload_file(client: AsyncClient, camera_img: bytes, access_token: str) -> None:
    filename = f"{uuid4().hex[:6]}-camera.png"
    expected_obj = FileUploadDTO(
        name=filename,
        size=len(camera_img),
        content=camera_img,
        tags="camera,photo",
        user_id=1,  # FIXME: Need to determine how to get the expected user_id
    )
    expected = expected_obj.model_dump(exclude={"content", "upload_timestamp", "tags", "user_id"})
    response = await client.post(
        "/file/upload",
        files={"file": (filename, camera_img, "image/png")},
        data={"tags": "camera,photo"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    actual: dict[str, Any] = response.json()
    actual.pop("upload_timestamp")
    actual.pop("user_id")
    assert response.status_code == 201
    assert actual == expected


@pytest.mark.anyio
@pytest.mark.usefixtures("_test_bucket")
async def test_upload_file_no_tags(client: AsyncClient, camera_img: bytes, access_token: str) -> None:
    filename = f"{uuid4().hex[:6]}-camera.png"

    # FIXME: Need to determine how to get the expected user_id
    expected_obj = FileUploadDTO(name=filename, size=len(camera_img), content=camera_img, tags=None, user_id=1)
    expected = expected_obj.model_dump(exclude={"content", "upload_timestamp", "tags", "user_id"})

    response = await client.post(
        "/file/upload",
        files={"file": (filename, camera_img, "image/png")},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 201
    actual: dict[str, Any] = response.json()
    actual.pop("upload_timestamp")
    actual.pop("user_id")
    assert actual == expected
