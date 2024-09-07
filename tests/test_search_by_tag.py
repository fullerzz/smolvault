import pytest
from httpx import AsyncClient

from smolvault.models import FileMetadata


@pytest.mark.anyio
@pytest.mark.usefixtures("_bucket_w_camera_img")
async def test_search_tag_exists(
    client: AsyncClient,
    file_metadata: FileMetadata,
    camera_img: bytes,
    access_token: str,
) -> None:
    # Upload a file with tags
    await client.post(
        "/file/upload",
        files={"file": ("tagged-camera.png", camera_img, "image/png")},
        data={"tags": "pytest, random, pixels"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    # Expected metadata
    file_metadata.name = "tagged-camera.png"
    file_metadata.tags = "pytest, random, pixels"
    file_metadata.link = "http://pi.local:8000/file/original?filename=tagged-camera.png"
    expected = [file_metadata.model_dump(by_alias=True, exclude={"upload_timestamp"})]

    response = await client.get(
        "/files/search",
        params={"tag": "pytest"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    actual = response.json()
    actual[0].pop("upload_timestamp")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert actual == expected


@pytest.mark.anyio
@pytest.mark.usefixtures("_test_bucket")
async def test_search_tag_not_found(client: AsyncClient, access_token: str) -> None:
    response = await client.get(
        "/files/search",
        params={"tag": "fake-tag"},
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert len(response.json()) == 0
    assert response.json() == []
