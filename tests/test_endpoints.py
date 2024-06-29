import pytest
from httpx import AsyncClient

from smolvault.main import app


@pytest.fixture(scope="module")
def client() -> AsyncClient:
    return AsyncClient(app=app, base_url="http://testserver")

@pytest.mark.asyncio
async def test_read_root(client: AsyncClient) -> None:
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"Hello": "World"}


@pytest.mark.asyncio
async def test_upload_file(client: AsyncClient) -> None:
    response = await client.post("/file/upload/")
    assert response.status_code == 422
    assert response.json() == {"detail": [{"loc": ["body", "file"], "msg": "field required", "type": "value_error"}]}