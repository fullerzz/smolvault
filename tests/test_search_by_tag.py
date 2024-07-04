import pytest
from httpx import AsyncClient
from smolvault.models import FileMetadata


@pytest.mark.asyncio()
@pytest.mark.usefixtures("_bucket_w_camera_img")
async def test_search_tag_exists(
    client: AsyncClient,
    file_metadata: FileMetadata,
) -> None:
    response = await client.get("/files/search", params={"tag": "camera"})
    assert response.status_code == 200
    assert len(response.json()) == 1

    expected = [file_metadata.model_dump(by_alias=True, exclude={"upload_timestamp"})]
    actual = response.json()
    actual[0].pop("upload_timestamp")
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