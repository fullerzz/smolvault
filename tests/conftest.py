import pytest
from fastapi.testclient import TestClient

from smolvault.clients.database import DatabaseClient
from smolvault.main import app

@pytest.fixture(scope="session")
def env_vars() -> dict[str, str]:
    return {
        "SMOLVAULT_DB": "test.db",
        "SMOLVAULT_BUCKET": "test-bucket",
    }


@pytest.fixture()
def test_client() -> TestClient:
    return TestClient(app)

@pytest.fixture(scope="session")
def camera_img() -> bytes:
    with open("tests/mock_data/camera.png", "rb") as f:
        return f.read()


@pytest.fixture(scope="module")
def db() -> DatabaseClient:
    return DatabaseClient(db_filename="test.db")
