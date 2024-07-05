import pytest
from httpx import AsyncClient
from smolvault.models import FileMetadata


@pytest.mark.asyncio()
@pytest.mark.usefixtures("_bucket_w_camera_img")
async def test_search_tag_exists(
    client: AsyncClient,
    file_metadata: FileMetadata,
    camera_img: bytes,
) -> None:
    # Upload a file with tags
    await client.post(
        "/file/upload",
        files={"file": ("tagged-camera.png", camera_img, "image/png")},
        data={"tags": "pytest, random, pixels"},
    )
    # Expected metadata
    file_metadata.name = "tagged-camera.png"
    file_metadata.tags = "pytest, random, pixels"
    file_metadata.link = "http://pi.local:1234/file/tagged-camera.png"
    expected = [file_metadata.model_dump(by_alias=True, exclude={"upload_timestamp"})]

    response = await client.get("/files/search", params={"tag": "pytest"})
    actual = response.json()
    actual[0].pop("upload_timestamp")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert actual == expected


@pytest.mark.asyncio()
@pytest.mark.usefixtures("_test_bucket")
async def test_search_tag_not_found(
    client: AsyncClient,
) -> None:
    response = await client.get("/files/search", params={"tag": "fake-tag"})
    assert response.status_code == 200
    assert len(response.json()) == 0
    assert response.json() == []
